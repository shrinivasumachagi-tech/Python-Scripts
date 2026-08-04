from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from address import AddressModule
from communication import Communication
from current import CurrentModule
from dip_switch import DipSwitchModule
from ethernet import EthernetModule
from fpga_io import FPGAIOModule
from hardware_version import HardwareVersionModule
from led import LEDModule
from mac_address import MACAddressModule
from report import ReportGenerator
from serial_number import SerialNumberModule
from startup import StartupModule
from temperature import TemperatureModule
from utils import FileHelper, LoggerFactory, ensure_dir, make_result
from voltage import VoltageModule

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"
LIMITS_PATH = BASE_DIR / "config" / "limits.json"
COMMANDS_PATH = BASE_DIR / "config" / "commands.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IBCN Automation Framework")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    parser.add_argument("--serial", default=None, help="Override serial number")
    parser.add_argument("--mac", default=None, help="Override MAC address")
    parser.add_argument("--hw-revision", default="A1", help="Override hardware revision")
    return parser.parse_args()


def build_runtime_context(args: argparse.Namespace) -> dict[str, Any]:
    config = FileHelper.read_json(CONFIG_PATH)
    limits = FileHelper.read_json(LIMITS_PATH)
    commands = FileHelper.read_json(COMMANDS_PATH)

    log_dir = ensure_dir(config.get("log_folder", "logs"))
    report_dir = ensure_dir(config.get("report_folder", "reports"))
    logger = LoggerFactory.get_logger("IBCN_Automation", os.path.join(log_dir, "automation.log"))

    return {
        "config": config,
        "limits": limits,
        "commands": commands,
        "logger": logger,
        "log_dir": log_dir,
        "report_dir": report_dir,
        "simulate": args.simulate or os.getenv("IBCN_SIMULATE", "0").lower() in {"1", "true", "yes"},
        "serial": args.serial,
        "mac": args.mac,
        "hw_revision": args.hw_revision,
    }


def run_sequence(context: dict[str, Any]) -> dict[str, Any]:
    logger = context["logger"]
    config = context["config"]
    limits = context["limits"]
    commands = context["commands"]
    simulate = context["simulate"]

    communication = Communication(config=config, logger=logger, simulate=simulate)
    startup_result = communication.open_terminal()
    if startup_result["status"] != "PASS":
        logger.error("Communication failed to initialize: %s", startup_result["message"])
        return make_result("FAIL", "Communication initialization failed", {"details": startup_result})

    modules = [
        ("startup", StartupModule(communication, config, commands, logger)),
        ("serial_number", SerialNumberModule(communication, config, commands, logger)),
        ("hardware_version", HardwareVersionModule(communication, config, commands, logger)),
        ("mac_address", MACAddressModule(communication, config, commands, logger)),
        ("fpga_io", FPGAIOModule(communication, config, commands, logger)),
        ("voltage", VoltageModule(communication, config, limits, commands, logger)),
        ("current", CurrentModule(communication, config, limits, commands, logger)),
        ("temperature", TemperatureModule(communication, config, limits, commands, logger)),
        ("ethernet", EthernetModule(communication, config, commands, logger)),
        ("led", LEDModule(communication, config, logger, simulate=simulate)),
        ("address", AddressModule(communication, config, commands, logger)),
        ("dip_switch", DipSwitchModule(communication, config, logger, simulate=simulate)),
    ]

    results = []
    for name, module in modules:
        try:
            if name == "startup":
                result = module.run()
            elif name == "serial_number":
                result = module.run(context.get("serial"))
            elif name == "hardware_version":
                result = module.run(context.get("hw_revision"))
            elif name == "mac_address":
                result = module.run(context.get("mac"))
            elif name == "led":
                result = module.run()
            elif name == "dip_switch":
                result = module.run()
            else:
                result = module.run()
            results.append({"module": name, **result})
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.exception("Module %s failed unexpectedly", name)
            results.append({"module": name, "status": "FAIL", "message": str(exc), "data": {}})

    report_generator = ReportGenerator(config=config, logger=logger)
    report_result = report_generator.generate(results, report_dir=context["report_dir"])

    communication.close_terminal()

    overall_status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
    overall_message = "Automation sequence completed successfully" if overall_status == "PASS" else "Automation sequence completed with failures"
    return make_result(
        overall_status,
        overall_message,
        {
            "results": results,
            "report": report_result["data"],
            "simulate": simulate,
        },
    )


def main() -> None:
    args = parse_args()
    context = build_runtime_context(args)
    result = run_sequence(context)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
