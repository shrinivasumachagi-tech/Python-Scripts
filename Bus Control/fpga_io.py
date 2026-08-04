from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class FPGAIOModule:
    """Performs FPGA I/O related checks and tests."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("FPGAIOModule")

    def get_vhdl_version(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("vhdl", "fpga_io 9"))
        response = self.communication.read_response()
        return make_result("PASS", "VHDL version read", {"response": response.get("data", {}).get("response", "")})

    def get_nios_version(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("nios", "fpga_io 10"))
        response = self.communication.read_response()
        return make_result("PASS", "NIOS version read", {"response": response.get("data", {}).get("response", "")})

    def get_wdmcu_version(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("wdmcu", "fpga_io 11"))
        response = self.communication.read_response()
        return make_result("PASS", "WDMCU version read", {"response": response.get("data", {}).get("response", "")})

    def signal_test(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("signal_test", "fpga_io 12"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS" if "PASS" in text else "FAIL", "Signal test completed", {"response": text})

    def clock_sync(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("clock_sync", "clksync"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS" if "PASS" in text else "FAIL", "Clock sync completed", {"response": text})

    def io_loop(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("fpga_io", {}).get("io_loop", "io_loop"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS" if "PASS" in text else "FAIL", "IO loop completed", {"response": text})

    def run(self) -> dict[str, Any]:
        results = [self.get_vhdl_version(), self.get_nios_version(), self.get_wdmcu_version(), self.signal_test(), self.clock_sync(), self.io_loop()]
        status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
        return make_result(status, "FPGA I/O workflow completed", {"checks": results})
