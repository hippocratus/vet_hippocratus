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
    read_run_id = cfg.active_run_id or cfg.run_id
    units = list(wdb["qa_units"].find({"run_id": read_run_id}))
    if not units:
        return

    docs = [" ".join([u.get("title", ""), " ".join(u.get("questions", [])), " ".join(u.get("keywords", []))]) for u in units]
    vec, mat = build_tfidf(docs, max_features=10000)

    queries = [q for u in units for q in u.get("questions", [])]
    random.seed(42)
    random.shuffle(queries)
    if len(queries) > 100:
        queries = queries[:100]

    qmat = vec.transform(queries)
    sims = cosine_similarity(qmat, mat)

    top1_scores = []
    near_dup_hits = 0
    examples = []
    for qi, q in enumerate(queries):
        order = sims[qi].argsort()[::-1][:5]
        if not len(order):
            continue
        top1 = float(sims[qi, order[0]])
        top1_scores.append(top1)
        if len(order) > 1 and sims[qi, order[1]] >= 0.9:
            near_dup_hits += 1

        cand_units = [units[idx] for idx in order]
        sum_texts = [(u.get("content", {}).get("summary") or "")[:240] for u in cand_units]
        if len(sum_texts) > 1 and len(examples) < 10:
            svec, smat = build_tfidf(sum_texts, max_features=3000)
            ssim = cosine_similarity(smat)
            found = False
            for i in range(len(sum_texts)):
                for j in range(i + 1, len(sum_texts)):
                    if ssim[i, j] >= 0.9:
                        examples.append(
                            {
                                "query": q,
                                "concept_id_1": str(cand_units[i].get("concept_id") or cand_units[i].get("_id")),
                                "concept_id_2": str(cand_units[j].get("concept_id") or cand_units[j].get("_id")),
                                "summary1": sum_texts[i],
                                "summary2": sum_texts[j],
                                "summary_similarity": float(ssim[i, j]),
                            }
                        )
                        found = True
                        break
                if found:
                    break

    eval_doc = {
        "run_id": cfg.run_id,
        "query_count": len(queries),
        "avg_top1_similarity": sum(top1_scores) / (len(top1_scores) or 1),
        "near_duplicate_top_hits_rate": near_dup_hits / (len(queries) or 1),
        "almost_identical_examples": examples,
    }
    safe_insert_one(wdb["qa_eval"], eval_doc, dry_run=cfg.dry_run)
    Path("reports/retrieval_eval.json").write_text(json.dumps(eval_doc, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/retrieval_eval.md").write_text(
        "# Retrieval Eval\n\n"
        + f"- queries: {eval_doc['query_count']}\n"
        + f"- avg top1 similarity: {eval_doc['avg_top1_similarity']:.4f}\n"
        + f"- near-duplicate top hits rate: {eval_doc['near_duplicate_top_hits_rate']:.2%}\n"
        + f"- almost-identical examples: {len(examples)}\n",
        encoding="utf-8",
    )
