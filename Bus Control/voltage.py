from __future__ import annotations

import re
from typing import Any

from utils import LoggerFactory, make_result


class VoltageModule:
    """Reads and validates voltage rails."""

    def __init__(self, communication: Any, config: dict[str, Any], limits: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.limits = limits
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("VoltageModule")

    def read_voltage(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("voltage", {}).get("read", "test ibcn_production voltage 0"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        values: dict[str, float] = {}
        for line in text.splitlines():
            if ":" in line:
                name, raw_value = line.split(":", 1)
                try:
                    values[name.strip()] = float(raw_value.replace("V", ""))
                except ValueError:
                    continue
        return make_result("PASS", "Voltage values read", {"values": values})

    def verify(self, values: dict[str, float]) -> dict[str, Any]:
        failures: list[str] = []
        for rail, value in values.items():
            rail_limits = self.limits.get("voltage", {}).get(rail)
            if rail_limits is None:
                continue
            lower, upper = rail_limits["min"], rail_limits["max"]
            if not (lower <= value <= upper):
                failures.append(f"{rail}={value} outside [{lower}, {upper}]")
        if failures:
            return make_result("FAIL", "Voltage verification failed", {"failures": failures})
        return make_result("PASS", "Voltage verification passed", {"values": values})

    def run(self) -> dict[str, Any]:
        read_result = self.read_voltage()
        values = read_result.get("data", {}).get("values", {})
        verify_result = self.verify(values)
        return make_result(verify_result["status"], verify_result["message"], {"values": values, "verification": verify_result["data"]})
