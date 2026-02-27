from __future__ import annotations

import json
import random
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from ..common.mongo import safe_insert_one
from ..common.tfidf import build_tfidf


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    units = list(wdb["qa_units"].find({"run_id": cfg.run_id}))
    if not units:
        return

    docs = [" ".join([u.get("title", ""), " ".join(u.get("questions", [])), " ".join(u.get("keywords", []))]) for u in units]
    vec, mat = build_tfidf(docs, max_features=10000)

    queries = [q for u in units for q in u.get("questions", [])]
    random.seed(42)
    random.shuffle(queries)
    queries = queries[: min(100, max(50, len(queries)))]
    qmat = vec.transform(queries)
    sims = cosine_similarity(qmat, mat)

    top1_scores = []
    near_dup_hits = 0
    examples = []
    for qi, q in enumerate(queries):
        order = sims[qi].argsort()[::-1][:5]
        top1 = sims[qi, order[0]] if len(order) else 0
        top1_scores.append(float(top1))
        if len(order) > 1 and sims[qi, order[1]] >= 0.9:
            near_dup_hits += 1
        if len(examples) < 10 and len(order) > 1:
            u1 = units[order[0]]
            u2 = units[order[1]]
            summary1 = (u1.get("content", {}).get("summary") or "")[:200]
            summary2 = (u2.get("content", {}).get("summary") or "")[:200]
            examples.append({"query": q, "concept_id_1": u1["concept_id"], "concept_id_2": u2["concept_id"], "summary1": summary1, "summary2": summary2})

    eval_doc = {
        "run_id": cfg.run_id,
        "query_count": len(queries),
        "avg_top1_similarity": sum(top1_scores) / (len(top1_scores) or 1),
        "near_duplicate_top_hits_rate": near_dup_hits / (len(queries) or 1),
        "almost_identical_examples": examples,
    }
    safe_insert_one(wdb["qa_eval"], eval_doc, dry_run=cfg.dry_run)
    Path("reports/retrieval_eval.json").write_text(json.dumps(eval_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("reports/retrieval_eval.md").write_text(
        "# Retrieval Eval\n\n"
        + f"- queries: {eval_doc['query_count']}\n"
        + f"- avg top1 similarity: {eval_doc['avg_top1_similarity']:.4f}\n"
        + f"- near-duplicate top hits rate: {eval_doc['near_duplicate_top_hits_rate']:.2%}\n",
        encoding="utf-8",
    )
