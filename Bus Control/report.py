from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils import LoggerFactory, make_result


class ReportGenerator:
    """Generates JSON and CSV reports for the automation run."""

    def __init__(self, config: dict[str, Any], logger: Any = None) -> None:
        self.config = config
        self.logger = logger or LoggerFactory.get_logger("ReportGenerator")

    def generate(self, results: list[dict[str, Any]], report_dir: str | Path | None = None) -> dict[str, Any]:
        report_dir = Path(report_dir or self.config.get("report_folder", "reports"))
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = report_dir / f"ibcn_report_{timestamp}.json"
        csv_path = report_dir / f"ibcn_report_{timestamp}.csv"

        with json_path.open("w", encoding="utf-8") as handle:
            json.dump({"timestamp": timestamp, "results": results}, handle, indent=2)

        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["module", "status", "message"])
            writer.writeheader()
            for row in results:
                writer.writerow({"module": row.get("module", ""), "status": row.get("status", ""), "message": row.get("message", "")})

        return make_result("PASS", "Reports written", {"json": str(json_path), "csv": str(csv_path)})
