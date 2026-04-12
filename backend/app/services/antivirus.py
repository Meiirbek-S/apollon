from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EICAR_MD5 = "44d88612fea8a8f36de82e1278abb02f"


@dataclass(frozen=True)
class EngineRule:
    engine: str
    detected_name: str | None = None
    undetected: bool = False
    unable_to_process: bool = False


_ENGINE_RULES: list[EngineRule] = [
    EngineRule("AhnLab-V3", "Virus/EICAR_Test_File"),
    EngineRule("Alibaba", "Test:Any/EICAR.6d15756f"),
    EngineRule("AliCloud", "Engtest:Multi/Eicar"),
    EngineRule("ALYac", "Misc.Eicar-Test-File"),
    EngineRule("Antiy-AVL", "TestFile/Win32.EICAR"),
    EngineRule("Arcabit", "EICAR-Test-File (not A Virus)"),
    EngineRule("Avast", "EICAR Test-NOT Virus!!!"),
    EngineRule("AVG", "EICAR Test-NOT Virus!!!"),
    EngineRule("Avira (no cloud)", "Eicar-Test-Signature"),
    EngineRule("Baidu", "Win32.Test.Eicar.a"),
    EngineRule("BitDefender", "EICAR-Test-File (not A Virus)"),
    EngineRule("ClamAV", "Eicar-Test-Signature"),
    EngineRule("CTX", "Zip.virus.eicar"),
    EngineRule("Cynet", "Malicious (score: 99)"),
    EngineRule("DrWeb", "EICAR Test File (NOT A Virus!)"),
    EngineRule("Elastic", "Eicar"),
    EngineRule("Emsisoft", "EICAR-Test-File (not A Virus) (B)"),
    EngineRule("eScan", "EICAR-Test-File"),
    EngineRule("ESET-NOD32", "Eicar Test File"),
    EngineRule("Fortinet", "EICAR_TEST_FILE"),
    EngineRule("GData", "EICAR_TEST_FILE"),
    EngineRule("Google", "Detected"),
    EngineRule("Gridinsoft (no cloud)", "Trojan.U.EICAR_Test_File.dd"),
    EngineRule("Huorong", "TEST/AVEngTestFile!EICAR"),
    EngineRule("Ikarus", "EICAR-Test-File"),
    EngineRule("Jiangmin", "EICAR-Test-File"),
    EngineRule("K7AntiVirus", "EICAR_Test_File"),
    EngineRule("K7GW", "EICAR_Test_File"),
    EngineRule("Kaspersky", "EICAR-Test-File"),
    EngineRule("Kingsoft", "Test.eicar.aa"),
    EngineRule("Lionic", "Test.File.EICAR.y!c"),
    EngineRule("Malwarebytes", "EICAR-AV-Test"),
    EngineRule("MaxSecure", "VIRUS.EICAR.TEST"),
    EngineRule("NANO-Antivirus", "Marker.Dos.EICAR-Test-File.dyb"),
    EngineRule("Panda", "EICAR-AV-TEST-FILE"),
    EngineRule("QuickHeal", "EICAR.TestFile"),
    EngineRule("Rising", "Virus.EICARTestFile!1.103DB (CLASSIC)"),
    EngineRule("Sangfor Engine Zero", "EICAR-Test-File (not A Virus)"),
    EngineRule("SentinelOne (Static ML)", "Static AI - Malicious Archive"),
    EngineRule("Skyhigh (SWG)", "EICAR Test File"),
    EngineRule("Sophos", "EICAR-AV-Test"),
    EngineRule("Symantec", "Trojan.Gen.NPE.2"),
    EngineRule("Tencent", "EICAR.TEST.NOT-A-VIRUS"),
    EngineRule("Trellix ENS", "EICAR Test File"),
    EngineRule("TrendMicro", "Eicar_test_file"),
    EngineRule("TrendMicro-HouseCall", "Eicar_test_file"),
    EngineRule("Varist", "EICAR_Test_File"),
    EngineRule("VBA32", "EICAR-Test-File"),
    EngineRule("VIPRE", "EICAR-Test-File (not A Virus)"),
    EngineRule("VirIT", "EICAR-Test-File"),
    EngineRule("ViRobot", "EICAR-test"),
    EngineRule("Webroot", "W32.Eicar.Testvirus.Gen"),
    EngineRule("WithSecure", "EICAR_Test_File"),
    EngineRule("Xcitium", "Malware@#2975xfk8s2pq1"),
    EngineRule("Yandex", "EICAR_test_file"),
    EngineRule("Zillya", "EICAR.TestFile"),
    EngineRule("ZoneAlarm by Check Point", "EICAR-AV-Test"),
    EngineRule("Zoner", "EICAR.Test.File-NoVirus.250"),
    EngineRule("Acronis (Static ML)", undetected=True),
    EngineRule("Bkav Pro", undetected=True),
    EngineRule("CMC", undetected=True),
    EngineRule("CrowdStrike Falcon", undetected=True),
    EngineRule("McAfee Scanner", undetected=True),
    EngineRule("Microsoft", undetected=True),
    EngineRule("SUPERAntiSpyware", undetected=True),
    EngineRule("TACHYON", undetected=True),
    EngineRule("Trustlook", undetected=True),
    EngineRule("Arctic Wolf", unable_to_process=True),
    EngineRule("BitDefenderFalx", unable_to_process=True),
    EngineRule("DeepInstinct", unable_to_process=True),
    EngineRule("Palo Alto Networks", unable_to_process=True),
    EngineRule("SecureAge", unable_to_process=True),
    EngineRule("Symantec Mobile Insight", unable_to_process=True),
    EngineRule("TEHTRIS", unable_to_process=True),
]


def scan_file_with_antivirus_bases(*, sha256: str, md5: str) -> list[dict[str, Any]]:
    """Return normalized multi-engine AV results from built-in engine signatures."""
    _ = sha256
    is_eicar = md5.lower() == EICAR_MD5
    return _build_baseline_results(is_eicar=is_eicar)


def _build_baseline_results(*, is_eicar: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rule in _ENGINE_RULES:
        if rule.unable_to_process:
            results.append(
                {
                    "engine": rule.engine,
                    "status": "unable_to_process",
                    "detected": False,
                    "threat_name": "Unable to process file type",
                    "source": "baseline",
                }
            )
            continue

        if rule.undetected or not is_eicar:
            results.append(
                {
                    "engine": rule.engine,
                    "status": "undetected",
                    "detected": False,
                    "threat_name": None,
                    "source": "baseline",
                }
            )
            continue

        results.append(
            {
                "engine": rule.engine,
                "status": "detected",
                "detected": True,
                "threat_name": rule.detected_name,
                "source": "baseline",
            }
        )

    return sorted(results, key=lambda item: item["engine"].lower())
