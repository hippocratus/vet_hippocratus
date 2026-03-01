from __future__ import annotations

import argparse
import importlib
import sys
import uuid

from .common.logging import setup_logging
from .common.mongo import connect_mongo
from .config import load_env_config


STEP_MODULES = {
    1: "tools_vet_analytics.steps.01_inventory",
    2: "tools_vet_analytics.steps.02_dedup",
    3: "tools_vet_analytics.steps.03_evidence_blocks",
    4: "tools_vet_analytics.steps.04_concepts",
    5: "tools_vet_analytics.steps.05_atoms",
    6: "tools_vet_analytics.steps.06_qa_units",
    7: "tools_vet_analytics.steps.07_retrieval_eval",
    8: "tools_vet_analytics.steps.08_final_report",
}

OUTPUT_COLLECTIONS = [
    "inv_inventory",
    "inv_samples",
    "dedup_groups",
    "evidence_blocks",
    "kb_concepts",
    "kb_atoms",
    "qa_units",
    "qa_eval",
    "run_reports",
]


def parse_args():
    p = argparse.ArgumentParser(description="Vet analytics pipeline")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--sample-per-collection", type=int, default=200)
    p.add_argument("--chunk-size-chars", type=int, default=1500)
    p.add_argument("--overlap-chars", type=int, default=250)
    p.add_argument("--k-clusters", type=int, default=50)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--from-step", type=int, default=1)
    p.add_argument("--to-step", type=int, default=8)
    p.add_argument("--run-id", type=str, default="")
    p.add_argument("--active-run-id", type=str, default="")
    p.add_argument("--include-locales", type=str, default="", help="Comma-separated locale prefixes, e.g. ru,pt-br,sw")
    p.add_argument("--allow-overwrite-run", action="store_true")
    p.add_argument("--recompute-titles-only", action="store_true")
    return p.parse_args()


def _parse_locales(value: str) -> list[str]:
    return [x.strip().lower() for x in (value or "").split(",") if x.strip()]


def _run_has_outputs(write_db, run_id: str) -> bool:
    for coll in OUTPUT_COLLECTIONS:
        if write_db[coll].find_one({"run_id": run_id}, {"_id": 1}):
            return True
    return False


def main():
    args = parse_args()
    cfg = load_env_config()
    cfg.dry_run = args.dry_run
    cfg.limit = args.limit
    cfg.sample_per_collection = args.sample_per_collection
    cfg.chunk_size_chars = args.chunk_size_chars
    cfg.overlap_chars = args.overlap_chars
    cfg.k_clusters = args.k_clusters
    cfg.resume = args.resume
    cfg.from_step = args.from_step
    cfg.to_step = args.to_step
    cfg.run_id = args.run_id or str(uuid.uuid4())
    cfg.active_run_id = args.active_run_id or cfg.run_id
    cfg.include_locales = _parse_locales(args.include_locales)
    cfg.allow_overwrite_run = args.allow_overwrite_run
    cfg.recompute_titles_only = args.recompute_titles_only

    if cfg.recompute_titles_only:
        if not args.run_id:
            print("--recompute-titles-only requires explicit --run-id", file=sys.stderr)
            sys.exit(1)
        cfg.from_step = 4
        cfg.to_step = 4
        cfg.active_run_id = cfg.run_id

    logger = setup_logging(cfg.run_id)
    mongo = connect_mongo(cfg.mongo_uri_read, cfg.mongo_uri_write, cfg.mongo_db_read, cfg.mongo_db_write)

    if args.run_id and not cfg.allow_overwrite_run and _run_has_outputs(mongo.write_db, cfg.run_id):
        logger.error("run_id=%s already has output docs; pass --allow-overwrite-run to overwrite", cfg.run_id)
        sys.exit(1)

    ctx = {"config": cfg, "logger": logger, "mongo": mongo, "warnings": []}
    logger.info(
        "Starting run_id=%s active_run_id=%s steps=%s..%s include_locales=%s",
        cfg.run_id,
        cfg.active_run_id,
        cfg.from_step,
        cfg.to_step,
        cfg.include_locales,
    )

    for i in range(cfg.from_step, cfg.to_step + 1):
        module = importlib.import_module(STEP_MODULES[i])
        logger.info("Running step %02d", i)
        module.run(ctx)

    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
