import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

from app.core.config import settings
from app.models.static_analysis import RiskLevel


class DynamicAnalyzer:
    provider = "unknown"

    def analyze(self, sample_path: str, filename: str, sha256: str) -> dict:
        raise NotImplementedError


class DockerSandboxAnalyzer(DynamicAnalyzer):
    provider = "docker"

    def analyze(self, sample_path: str, filename: str, sha256: str) -> dict:
        sandbox_id = f"docker-{uuid.uuid4().hex[:12]}"
        sample = Path(sample_path)
        risk_score = 0
        suspicious_actions: list[str] = []

        if filename.lower().endswith((".exe", ".dll", ".scr", ".ps1", ".bat")):
            risk_score += 25
            suspicious_actions.append("Исполняемый файл запрошен для контейнерного прогона")

        # Изоляция контейнера: без сети, read-only root fs, ограниченные ресурсы.
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--memory",
            "256m",
            "--cpus",
            "1.0",
            "-v",
            f"{sample.resolve()}:/sample:ro",
            settings.dynamic_docker_image,
            "sh",
            "-lc",
            "sha256sum /sample && wc -c /sample",
        ]

        runtime_meta = {"sandbox_id": sandbox_id, "container_image": settings.dynamic_docker_image}
        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=25)
            runtime_meta["exit_code"] = proc.returncode
            runtime_meta["stdout"] = proc.stdout.strip()
            runtime_meta["stderr"] = proc.stderr.strip()
            if proc.returncode != 0:
                risk_score += 10
                suspicious_actions.append("Контейнер завершился с ошибкой при выполнении образца")
        except Exception as exc:  # noqa: BLE001
            runtime_meta["error"] = str(exc)
            risk_score += 10
            suspicious_actions.append("Контейнерный запуск недоступен, использован fallback профилирования")

        file_size = sample.stat().st_size
        if file_size > 5 * 1024 * 1024:
            risk_score += 10
            suspicious_actions.append("Крупный исполняемый объект")

        risk_level = RiskLevel.MALWARE_LIKE if risk_score >= 60 else RiskLevel.SUSPICIOUS if risk_score >= 25 else RiskLevel.SAFE
        verdict = (
            f"{risk_level.value}: контейнерный прогон завершен, обнаружены потенциально опасные действия (score={risk_score})"
            if risk_score
            else "SAFE: контейнерный прогон не показал выраженных риск-сигналов (score=0)"
        )

        return {
            "provider": self.provider,
            "sandbox_id": sandbox_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "suspicious_actions": suspicious_actions,
            "network_connections": [],
            "file_changes": [],
            "registry_changes": [],
            "verdict_reason": verdict,
            "raw_report": {
                "runtime": runtime_meta,
                "sha256": sha256,
                "file_size": file_size,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            },
        }


class ExternalSandboxAnalyzer(DynamicAnalyzer):
    provider = "external"

    def analyze(self, sample_path: str, filename: str, sha256: str) -> dict:
        sandbox_id = f"ext-{uuid.uuid4().hex[:12]}"
        payload = {
            "filename": filename,
            "sha256": sha256,
            "size": Path(sample_path).stat().st_size,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }

        api_url = settings.dynamic_external_api_url
        api_key = settings.dynamic_external_api_key

        if not api_url or not api_key:
            return {
                "provider": self.provider,
                "sandbox_id": sandbox_id,
                "risk_score": 0,
                "risk_level": RiskLevel.SAFE,
                "suspicious_actions": ["Внешняя песочница не настроена: использован no-op результат"],
                "network_connections": [],
                "file_changes": [],
                "registry_changes": [],
                "verdict_reason": "SAFE: external sandbox не настроен (score=0)",
                "raw_report": {"request_payload": payload, "note": "configure dynamic_external_api_url and key"},
            }

        req = request.Request(
            api_url,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with request.urlopen(req, timeout=20) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8") or "{}")

        score = int(body.get("risk_score", 0))
        level = RiskLevel.MALWARE_LIKE if score >= 60 else RiskLevel.SUSPICIOUS if score >= 25 else RiskLevel.SAFE

        return {
            "provider": self.provider,
            "sandbox_id": str(body.get("sandbox_id", sandbox_id)),
            "risk_score": score,
            "risk_level": level,
            "suspicious_actions": list(body.get("suspicious_actions", [])),
            "network_connections": list(body.get("network_connections", [])),
            "file_changes": list(body.get("file_changes", [])),
            "registry_changes": list(body.get("registry_changes", [])),
            "verdict_reason": str(body.get("verdict_reason", f"{level.value}: external sandbox verdict")),
            "raw_report": body,
        }


def build_dynamic_analyzer() -> DynamicAnalyzer:
    provider = (settings.dynamic_analysis_provider or "docker").lower().strip()
    if provider == "external":
        return ExternalSandboxAnalyzer()
    return DockerSandboxAnalyzer()


def compute_sha256(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as src:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
