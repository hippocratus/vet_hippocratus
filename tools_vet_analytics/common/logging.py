from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(run_id: str) -> logging.Logger:
    Path("reports").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("vet_analytics")
    logger.setLevel(logging.INFO)
    logger.handlers = []

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    fh = logging.FileHandler(f"reports/run_{run_id}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger
