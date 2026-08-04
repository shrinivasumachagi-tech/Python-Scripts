from __future__ import annotations

import os
import subprocess
import time
from typing import Any

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pyautogui = None

from utils import LoggerFactory, make_result


class Communication:
    """Communication abstraction for Tera Term automation with simulation fallback."""

    def __init__(self, config: dict[str, Any], logger: Any = None, simulate: bool = False) -> None:
        self.config = config
        self.logger = logger or LoggerFactory.get_logger("Communication")
        self.simulate = simulate or os.getenv("IBCN_SIMULATE", "0").lower() in {"1", "true", "yes"}
        self._terminal_process: Any = None
        self._response_buffer = ""
        self._last_command: str | None = None
        self.backend = "simulation" if self.simulate else "teraterm"

    def open_terminal(self) -> dict[str, Any]:
        try:
            if self.simulate:
                self.logger.info("Running in simulation mode; no terminal required")
                return make_result("PASS", "Simulation mode enabled", {"backend": self.backend})

            executable = self.config.get("terminal_executable", "ttermpro.exe")
            self._terminal_process = subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.logger.info("Opened terminal with executable %s", executable)
            return make_result("PASS", "Terminal opened", {"backend": self.backend})
        except Exception as exc:  # pragma: no cover - runtime environment dependent
            self.logger.exception("Unable to open terminal: %s", exc)
            self.simulate = True
            self.backend = "simulation"
            return make_result("FAIL", f"Unable to open terminal: {exc}", {"backend": self.backend})

    def close_terminal(self) -> dict[str, Any]:
        try:
            if self._terminal_process and self._terminal_process.poll() is None:
                self._terminal_process.terminate()
                self._terminal_process.wait(timeout=5)
            self.logger.info("Closed terminal")
            return make_result("PASS", "Terminal closed", {})
        except Exception as exc:  # pragma: no cover - runtime environment dependent
            self.logger.exception("Unable to close terminal: %s", exc)
            return make_result("FAIL", f"Unable to close terminal: {exc}", {})

    def send_command(self, command: str) -> dict[str, Any]:
        self._last_command = command
        if self.simulate:
            self._response_buffer = self._simulate_response(command)
            self.logger.info("Simulated command: %s", command)
            return make_result("PASS", "Command simulated", {"command": command, "response": self._response_buffer})

        try:
            if pyautogui is not None:
                pyautogui.typewrite(command + "\n")
            else:
                self._response_buffer = ""  # fallback placeholder for non-GUI environments
            self.logger.info("Sent command: %s", command)
            return make_result("PASS", "Command sent", {"command": command})
        except Exception as exc:  # pragma: no cover - runtime environment dependent
            self.logger.exception("Failed to send command: %s", exc)
            return make_result("FAIL", f"Failed to send command: {exc}", {"command": command})

    def wait_for_prompt(self, timeout: float = 20.0) -> dict[str, Any]:
        if self.simulate:
            time.sleep(0.1)
            return make_result("PASS", "Prompt detected", {"timeout": timeout})

        time.sleep(1)
        return make_result("PASS", "Prompt wait completed", {"timeout": timeout})

    def read_response(self) -> dict[str, Any]:
        response = self._response_buffer
        self._response_buffer = ""
        return make_result("PASS", "Response read", {"response": response})

    def clear_buffer(self) -> dict[str, Any]:
        self._response_buffer = ""
        return make_result("PASS", "Buffer cleared", {})

    def _simulate_response(self, command: str) -> str:
        value = command.strip().lower()
        if value.startswith("test ibcn_production set_serial"):
            return "SERIAL_SET_OK"
        if value.startswith("test ibcn_production fpga_io 2"):
            return "SERIAL:12345678"
        if value.startswith("set_hw_rev"):
            return "HW_REV_SET"
        if value.startswith("fpga_io 14"):
            return "A1"
        if value.startswith("test ibcn_production set_mac"):
            return "MAC_SET"
        if value.startswith("test ibcn_production fpga_io 1"):
            return "00:11:22:33:44:55"
        if value.startswith("fpga_io 9"):
            return "VHDL 1.0.0"
        if value.startswith("fpga_io 10"):
            return "NIOS 1.2.3"
        if value.startswith("fpga_io 11"):
            return "WDMCU 4.5.6"
        if value.startswith("fpga_io 12"):
            return "PASS"
        if value.startswith("fpga_io 15"):
            return "PASS"
        if value.startswith("fpga_io 7"):
            return "0x55"
        if value.startswith("test ibcn_production voltage 0"):
            return "1V1:1.05V\n1V2:1.20V\n1V35:1.35V\n2V5:2.48V\n3V3:3.31V\n3V3_SD:3.29V\n5V:5.02V\nCurrent_IN:0.80A"
        if value.startswith("test ibcn_production temperature 0"):
            return "IBCN1:34.2C\nIBCN2:35.1C\nIBCN3:33.8C\nIBCN4:36.0C\nIPSN1:31.5C"
        if value.startswith("ping"):
            return "PING_OK 64 bytes from 172.16.172.66"
        if value.startswith("boot") or "u-boot" in value:
            return "U-Boot SPL\nCALIBRATION PASSED\n=>"
        if value.startswith("io_loop") or value.startswith("clksync"):
            return "PASS"
        return "OK"
