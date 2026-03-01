from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

from ..common.mongo import safe_upsert_many
from ..common.tfidf import build_tfidf, get_stopwords_for_locales


FALLBACK_TITLE = {
    "ru": "ветеринария: тема {cluster_index}",
    "pt": "veterinária: tema {cluster_index}",
    "sw": "mada: {cluster_index}",
}


def _locale_matches_prefix(locale: str, include_locales: list[str]) -> bool:
    if not include_locales:
        return True
    norm = (locale or "und").strip().lower()
    return any(norm.startswith(pref) for pref in include_locales)


def _valid_kw(token: str, stopwords: set[str]) -> bool:
    t = (token or "").strip().lower()
    if len(t) < 3:
        return False
    if t in stopwords:
        return False
    if t.isdigit():
        return False
    return True


def _fallback_title(cluster_index: int, locale: str) -> str:
    lang = (locale or "ru").split("-")[0]
    tmpl = FALLBACK_TITLE.get(lang, FALLBACK_TITLE["ru"])
    return tmpl.format(cluster_index=cluster_index)


def _title_guess(keywords: list[str], cluster_index: int, locale: str, stopwords: set[str]) -> str:
    usable = [kw for kw in keywords if _valid_kw(kw, stopwords)]
    if len(usable) < 2:
        return _fallback_title(cluster_index, locale)
    return ", ".join(usable[:5])


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    read_run_id = cfg.active_run_id or cfg.run_id
    include_locales = cfg.include_locales or []

    blocks = [
        b
        for b in wdb["evidence_blocks"].find({"run_id": read_run_id})
        if _locale_matches_prefix(b.get("source_locale", "und"), include_locales)
    ]
    if not blocks:
        Path("reports/concepts_summary.md").write_text("# Concepts\n\nNo evidence blocks.", encoding="utf-8")
        return

    texts = [b["text"] for b in blocks]
    vec, mat = build_tfidf(texts, locales=include_locales or ["ru", "pt", "sw"])
    stopwords = set(get_stopwords_for_locales(include_locales or ["ru", "pt", "sw"]))

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
    bad_titles = []
    good_titles = []

    feats = vec.get_feature_names_out()
    for ci, idxs in cluster_to_idx.items():
        rows = mat[idxs]
        mean = np.asarray(rows.mean(axis=0)).ravel()
        top_idx = mean.argsort()[::-1][:50]
        raw_keywords = [feats[i] for i in top_idx if mean[i] > 0]
        filtered_keywords = [kw for kw in raw_keywords if _valid_kw(kw, stopwords)]

        raw_title_tokens = raw_keywords[:3]
        if raw_title_tokens and all(t.lower() in stopwords for t in raw_title_tokens):
            raw_stopword_dominated += 1

        loc_dist = Counter((blocks[ii].get("source_locale", "und") or "und") for ii in idxs)
        dominant_locale = loc_dist.most_common(1)[0][0] if loc_dist else "ru"

        title_guess = _title_guess(raw_keywords, ci, dominant_locale, stopwords)
        final_title_tokens = [x.strip().lower() for x in title_guess.split(",")[:3] if x.strip()]
        if final_title_tokens and all(t in stopwords for t in final_title_tokens):
            final_stopword_dominated += 1
            if len(bad_titles) < 10:
                bad_titles.append(title_guess)
        elif len(good_titles) < 10:
            good_titles.append(title_guess)

        dists = []
        for ii in idxs:
            row = mat[ii].toarray()[0]
            dist = np.linalg.norm(row - centers[ci])
            dists.append((dist, ii))
        rep = [blocks[ii]["block_id"] for _, ii in sorted(dists)[:5]]
        all_ids = [blocks[ii]["block_id"] for ii in idxs][:200]

        concept_id = f"cpt_{cfg.run_id}_{ci}"
        out.append(
            {
                "concept_id": concept_id,
                "run_id": cfg.run_id,
                "source_run_id": read_run_id,
                "title_guess": title_guess,
                "top_keywords": filtered_keywords[:20] or raw_keywords[:20],
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
        "sample_bad_titles": bad_titles,
        "sample_good_titles": good_titles,
    }
    Path("reports/concepts_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
