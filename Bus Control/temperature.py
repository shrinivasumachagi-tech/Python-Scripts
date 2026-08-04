from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class TemperatureModule:
    """Reads and validates temperature sensors."""

    def __init__(self, communication: Any, config: dict[str, Any], limits: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.limits = limits
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("TemperatureModule")

    def read_temperature(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("temperature", {}).get("read", "test ibcn_production temperature 0"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        values: dict[str, float] = {}
        for line in text.splitlines():
            if ":" in line:
                sensor, raw_value = line.split(":", 1)
                try:
                    values[sensor.strip()] = float(raw_value.replace("C", ""))
                except ValueError:
                    continue
        return make_result("PASS", "Temperature values read", {"values": values})

    def verify(self, values: dict[str, float]) -> dict[str, Any]:
        failures: list[str] = []
        for sensor, value in values.items():
            sensor_limits = self.limits.get("temperature", {}).get(sensor)
            if sensor_limits is None:
                continue
            lower, upper = sensor_limits["min"], sensor_limits["max"]
            if not (lower <= value <= upper):
                failures.append(f"{sensor}={value} outside [{lower}, {upper}]")
        if failures:
            return make_result("FAIL", "Temperature verification failed", {"failures": failures})
        return make_result("PASS", "Temperature verification passed", {"values": values})

    def run(self) -> dict[str, Any]:
        read_result = self.read_temperature()
        values = read_result.get("data", {}).get("values", {})
        verify_result = self.verify(values)
        return make_result(verify_result["status"], verify_result["message"], {"values": values, "verification": verify_result["data"]})
