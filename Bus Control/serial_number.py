from __future__ import annotations

import re
from typing import Any

from utils import LoggerFactory, make_result


class SerialNumberModule:
    """Handles serial number programming, reading, and verification."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("SerialNumberModule")

    def write_serial(self, serial: str) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("serial", {}).get("write", f"test ibcn_production set_serial {serial}"))
        return make_result("PASS", "Serial number write command issued", {"serial": serial})

    def read_serial(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("serial", {}).get("read", "test ibcn_production fpga_io 2"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        match = re.search(r"serial[:\s]+([A-Za-z0-9]+)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"([A-Za-z0-9]{4,})", text)
        serial = match.group(1) if match else ""
        return make_result("PASS", "Serial number read", {"serial": serial})

    def verify_serial(self, serial: str) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("serial", {}).get("verify", "test ibcn_production fpga_io 2"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        if serial and serial in text:
            return make_result("PASS", "Serial number verified", {"serial": serial, "response": text})
        return make_result("FAIL", "Serial number mismatch", {"serial": serial, "response": text})

    def run(self, serial: str | None = None) -> dict[str, Any]:
        target_serial = serial or self.config.get("default_serial", "12345678")
        self.write_serial(target_serial)
        read_result = self.read_serial()
        verify_result = self.verify_serial(target_serial)
        if verify_result["status"] == "PASS":
            return make_result("PASS", "Serial number workflow completed", {"serial": target_serial, "read": read_result["data"]})
        return make_result("FAIL", "Serial number workflow failed", {"serial": target_serial, "read": read_result["data"], "verify": verify_result["data"]})
