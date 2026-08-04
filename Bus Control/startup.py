from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class StartupModule:
    """Validates DUT boot readiness and prompt availability."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("StartupModule")

    def run(self) -> dict[str, Any]:
        try:
            self.communication.send_command("boot")
            self.communication.wait_for_prompt(timeout=self.config.get("timeout", 30))
            response = self.communication.read_response()
            text = response.get("data", {}).get("response", "")
            if "U-Boot SPL" in text and "CALIBRATION PASSED" in text and ("=>" in text or "login:" in text):
                return make_result("PASS", "Boot sequence completed", {"response": text})
            return make_result("FAIL", "Boot verification failed", {"response": text})
        except Exception as exc:  # pragma: no cover - defensive fallback
            self.logger.exception("Startup verification failed")
            return make_result("FAIL", f"Startup verification failed: {exc}", {})
