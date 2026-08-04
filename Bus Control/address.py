from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class AddressModule:
    """Reads and validates FPGA address values."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("AddressModule")

    def read_address(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("address", {}).get("read", "fpga_io 7"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS", "Address read", {"address": text})

    def verify(self, address: str) -> dict[str, Any]:
        expected = self.config.get("expected_address", ["0x55", "0xAA"])
        if address in expected:
            return make_result("PASS", "Address verified", {"address": address})
        return make_result("FAIL", "Address mismatch", {"address": address, "expected": expected})

    def run(self) -> dict[str, Any]:
        read_result = self.read_address()
        address = read_result.get("data", {}).get("address", "")
        verify_result = self.verify(address)
        return make_result(verify_result["status"], verify_result["message"], {"address": address, "verification": verify_result["data"]})
