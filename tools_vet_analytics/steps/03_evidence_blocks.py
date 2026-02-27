from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many
from ..common.normalize import split_chunks


def run(ctx):
    cfg = ctx["config"]
    rdb = ctx["mongo"].read_db
    wdb = ctx["mongo"].write_db
    selected = ctx.get("selected_sources", [])

    out = []
    locale_count = Counter()
    for coll, _, content_field in selected:
        field = content_field.split(".")[-1]
        proj = {field: 1, "title": 1, "name": 1, "language": 1, "lang": 1, "locale": 1, "source_locale": 1}
        cur = rdb[coll].find({}, proj)
        if cfg.limit:
            cur = cur.limit(cfg.limit)
        for doc in cur:
            text = doc.get(field)
            if not isinstance(text, str) or not text.strip():
                continue
            chunks = split_chunks(text, cfg.chunk_size_chars, cfg.overlap_chars)
            locale = doc.get("language") or doc.get("lang") or doc.get("locale") or doc.get("source_locale") or "ru"
            locale_count[locale] += len(chunks)
            for i, chunk in enumerate(chunks):
                bh = sha1_text(chunk)
                block_id = sha1_text(f"{coll}|{doc.get('_id')}|{i}|{bh}")
                out.append({
                    "block_id": block_id,
                    "run_id": cfg.run_id,
                    "source_collection": coll,
                    "source_doc_id": str(doc.get("_id")),
                    "title": doc.get("title") or doc.get("name"),
                    "source_locale": locale,
                    "text": chunk,
                    "text_hash": bh,
                    "char_len": len(chunk),
                    "block_index": i,
                })

    safe_upsert_many(wdb["evidence_blocks"], out, "block_id", cfg.run_id, dry_run=cfg.dry_run)
    md = ["# Evidence Blocks", "", f"blocks: {len(out)}", "", "Locales:"]
    for k, v in locale_count.items():
        md.append(f"- {k}: {v}")
    if out:
        md.append(f"\nAverage length: {sum(x['char_len'] for x in out)/len(out):.1f}")
    Path("reports/evidence_blocks.md").write_text("\n".join(md), encoding="utf-8")
    Path("reports/evidence_blocks.json").write_text(json.dumps({"count": len(out), "locale_distribution": locale_count}, ensure_ascii=False, indent=2, default=dict), encoding="utf-8")
