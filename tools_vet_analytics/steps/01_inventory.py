from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from ..common.mongo import safe_upsert_many
from ..common.schema_infer import infer_schema_profile

STRUCTURED_HINTS = {
    "red_flags", "triage", "diagnostic_steps", "differentials", "symptoms", "protocol", "steps", "assessment"
}


def _classify(schema: Dict[str, Any]) -> Dict[str, Any]:
    fp = schema["field_profiles"]
    triggers = []
    structured = False
    for field, prof in fp.items():
        leaf = field.split(".")[-1].lower()
        cov = prof.get("coverage_pct", 0)
        if leaf in STRUCTURED_HINTS and cov > 0.1:
            structured = True
            triggers.append({"field": field, "coverage_pct": cov})
    has_content = len(schema.get("content_fields", [])) > 0
    if structured and has_content:
        ctype = "mixed"
    elif structured:
        ctype = "structured_logic"
    elif has_content:
        ctype = "raw_text"
    else:
        ctype = "unknown"
    return {"collection_type": ctype, "classification_evidence": triggers}


def run(ctx):
    db = ctx["mongo"].read_db
    wdb = ctx["mongo"].write_db
    cfg = ctx["config"]
    logger = ctx["logger"]

    out = []
    for coll in db.list_collection_names():
        c = db[coll]
        count = c.count_documents({})
        sample_n = min(cfg.sample_per_collection, count)
        if cfg.limit and sample_n > cfg.limit:
            sample_n = cfg.limit
        samples = list(c.find({}, limit=sample_n))
        stats = {"stats_available": False}
        try:
            cs = db.command("collStats", coll)
            stats = {
                "stats_available": True,
                "size": cs.get("size"),
                "storageSize": cs.get("storageSize"),
                "avgObjSize": cs.get("avgObjSize"),
                "nindexes": cs.get("nindexes"),
            }
        except Exception:
            pass
        schema = infer_schema_profile(samples)
        cls = _classify(schema)

        title_dup = {}
        for tf in schema.get("title_fields", [])[:1]:
            vals = [s.get(tf.split(".")[-1]) for s in samples if isinstance(s.get(tf.split(".")[-1]), str)]
            cnt = Counter(vals)
            title_dup = {"field": tf, "top_repeats": cnt.most_common(5)}

        doc = {
            "inventory_id": f"inv::{coll}",
            "run_id": cfg.run_id,
            "collection": coll,
            "count": count,
            "sample_size": sample_n,
            "schema": schema,
            "classification": cls,
            "coll_stats": stats,
            "suspected_duplicates": title_dup,
        }
        out.append(doc)

    safe_upsert_many(wdb["inv_inventory"], out, "inventory_id", cfg.run_id, dry_run=cfg.dry_run)

    Path("reports").mkdir(exist_ok=True)
    Path("reports/inventory.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = ["| collection | count | type | sample |", "|---|---:|---|---:|"]
    for d in out:
        rows.append(f"| {d['collection']} | {d['count']} | {d['classification']['collection_type']} | {d['sample_size']} |")
    content_fields = []
    for d in out:
        for f in d["schema"].get("content_fields", []):
            content_fields.append((f"{d['collection']}.{f}", d["schema"]["field_profiles"][f]["avg_length"]))
    content_fields = sorted(content_fields, key=lambda x: x[1], reverse=True)[:10]
    lang_summary = []
    for d in out:
        for lf in d["schema"].get("language_fields", []):
            cov = d["schema"]["field_profiles"][lf]["coverage_pct"]
            lang_summary.append(f"- {d['collection']}.{lf}: {cov:.1%}")

    md = "\n".join([
        "# Inventory Summary", "", *rows, "", "## Top content fields by avg length", *[f"- {a}: {b:.1f}" for a, b in content_fields],
        "", "## Language field coverage", *(lang_summary or ["- none detected"]),
    ])
    Path("reports/inventory.md").write_text(md, encoding="utf-8")
    logger.info("Inventory done: %d collections", len(out))
    ctx["inventory"] = out
