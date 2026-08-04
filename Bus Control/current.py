from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class CurrentModule:
    """Reads and validates current values."""

    def __init__(self, communication: Any, config: dict[str, Any], limits: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.limits = limits
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("CurrentModule")

    def read_current(self) -> dict[str, Any]:
        self.communication.send_command(self.commands.get("current", {}).get("read", "test ibcn_production voltage 0"))
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        current_value = None
        for line in text.splitlines():
            if line.startswith("Current_IN"):
                _, raw_value = line.split(":", 1)
                current_value = float(raw_value.replace("A", ""))
                break
        return make_result("PASS", "Current value read", {"current": current_value})

    def verify(self, current_value: float | None) -> dict[str, Any]:
        if current_value is None:
            return make_result("FAIL", "Current value missing", {})
        limit = self.limits.get("current", {}).get("Current_IN")
        if limit is None:
            return make_result("PASS", "Current limit not configured", {"current": current_value})
        if limit["min"] <= current_value <= limit["max"]:
            return make_result("PASS", "Current verification passed", {"current": current_value})
        return make_result("FAIL", "Current verification failed", {"current": current_value, "limit": limit})

    def run(self) -> dict[str, Any]:
        read_result = self.read_current()
        current_value = read_result.get("data", {}).get("current")
        verify_result = self.verify(current_value)
        return make_result(verify_result["status"], verify_result["message"], {"current": current_value, "verification": verify_result["data"]})
