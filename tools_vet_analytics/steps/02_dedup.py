from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many
from ..common.normalize import normalize_ru_text


def _get_dotted_value(doc, path):
    cur = doc
    for key in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
        if cur is None:
            return None
    return cur


def _load_inventory(ctx):
    if "inventory" in ctx:
        return ctx["inventory"]
    return list(ctx["mongo"].write_db["inv_inventory"].find({"run_id": ctx["config"].run_id}))


def run(ctx):
    cfg = ctx["config"]
    rdb = ctx["mongo"].read_db
    wdb = ctx["mongo"].write_db
    inv = _load_inventory(ctx)

    candidates = []
    for d in inv:
        ctype = d["classification"]["collection_type"]
        cfields = d["schema"].get("content_fields", [])
        if ctype in {"raw_text", "mixed"} and cfields:
            candidates.append((d["collection"], d["count"], cfields[0]))
    candidates.sort(key=lambda x: x[1], reverse=True)
    selected = candidates[:3]
    ctx["selected_sources"] = selected

    groups = defaultdict(lambda: {"count": 0, "doc_ids": [], "titles": [], "snippet": "", "source_collection": ""})
    for coll, _, content_field in selected:
        c = rdb[coll]
        limit = cfg.limit or 0
        cur = c.find({}, {content_field: 1, "title": 1, "name": 1})
        if limit:
            cur = cur.limit(limit)
        for doc in cur:
            raw = _get_dotted_value(doc, content_field) or ""
            if not isinstance(raw, str) or not raw.strip():
                continue
            norm = normalize_ru_text(raw)
            h = sha1_text(norm)
            g = groups[h]
            g["count"] += 1
            g["source_collection"] = coll
            if len(g["doc_ids"]) < 100:
                g["doc_ids"].append(str(doc.get("_id")))
            t = doc.get("title") or doc.get("name")
            if isinstance(t, str) and len(g["titles"]) < 50:
                g["titles"].append(t)
            if not g["snippet"]:
                g["snippet"] = norm[:300]

    out = []
    for h, g in groups.items():
        out.append({
            "dedup_id": f"raw::{h}",
            "run_id": cfg.run_id,
            "dedup_type": "raw_text",
            "norm_hash": h,
            "count": g["count"],
            "source_collection": g["source_collection"],
            "doc_ids": g["doc_ids"],
            "titles": g["titles"],
            "sample_snippet": g["snippet"],
        })

    safe_upsert_many(wdb["dedup_groups"], out, "dedup_id", cfg.run_id, dry_run=cfg.dry_run)
    Path("reports/dedup_raw_text.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Raw Text Dedup", "", f"groups: {len(out)}", "", "Top duplicates:"]
    for d in sorted(out, key=lambda x: x["count"], reverse=True)[:20]:
        md.append(f"- {d['norm_hash'][:10]}... count={d['count']} collection={d['source_collection']}")
    Path("reports/dedup_raw_text.md").write_text("\n".join(md), encoding="utf-8")
