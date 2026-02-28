from __future__ import annotations

import json
from pathlib import Path
from statistics import median

from ..common.mongo import safe_insert_one


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db

    inv = list(wdb["inv_inventory"].find({"run_id": cfg.run_id}))
    blocks = list(wdb["evidence_blocks"].find({"run_id": cfg.run_id}))
    concepts = list(wdb["kb_concepts"].find({"run_id": cfg.run_id}))
    atoms = list(wdb["kb_atoms"].find({"run_id": cfg.run_id}))
    qa = list(wdb["qa_units"].find({"run_id": cfg.run_id}))
    dedups = list(wdb["dedup_groups"].find({"run_id": cfg.run_id}))
    qeval = wdb["qa_eval"].find_one({"run_id": cfg.run_id}) or {}

    atom_by_type = {}
    for a in atoms:
        atom_by_type[a["atom_type"]] = atom_by_type.get(a["atom_type"], 0) + 1

    locale_dist = {}
    for b in blocks:
        k = b.get("source_locale", "ru") or "ru"
        locale_dist[k] = locale_dist.get(k, 0) + 1

    concept_blocks = [c.get("block_count", 0) for c in concepts] or [0]
    atom_dedup_groups = [d for d in dedups if d.get("dedup_type") == "atom"]
    dedup_rate = len(atom_dedup_groups) / (len(atoms) or 1)

    gaps = {
        "concepts_zero_red_flags": [
            c["concept_id"]
            for c in concepts
            if not list(wdb["kb_atoms"].find({"run_id": cfg.run_id, "concept_id": c["concept_id"], "atom_type": "red_flag"}, {"_id": 1}).limit(1))
        ],
        "concepts_zero_diagnostic_steps": [
            c["concept_id"]
            for c in concepts
            if not list(wdb["kb_atoms"].find({"run_id": cfg.run_id, "concept_id": c["concept_id"], "atom_type": "diagnostic_step"}, {"_id": 1}).limit(1))
        ],
        "concepts_low_evidence": [c["concept_id"] for c in concepts if c.get("block_count", 0) < 5],
        "concepts_high_dup_ratio": [
            c["concept_id"]
            for c in concepts
            if len(list(wdb["dedup_groups"].find({"run_id": cfg.run_id, "dedup_type": "atom", "members.1": {"$exists": True}}).limit(1))) > 0
        ],
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
        "qa_units_by_variant": {
            "b2c_simple": len([x for x in qa if x.get("audience") == "b2c" and x.get("tone") == "simple"]),
            "b2b_pro": len([x for x in qa if x.get("audience") == "b2b" and x.get("tone") == "pro"]),
        },
    }

    Path("reports/coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/coverage.md").write_text("# Coverage\n\n" + "\n".join([f"- {k}: {v}" for k, v in coverage.items() if k != "atoms_by_type"]), encoding="utf-8")
    Path("reports/gaps.json").write_text(json.dumps(gaps, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/gaps.md").write_text("# Gaps\n\n" + "\n".join([f"- {k}: {len(v)}" for k, v in gaps.items()]), encoding="utf-8")

    final = {
        "run_id": cfg.run_id,
        "configs": cfg.to_dict(),
        "coverage": coverage,
        "gaps": gaps,
        "retrieval_eval": qeval,
        "recommendations": [
            "Добавить RU лемматизацию для улучшения кластеризации.",
            "Добавить более глубокий парсинг структурированных полей.",
            "Рассмотреть embeddings-подход на следующей итерации.",
        ],
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
        f"- collections inventoried: {coverage['source_collections']}\n"
        f"- evidence blocks: {coverage['evidence_blocks']}\n"
        f"- concepts: {coverage['concepts']}\n"
        f"- atoms: {coverage['atoms_total']}\n"
        f"- qa units: {coverage['qa_units_total']}\n",
        encoding="utf-8",
    )

    safe_insert_one(wdb["run_reports"], final, dry_run=cfg.dry_run)
