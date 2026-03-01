from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many
from ..common.normalize import split_chunks
from ..common.tfidf import stopword_hit_count


INVALID_LANG = {"", "none", "und"}


def _get_dotted_value(doc, path):
    cur = doc
    for key in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
        if cur is None:
            return None
    return cur


def _locale_matches_prefix(locale: str, include_locales: list[str]) -> bool:
    if not include_locales:
        return True
    norm = (locale or "und").strip().lower()
    return any(norm.startswith(pref) for pref in include_locales)


def _heuristic_locale(text: str) -> str:
    sample = (text or "")[:1500].lower()
    scores = {
        "ru": stopword_hit_count(sample, "ru"),
        "pt": stopword_hit_count(sample, "pt"),
        "sw": stopword_hit_count(sample, "sw"),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] >= 5 else "und"


def _effective_locale(doc, text: str) -> str:
    lang_tag = str(doc.get("lang_tag") or "").strip().lower()
    if lang_tag:
        return lang_tag

    language = str(doc.get("language") or doc.get("lang") or doc.get("locale") or doc.get("source_locale") or "").strip().lower()
    if language and language not in INVALID_LANG:
        return language

    return _heuristic_locale(text)


def run(ctx):
    cfg = ctx["config"]
    rdb = ctx["mongo"].read_db
    wdb = ctx["mongo"].write_db
    read_run_id = cfg.active_run_id or cfg.run_id
    selected = ctx.get("selected_sources", [])

    out = []
    locale_count = Counter()
    include_locales = cfg.include_locales or []

    for coll, _, content_field in selected:
        proj = {
            content_field: 1,
            "title": 1,
            "name": 1,
            "language": 1,
            "lang": 1,
            "lang_tag": 1,
            "locale": 1,
            "source_locale": 1,
        }
        cur = rdb[coll].find({}, proj)
        if cfg.limit:
            cur = cur.limit(cfg.limit)
        for doc in cur:
            text = _get_dotted_value(doc, content_field)
            if not isinstance(text, str) or not text.strip():
                continue
            locale = _effective_locale(doc, text)
            if not _locale_matches_prefix(locale, include_locales):
                continue

            chunks = split_chunks(text, cfg.chunk_size_chars, cfg.overlap_chars)
            locale_count[locale] += len(chunks)
            for i, chunk in enumerate(chunks):
                bh = sha1_text(chunk)
                block_id = sha1_text(f"{coll}|{doc.get('_id')}|{i}|{bh}")
                out.append(
                    {
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
                    }
                )

    safe_upsert_many(wdb["evidence_blocks"], out, "block_id", cfg.run_id, dry_run=cfg.dry_run)
    md = ["# Evidence Blocks", "", f"blocks: {len(out)}", "", "Locales:"]
    for k, v in locale_count.items():
        md.append(f"- {k}: {v}")
    if out:
        md.append(f"\nAverage length: {sum(x['char_len'] for x in out)/len(out):.1f}")
    Path("reports/evidence_blocks.md").write_text("\n".join(md), encoding="utf-8")
    Path("reports/evidence_blocks.json").write_text(
        json.dumps({"count": len(out), "locale_distribution": dict(locale_count)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
