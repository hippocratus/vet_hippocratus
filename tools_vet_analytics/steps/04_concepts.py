from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

from ..common.mongo import safe_upsert_many
from ..common.tfidf import build_tfidf, load_ru_stopwords


STOPWORDS = load_ru_stopwords()


def _valid_kw(token: str) -> bool:
    t = (token or "").strip().lower()
    if len(t) < 3:
        return False
    if t in STOPWORDS:
        return False
    if t.isdigit():
        return False
    if len(t) == 1:
        return False
    return True


def _title_guess(keywords: list[str], cluster_index: int) -> str:
    picked = []
    for kw in keywords:
        if _valid_kw(kw):
            picked.append(kw)
        if len(picked) >= 3:
            break
    if len(picked) < 3:
        for kw in keywords:
            if kw not in picked and len(kw) >= 3 and not kw.isdigit():
                picked.append(kw)
            if len(picked) >= 3:
                break
    if not picked:
        return f"ветеринария: тема {cluster_index}"
    return ", ".join(picked[:3])


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    read_run_id = cfg.active_run_id or cfg.run_id
    blocks = list(wdb["evidence_blocks"].find({"run_id": read_run_id}))
    if not blocks:
        Path("reports/concepts_summary.md").write_text("# Concepts\n\nNo evidence blocks.", encoding="utf-8")
        return

    texts = [b["text"] for b in blocks]
    vec, mat = build_tfidf(texts)
    k = max(1, min(cfg.k_clusters, len(blocks)))
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(mat)
    centers = km.cluster_centers_

    cluster_to_idx = defaultdict(list)
    for i, l in enumerate(labels):
        cluster_to_idx[int(l)].append(i)

    now = datetime.now(timezone.utc).isoformat()
    out = []
    raw_stopword_dominated = 0
    final_stopword_dominated = 0
    for ci, idxs in cluster_to_idx.items():
        rows = mat[idxs]
        mean = np.asarray(rows.mean(axis=0)).ravel()
        top_idx = mean.argsort()[::-1][:40]
        feats = vec.get_feature_names_out()
        raw_keywords = [feats[i] for i in top_idx if mean[i] > 0]

        filtered_keywords = [kw for kw in raw_keywords if _valid_kw(kw)]
        keywords = filtered_keywords[:20] if filtered_keywords else raw_keywords[:20]

        raw_title_tokens = raw_keywords[:3]
        if raw_title_tokens and any(t.lower() in STOPWORDS for t in raw_title_tokens):
            raw_stopword_dominated += 1

        title_guess = _title_guess(keywords, ci)
        final_title_tokens = [t.strip().lower() for t in title_guess.split(",")[:3] if t.strip()]
        if final_title_tokens and any(t in STOPWORDS for t in final_title_tokens):
            final_stopword_dominated += 1

        dists = []
        for ii in idxs:
            row = mat[ii].toarray()[0]
            dist = np.linalg.norm(row - centers[ci])
            dists.append((dist, ii))
        rep = [blocks[ii]["block_id"] for _, ii in sorted(dists)[:5]]
        all_ids = [blocks[ii]["block_id"] for ii in idxs][:200]

        loc_dist = Counter(blocks[ii].get("source_locale", "ru") for ii in idxs)
        concept_id = f"cpt_{cfg.run_id}_{ci}"
        out.append(
            {
                "concept_id": concept_id,
                "run_id": cfg.run_id,
                "source_run_id": read_run_id,
                "title_guess": title_guess,
                "top_keywords": keywords,
                "rep_block_ids": rep,
                "block_ids": all_ids,
                "block_count": len(idxs),
                "source_locale_distribution": dict(loc_dist),
                "cluster_index": ci,
                "created_at": now,
            }
        )

    safe_upsert_many(wdb["kb_concepts"], out, "concept_id", cfg.run_id, dry_run=cfg.dry_run)
    Path("reports/concepts_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/concepts_summary.md").write_text(
        "# Concepts\n\n" + "\n".join(f"- {d['concept_id']} ({d['block_count']} blocks): {d['title_guess']}" for d in out),
        encoding="utf-8",
    )

    quality = {
        "run_id": cfg.run_id,
        "source_run_id": read_run_id,
        "concept_count": len(out),
        "stopword_dominated_titles_before": raw_stopword_dominated,
        "stopword_dominated_titles_after": final_stopword_dominated,
        "top_10_titles_after": [d["title_guess"] for d in out[:10]],
    }
    Path("reports/concepts_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/concepts_quality.md").write_text(
        "# Concepts Quality\n\n"
        f"- run_id: {cfg.run_id}\n"
        f"- source_run_id: {read_run_id}\n"
        f"- concepts: {len(out)}\n"
        f"- stopword-dominated titles (before): {raw_stopword_dominated}\n"
        f"- stopword-dominated titles (after): {final_stopword_dominated}\n\n"
        "## Top 10 titles after fix\n"
        + "\n".join(f"- {t}" for t in quality["top_10_titles_after"]),
        encoding="utf-8",
    )
