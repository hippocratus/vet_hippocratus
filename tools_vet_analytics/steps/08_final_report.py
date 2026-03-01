from __future__ import annotations

import json
from pathlib import Path
from statistics import median

from ..common.mongo import safe_upsert_many
from ..common.tfidf import get_stopwords_for_locales


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    read_run_id = cfg.active_run_id or cfg.run_id

    inv = list(wdb["inv_inventory"].find({"run_id": read_run_id}))
    blocks = list(wdb["evidence_blocks"].find({"run_id": read_run_id}))
    concepts = list(wdb["kb_concepts"].find({"run_id": read_run_id}))
    atoms = list(wdb["kb_atoms"].find({"run_id": read_run_id}))
    qa = list(wdb["qa_units"].find({"run_id": read_run_id}))
    dedups = list(wdb["dedup_groups"].find({"run_id": read_run_id}))
    qeval = wdb["qa_eval"].find_one({"run_id": read_run_id}) or {}

    atom_by_type = {}
    for a in atoms:
        atom_by_type[a["atom_type"]] = atom_by_type.get(a["atom_type"], 0) + 1

    locale_dist = {}
    for b in blocks:
        k = b.get("source_locale", "und") or "und"
        locale_dist[k] = locale_dist.get(k, 0) + 1

    concept_blocks = [c.get("block_count", 0) for c in concepts] or [0]
    atom_dedup_groups = [d for d in dedups if d.get("dedup_type") == "atom"]
    dedup_rate = len(atom_dedup_groups) / (len(atoms) or 1)

    gaps = {
        "concepts_zero_red_flags": [
            c["concept_id"]
            for c in concepts
            if not list(
                wdb["kb_atoms"].find(
                    {"run_id": read_run_id, "concept_id": c["concept_id"], "atom_type": "red_flag"}, {"_id": 1}
                ).limit(1)
            )
        ],
        "concepts_zero_diagnostic_steps": [
            c["concept_id"]
            for c in concepts
            if not list(
                wdb["kb_atoms"].find(
                    {"run_id": read_run_id, "concept_id": c["concept_id"], "atom_type": "diagnostic_step"}, {"_id": 1}
                ).limit(1)
            )
        ],
        "concepts_low_evidence": [c["concept_id"] for c in concepts if c.get("block_count", 0) < 5],
    }

    stopwords = set(get_stopwords_for_locales(["ru", "pt", "sw"]))
    bad_titles = []
    good_titles = []
    for c in concepts:
        title = (c.get("title_guess") or "").strip()
        tokens = [t.strip().lower() for t in title.split(",") if t.strip()]
        all_stopword = bool(tokens) and all((len(t) < 3 or t in stopwords or t.isdigit()) for t in tokens)
        too_short = len(tokens) < 2
        if all_stopword or too_short:
            if len(bad_titles) < 10:
                bad_titles.append(title)
        elif len(good_titles) < 10:
            good_titles.append(title)

    title_stats = {
        "total_concepts": len(concepts),
        "stopword_only_titles_count": len(bad_titles),
        "pct_stopword_only_titles": (len(bad_titles) / (len(concepts) or 1)),
        "sample_bad_titles": bad_titles,
        "sample_good_titles": good_titles,
    }

    coverage = {
        "source_collections": len(inv),
        "evidence_blocks": len(blocks),
        "evidence_locale_distribution": locale_dist,
        "concepts": len(concepts),
        "concept_block_count_min": min(concept_blocks),
        "concept_block_count_median": median(concept_blocks),
        "concept_block_count_max": max(concept_blocks),
        "atoms_total": len(atoms),
        "atoms_by_type": atom_by_type,
        "atom_dedup_groups": len(atom_dedup_groups),
        "atom_dedup_rate": dedup_rate,
        "dedup_groups_total": len(dedups),
        "qa_units_total": len(qa),
    }

    Path("reports/coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/gaps.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    final = {
        "report_id": f"run::{cfg.run_id}",
        "run_id": cfg.run_id,
        "source_run_id": read_run_id,
        "configs": cfg.to_dict(),
        "coverage": coverage,
        "gaps": gaps,
        "title_stats": title_stats,
        "retrieval_eval": qeval,
        "report_paths": [
            "reports/inventory.md",
            "reports/dedup_raw_text.md",
            "reports/evidence_blocks.md",
            "reports/concepts_summary.md",
            "reports/atoms_summary.md",
            "reports/qa_units_summary.md",
            "reports/retrieval_eval.md",
            "reports/final_report.md",
        ],
        "warnings": ctx.get("warnings", []),
    }
    Path("reports/final_report.json").write_text(json.dumps(final, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/final_report.md").write_text(
        "# Final report\n\n"
        f"- run_id: {cfg.run_id}\n"
        f"- evidence blocks: {coverage['evidence_blocks']}\n"
        f"- concepts: {coverage['concepts']}\n"
        f"- atoms: {coverage['atoms_total']}\n"
        f"- qa units: {coverage['qa_units_total']}\n"
        f"- bad titles pct: {title_stats['pct_stopword_only_titles']:.2%}\n",
        encoding="utf-8",
    )

    safe_upsert_many(wdb["run_reports"], [final], "report_id", cfg.run_id, dry_run=cfg.dry_run)
