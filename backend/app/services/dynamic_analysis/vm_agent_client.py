from dataclasses import dataclass

from app.services.dynamic_analysis.vbox_controller import VBoxController


@dataclass(slots=True)
class VMAgentClient:
    controller: VBoxController
    guest_user: str
    guest_password: str

    def run_sample(self, sample_guest_path: str) -> str:
        return self.controller.guest_run(
            username=self.guest_user,
            password=self.guest_password,
            exe=r"C:\\agent\\run_analysis.bat",
            arguments=[sample_guest_path],
        )
