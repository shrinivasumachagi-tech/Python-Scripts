from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any


def make_result(status: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"status": status, "message": message, "data": data or {}}


class LoggerFactory:
    """Creates configured loggers."""

    @staticmethod
    def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
            if log_file:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        return logger


class Timer:
    """Simple timing helper."""

    def __init__(self) -> None:
        self.start_time = time.time()

    def elapsed(self) -> float:
        return time.time() - self.start_time


class RetryMechanism:
    """Performs retries for transient failures."""

    def __init__(self, retries: int = 3, delay: float = 0.5) -> None:
        self.retries = retries
        self.delay = delay

    def run(self, action, *args: Any, **kwargs: Any) -> Any:
        for attempt in range(self.retries):
            try:
                return action(*args, **kwargs)
            except Exception:
                if attempt == self.retries - 1:
                    raise
                time.sleep(self.delay)
        raise RuntimeError("Retry mechanism exhausted")


class RegexParser:
    """Helper methods for extracting values from text."""

    @staticmethod
    def extract(pattern: str, text: str) -> str | None:
        match = re.search(pattern, text)
        return match.group(1) if match else None


class PromptDetector:
    """Detects common prompt tokens in received text."""

    @staticmethod
    def has_prompt(text: str) -> bool:
        return any(token in text for token in ("=>", "login:", "#", ">"))


class ResponseParser:
    """Parses response text into a dictionary."""

    @staticmethod
    def parse_key_value(text: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result


class TimestampGenerator:
    """Generates timestamps for filenames and reports."""

    @staticmethod
    def now() -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")


class FileHelper:
    """Loads and saves JSON files."""

    @staticmethod
    def read_json(path: str | os.PathLike[str]) -> dict[str, Any]:
        path = Path(path)
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def ensure_dir(path: str | os.PathLike[str]) -> str:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)
