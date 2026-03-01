from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from ..common.ids import canonical_hash
from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many


def _pick_locale(refs):
    cnt = Counter((r.get("source_locale", "und") or "und").lower() for r in refs)
    if not cnt:
        return "und"
    top = cnt.most_common(1)[0][0]
    if top.startswith("ru"):
        return "ru"
    if top.startswith("pt"):
        return "pt"
    if top.startswith("sw"):
        return "sw"
    return "und"


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    parts = [x.strip() for x in text.replace("\n", " ").split(".") if x.strip()]
    return parts[0][:260] if parts else text[:260]


def _mk_questions(locale: str, keywords: list[str], seed: str) -> list[str]:
    top = keywords[:5] or [seed]
    out = []
    if locale == "ru":
        tmpls = [
            "{k} у собаки: что делать?",
            "{k} у кошки: что делать?",
            "красные флаги при {k}",
            "диагностика при {k}",
            "возможные причины {k}",
            "как понять, что при {k} нужно срочно в клинику?",
            "что нельзя делать при {k}?",
            "первые шаги владельца при {k}",
        ]
    elif locale == "pt":
        tmpls = [
            "{k} em cães: o que fazer?",
            "{k} em gatos: o que fazer?",
            "sinais de alerta em {k}",
            "diagnóstico para {k}",
            "possíveis causas de {k}",
        ]
    elif locale == "sw":
        tmpls = [
            "{k} kwa mbwa: nifanye nini?",
            "{k} kwa paka: nifanye nini?",
            "dalili hatari za {k}",
            "uchunguzi wa {k}",
            "sababu zinazowezekana za {k}",
        ]
    else:
        tmpls = [
            "{k} in dogs: what to do?",
            "{k} in cats: what to do?",
            "red flags for {k}",
            "diagnostics for {k}",
            "possible causes of {k}",
            "when does {k} require urgent vet care?",
            "what to avoid with {k}?",
            "first owner actions for {k}",
        ]
    for k in top:
        for t in tmpls:
            out.append(t.format(k=k))
            if len(out) >= 15:
                return out
    return out[:15]


def _aggregate_refs(refs):
    seen = set()
    out = []
    for r in refs:
        key = (r.get("source_doc_id"), r.get("block_id"), r.get("text_hash"))
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "source_doc_id": r.get("source_doc_id"),
                "title": r.get("title"),
                "snippet_hash": r.get("text_hash"),
                "source_locale": r.get("source_locale", "ru"),
            }
        )
        if len(out) >= 100:
            break
    return out


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    parts = [x.strip() for x in text.replace("\n", " ").split(".") if x.strip()]
    return parts[0][:260] if parts else text[:260]


def _mk_questions(locale: str, keywords: list[str], seed: str) -> list[str]:
    top = keywords[:5] or [seed]
    out = []
    if locale == "ru":
        tmpls = [
            "{k} у собаки: что делать?",
            "{k} у кошки: что делать?",
            "красные флаги при {k}",
            "диагностика при {k}",
            "возможные причины {k}",
            "как понять, что при {k} нужно срочно в клинику?",
            "что нельзя делать при {k}?",
            "первые шаги владельца при {k}",
        ]
    else:
        tmpls = [
            "{k} in dogs: what to do?",
            "{k} in cats: what to do?",
            "red flags for {k}",
            "diagnostics for {k}",
            "possible causes of {k}",
            "when does {k} require urgent vet care?",
            "what to avoid with {k}?",
            "first owner actions for {k}",
        ]
    for k in top:
        for t in tmpls:
            out.append(t.format(k=k))
            if len(out) >= 15:
                return out
    return out[:15]


def _aggregate_refs(refs):
    seen = set()
    out = []
    for r in refs:
        key = (r.get("source_doc_id"), r.get("block_id"), r.get("text_hash"))
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "source_doc_id": r.get("source_doc_id"),
                "title": r.get("title"),
                "snippet_hash": r.get("text_hash"),
                "source_locale": r.get("source_locale", "ru"),
            }
        )
        if len(out) >= 100:
            break
    return out


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    read_run_id = cfg.active_run_id or cfg.run_id

    concepts = list(wdb["kb_concepts"].find({"run_id": read_run_id}))
    atoms = list(wdb["kb_atoms"].find({"run_id": read_run_id}))
    blocks_by_id = {b["block_id"]: b for b in wdb["evidence_blocks"].find({"run_id": read_run_id}, {"block_id": 1, "text": 1})}

    atoms_by_concept = defaultdict(list)
    for a in atoms:
        atoms_by_concept[a["concept_id"]].append(a)

    now = datetime.now(timezone.utc).isoformat()
    out = []
    sample = []
    for c in concepts:
        carr = atoms_by_concept.get(c["concept_id"], [])
        by_type = defaultdict(list)
        refs = []
        for a in carr:
            by_type[a["atom_type"]].append(a)
            refs.extend(a.get("source_refs", []))

        locale = _pick_locale(refs)
        keywords = list(dict.fromkeys((c.get("top_keywords", []) + [a["text"].split(" ")[0] for a in carr if a.get("text")])))[:30]
        seed = keywords[0] if keywords else c.get("title_guess", "состояние")
        questions = _mk_questions(locale, keywords, seed)

        rep_text = ""
        rep_ids = c.get("rep_block_ids", [])
        if rep_ids:
            rep_text = (blocks_by_id.get(rep_ids[0]) or {}).get("text", "")

        b2c_summary = " ".join([a["text"] for a in (by_type["owner_action"] + by_type["note_limitation"])[:3]])[:600]
        if not b2c_summary:
            b2c_summary = _first_sentence(rep_text)

        b2b_summary = " ".join([a["text"] for a in (by_type["diagnostic_step"] + by_type["note_limitation"])[:4]])[:700]
        if not b2b_summary:
            b2b_summary = _first_sentence(rep_text)

        b2c_content = {
            "summary": b2c_summary,
            "what_you_can_do_now": [a["text"] for a in (by_type["owner_action"] + by_type["triage_step"])[:5]],
            "red_flags": [a["text"] for a in by_type["red_flag"][:5]],
            "when_to_visit_vet": "urgent evaluation" if by_type["red_flag"] else "if persists/worsens",
            "what_to_avoid": ["Не давайте человеческие лекарства без назначения.", "Не откладывайте визит при ухудшении."],
        }
        b2b_content = {
            "summary": b2b_summary,
            "differentials": [{"name": a["text"][:120], "rationale": "", "notes": ""} for a in by_type["differential"][:8]],
            "diagnostic_steps": [{"step": a["text"][:160], "purpose": "", "notes": ""} for a in by_type["diagnostic_step"][:8]],
            "red_flags": [a["text"] for a in by_type["red_flag"][:8]],
            "triage_notes": " ".join(a["text"] for a in by_type["triage_step"][:3])[:300],
        }

        agg_refs = _aggregate_refs(refs)
        included = [a["atom_id"] for a in carr][:200]
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
                "questions": questions,
                "keywords": keywords,
                "content": content,
                "included_atoms": included,
                "source_refs": agg_refs,
                "status": "draft",
                "version": 1,
                "build_hash": canonical_hash({"content": content, "included_atoms": included}),
                "build_meta": {
                    "run_id": cfg.run_id,
                    "method": "rule_based_v1",
                    "locale_rule": "ru_if_80pct",
                    "created_at": now,
                },
                "created_at": now,
            }
            out.append(unit)
            if len(sample) < 10:
                sample.append(unit)

    safe_upsert_many(wdb["qa_units"], out, "qa_unit_id", cfg.run_id, dry_run=cfg.dry_run)
    Path("reports/qa_units_summary.md").write_text("# QA Units\n\nTotal: %d" % len(out), encoding="utf-8")
    Path("reports/qa_units_sample.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
