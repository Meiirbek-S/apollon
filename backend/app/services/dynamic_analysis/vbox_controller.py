import shlex
import subprocess
from dataclasses import dataclass


class VBoxCommandError(RuntimeError):
    pass


@dataclass(slots=True)
class VBoxController:
    vm_name: str
    snapshot_name: str
    timeout_seconds: int = 120

    def _run(self, args: list[str]) -> str:
        command = ["VBoxManage", *args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout_seconds, check=False)
        if result.returncode != 0:
            raise VBoxCommandError(
                f"VBox command failed: {shlex.join(command)}\nstdout={result.stdout}\nstderr={result.stderr}"
            )
        return result.stdout.strip()

    def check_vm(self) -> str:
        return self._run(["showvminfo", self.vm_name, "--machinereadable"])

    def restore_snapshot(self) -> str:
        return self._run(["snapshot", self.vm_name, "restore", self.snapshot_name])

    def start(self) -> str:
        return self._run(["startvm", self.vm_name, "--type", "headless"])

    def guest_run(self, username: str, password: str, exe: str, arguments: list[str]) -> str:
        return self._run(
            [
                "guestcontrol",
                self.vm_name,
                "run",
                "--username",
                username,
                "--password",
                password,
                "--exe",
                exe,
                "--",
                exe,
                *arguments,
            ]
        )

    def poweroff(self) -> str:
        return self._run(["controlvm", self.vm_name, "poweroff"])

    def safe_cleanup(self) -> None:
        try:
            self.poweroff()
        except VBoxCommandError:
            pass
        self.restore_snapshot()
