import logging
import os
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Centralised logging configuration.
#
# The suite emits logs at three destinations so that they are useful both when
# watching a live run in the terminal and when triaging a CI failure afterwards:
#   1. Console  -> human friendly, colour-free, level + message.
#   2. File     -> fully qualified, timestamped, written to logs/run_<ts>.log.
#   3. The test frameworks (pytest / allure) capture the same records via
#      caplog / stdout so they surface in the HTML reports too.
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
_LOG_FILE = LOG_DIR / f"run_{_RUN_STAMP}.log"

_CONSOLE_FMT = "%(levelname)-7s %(name)s | %(message)s"
_FILE_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"

_ROOT = logging.getLogger("tmdb_tests")
_ROOT.setLevel(logging.DEBUG)

if not _ROOT.handlers:
    _console = logging.StreamHandler()
    _console.setLevel(logging.INFO)
    _console.setFormatter(logging.Formatter(_CONSOLE_FMT))

    _file = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    _file.setLevel(logging.DEBUG)
    _file.setFormatter(logging.Formatter(_FILE_FMT))

    _ROOT.addHandler(_console)
    _ROOT.addHandler(_file)


def get_logger(name: str = "tmdb_tests") -> logging.Logger:
    """Return a child logger namespaced under ``tmdb_tests``.

    Using a child logger (e.g. ``tmdb_tests.pages.discover``) keeps the module
    origin visible in every record while inheriting the root handlers above.
    """
    return logging.getLogger(f"tmdb_tests.{name}")


def log_file_path() -> str:
    return str(_LOG_FILE)
