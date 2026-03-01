from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .common.mongo import connect_mongo
from .common.tfidf import get_stopwords_for_locales
from .config import load_env_config

COLLS = ["inv_inventory", "evidence_blocks", "kb_concepts", "kb_atoms", "qa_units", "dedup_groups", "qa_eval", "run_reports"]


def parse_args():
    p = argparse.ArgumentParser(description="Export static dashboard data JSON")
    p.add_argument("--out", type=str, default="reports/dashboard_data.json")
    p.add_argument("--limit-runs", type=int, default=10)
    return p.parse_args()


def _bad_title(title: str, stopwords: set[str]) -> bool:
    tokens = [t.strip().lower() for t in (title or "").split(",") if t.strip()]
    if len(tokens) < 2:
        return True
    return all((len(t) < 3 or t in stopwords or t.isdigit()) for t in tokens)


def main():
    args = parse_args()
    cfg = load_env_config()
    mongo = connect_mongo(cfg.mongo_uri_read, cfg.mongo_uri_write, cfg.mongo_db_read, cfg.mongo_db_write)
    wdb = mongo.write_db

    reports = list(wdb["run_reports"].find({}, {"_id": 0}).sort("_id", -1).limit(args.limit_runs))
    stopwords = set(get_stopwords_for_locales(["ru", "pt", "sw"]))

    payload = {"runs": []}
    for rep in reports:
        run_id = rep.get("run_id")
        if not run_id:
            continue
        counts = {c: wdb[c].count_documents({"run_id": run_id}) for c in COLLS}

        locale_ctr = Counter()
        for b in wdb["evidence_blocks"].find({"run_id": run_id}, {"source_locale": 1}):
            locale_ctr[(b.get("source_locale") or "und").lower()] += 1

        bad_titles = []
        for c in wdb["kb_concepts"].find({"run_id": run_id}, {"title_guess": 1}).limit(300):
            tg = c.get("title_guess", "")
            if _bad_title(tg, stopwords):
                bad_titles.append(tg)
                if len(bad_titles) >= 20:
                    break

        qa_sample = []
        for q in wdb["qa_units"].find({"run_id": run_id}, {"audience": 1, "tone": 1, "title": 1, "content.summary": 1}).limit(20):
            if len(qa_sample) >= 3:
                break
            qa_sample.append(
                {
                    "audience": q.get("audience"),
                    "tone": q.get("tone"),
                    "title": q.get("title"),
                    "summary": (q.get("content") or {}).get("summary", ""),
                }
            )

        payload["runs"].append(
            {
                "run_id": run_id,
                "created_at": rep.get("created_at") or rep.get("configs", {}).get("run_id"),
                "coverage": rep.get("coverage", {}),
                "gaps": rep.get("gaps", {}),
                "title_stats": rep.get("title_stats", {}),
                "counts": counts,
                "locale_distribution": dict(locale_ctr),
                "bad_titles": bad_titles,
                "qa_units_sample": qa_sample,
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
