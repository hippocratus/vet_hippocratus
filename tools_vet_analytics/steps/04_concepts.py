from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

from ..common.mongo import safe_upsert_many
from ..common.tfidf import build_tfidf


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    blocks = list(wdb["evidence_blocks"].find({"run_id": cfg.run_id}))
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
    for ci, idxs in cluster_to_idx.items():
        rows = mat[idxs]
        mean = np.asarray(rows.mean(axis=0)).ravel()
        top_idx = mean.argsort()[::-1][:20]
        feats = vec.get_feature_names_out()
        keywords = [feats[i] for i in top_idx if mean[i] > 0]

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
                "title_guess": ", ".join(keywords[:3]) if keywords else f"concept {ci}",
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
    Path("reports/concepts_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("reports/concepts_summary.md").write_text(
        "# Concepts\n\n" + "\n".join(f"- {d['concept_id']} ({d['block_count']} blocks): {d['title_guess']}" for d in out),
        encoding="utf-8",
    )
