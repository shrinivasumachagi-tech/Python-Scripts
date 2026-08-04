from __future__ import annotations

import re
from typing import Any

from utils import LoggerFactory, make_result


class MACAddressModule:
    """Handles MAC programming and verification."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("MACAddressModule")

    def write_mac(self, mac: str) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("mac", {}).get("write", f"test ibcn_production set_mac {mac}"))
        return make_result("PASS", "MAC write command issued", {"mac": mac})

    def read_mac(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("mac", {}).get("read", "test ibcn_production fpga_io 1"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        match = re.search(r"([0-9A-Fa-f:]{11,})", text)
        return make_result("PASS", "MAC read", {"mac": match.group(1) if match else text})

    def verify_mac(self, mac: str) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("mac", {}).get("verify", "test ibcn_production fpga_io 1"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        if mac and mac.lower() in text.lower():
            return make_result("PASS", "MAC verified", {"mac": mac, "response": text})
        return make_result("FAIL", "MAC mismatch", {"mac": mac, "response": text})

    def run(self, mac: str | None = None) -> dict[str, Any]:
        target_mac = mac or self.config.get("default_mac", "00:11:22:33:44:55")
        self.write_mac(target_mac)
        read_result = self.read_mac()
        verify_result = self.verify_mac(target_mac)
        if verify_result["status"] == "PASS":
            return make_result("PASS", "MAC workflow completed", {"mac": target_mac, "read": read_result["data"]})
        return make_result("FAIL", "MAC workflow failed", {"mac": target_mac, "read": read_result["data"], "verify": verify_result["data"]})
