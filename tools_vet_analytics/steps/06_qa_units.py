from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from ..common.ids import canonical_hash
from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many


def _pick_locale(concept, refs):
    cnt = Counter(r.get("source_locale", "ru") or "ru" for r in refs)
    total = sum(cnt.values()) or 1
    ru_share = (cnt.get("ru", 0) + cnt.get("unknown", 0)) / total
    return "ru" if ru_share >= 0.8 else "und"


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db

    concepts = list(wdb["kb_concepts"].find({"run_id": cfg.run_id}))
    atoms = list(wdb["kb_atoms"].find({"run_id": cfg.run_id}))
    atoms_by_concept = defaultdict(list)
    for a in atoms:
        atoms_by_concept[a["concept_id"]].append(a)

    out = []
    sample = []
    for c in concepts:
        carr = atoms_by_concept.get(c["concept_id"], [])
        by_type = defaultdict(list)
        refs = []
        for a in carr:
            by_type[a["atom_type"]].append(a)
            refs.extend(a.get("source_refs", []))

        locale = _pick_locale(c, refs)
        kw = list(dict.fromkeys((c.get("top_keywords", []) + [a["text"].split(" ")[0] for a in carr if a.get("text")]) ))[:30]
        seed = kw[0] if kw else c.get("title_guess", "состояние")
        if locale == "ru":
            questions = [
                f"{seed} у собаки: что делать?",
                f"{seed} у кошки: что делать?",
                f"красные флаги при {seed}",
                f"диагностика при {seed}",
                f"возможные причины {seed}",
            ]
        else:
            questions = [
                f"{seed} in dogs: what to do?", f"{seed} in cats: what to do?", f"red flags for {seed}", f"diagnostics for {seed}", f"possible causes of {seed}"
            ]

        b2c_content = {
            "summary": " ".join([a["text"] for a in (by_type["owner_action"] + by_type["note_limitation"])[:3]])[:600],
            "what_you_can_do_now": [a["text"] for a in (by_type["owner_action"] + by_type["triage_step"])[:5]],
            "red_flags": [a["text"] for a in by_type["red_flag"][:5]],
            "when_to_visit_vet": "urgent evaluation" if by_type["red_flag"] else "if persists/worsens",
            "what_to_avoid": ["Не давайте человеческие лекарства без назначения.", "Не откладывайте визит при ухудшении."]
        }
        b2b_content = {
            "summary": " ".join([a["text"] for a in (by_type["diagnostic_step"] + by_type["note_limitation"])[:4]])[:700],
            "differentials": [{"name": a["text"][:120], "rationale": "", "notes": ""} for a in by_type["differential"][:8]],
            "diagnostic_steps": [{"step": a["text"][:160], "purpose": "", "notes": ""} for a in by_type["diagnostic_step"][:8]],
            "red_flags": [a["text"] for a in by_type["red_flag"][:8]],
            "triage_notes": " ".join(a["text"] for a in by_type["triage_step"][:3])[:300],
        }

        for audience, tone, content in [("b2c", "simple", b2c_content), ("b2b", "pro", b2b_content)]:
            qa_unit_id = sha1_text(f"{c['concept_id']}|{locale}|{audience}|{tone}")
            unit = {
                "qa_unit_id": qa_unit_id,
                "run_id": cfg.run_id,
                "concept_id": c["concept_id"],
                "output_locale": locale,
                "audience": audience,
                "tone": tone,
                "title": c.get("title_guess"),
                "questions": questions[:15],
                "keywords": kw,
                "content": content,
                "included_atoms": [a["atom_id"] for a in carr][:200],
                "source_refs": refs[:100],
                "status": "draft",
                "version": 1,
                "build_hash": canonical_hash({"content": content, "included_atoms": [a["atom_id"] for a in carr][:200]}),
                "build_meta": {"run_id": cfg.run_id, "method": "rule_based_v1", "locale_rule": "ru_if_80pct"},
            }
            out.append(unit)
            if len(sample) < 10:
                sample.append(unit)

    safe_upsert_many(wdb["qa_units"], out, "qa_unit_id", cfg.run_id, dry_run=cfg.dry_run)
    Path("reports/qa_units_summary.md").write_text("# QA Units\n\nTotal: %d" % len(out), encoding="utf-8")
    Path("reports/qa_units_sample.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
