from __future__ import annotations

from typing import Any

from utils import LoggerFactory, make_result


class EthernetModule:
    """Checks Ethernet reachability by issuing ping commands."""

    def __init__(self, communication: Any, config: dict[str, Any], commands: dict[str, Any], logger: Any = None) -> None:
        self.communication = communication
        self.config = config
        self.commands = commands
        self.logger = logger or LoggerFactory.get_logger("EthernetModule")

    def ping(self, host: str) -> dict[str, Any]:
        self.communication.send_command(f"ping {host}")
        response = self.communication.read_response()
        text = response.get("data", {}).get("response", "")
        return make_result("PASS" if "PING_OK" in text else "FAIL", f"Ping result for {host}", {"host": host, "response": text})

    def run(self) -> dict[str, Any]:
        hosts = self.config.get("ethernet_hosts", ["172.16.172.66", "192.168.0.100"])
        results = [self.ping(host) for host in hosts]
        status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
        return make_result(status, "Ethernet verification completed", {"results": results})
