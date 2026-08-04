from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class HardwareVersionModule:
    """Handles hardware revision programming and verification."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("HardwareVersionModule")

    def write_hw_revision(self, revision: str) -> dict[str, Any]:
        command = self.commands.get("hardware_version", {}).get("write", f"set_hw_rev {revision}")
        self.communication.send_command(command)
        return make_result("PASS", "Hardware revision write command issued", {"revision": revision})

    def read_hw_revision(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("hardware_version", {}).get("read", "fpga_io 14"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS", "Hardware revision read", {"revision": text})

    def verify(self, revision: str) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("hardware_version", {}).get("verify", "fpga_io 14"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        if revision in text:
            return make_result("PASS", "Hardware revision verified", {"revision": revision, "response": text})
        return make_result("FAIL", "Hardware revision mismatch", {"revision": revision, "response": text})

    def run(self, revision: str | None = None) -> dict[str, Any]:
        target_revision = revision or self.config.get("default_hw_revision", "A1")
        self.write_hw_revision(target_revision)
        read_result = self.read_hw_revision()
        verify_result = self.verify(target_revision)
        if verify_result["status"] == "PASS":
            return make_result("PASS", "Hardware revision workflow completed", {"revision": target_revision, "read": read_result["data"]})
        return make_result("FAIL", "Hardware revision workflow failed", {"revision": target_revision, "read": read_result["data"], "verify": verify_result["data"]})
