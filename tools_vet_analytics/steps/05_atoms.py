from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import regex as re
from sklearn.metrics.pairwise import cosine_similarity

from ..common.hashing import sha1_text
from ..common.mongo import safe_upsert_many
from ..common.normalize import normalize_ru_text
from ..common.tfidf import build_tfidf

RUS_HEADINGS = {"симптомы", "диагностика", "лечение", "неотложно", "опасно", "причины"}

DIAG_RE = re.compile(
    r"(диагност|обследован|анализ крови|общий анализ|биохими|рентген|узи|ультразвук|пункц|мазок|посев|пцр|температур|пальпац|осмотр|анамнез|"
    r"diagn[oó]st|exame|raio[- ]?x|ultrassom|hemograma|teste|an[aá]lise|"
    r"uchunguzi|vipimo|damu|x[- ]?ray|ultrasound|joto|historia)",
    re.I,
)
RED_FLAG_RE = re.compile(
    r"(срочно|неотложно|немедленно|экстренно|судорог|коллапс|кров|вздут|неукротим|шок|острая боль|не дышит|синюшност|"
    r"urgente|emerg[êe]n|convuls|colapso|sangr|choque|dor aguda|"
    r"haraka|dharura|degedege|mshtuko|damu|ha[p]?umui)",
    re.I,
)
TRIAGE_RE = re.compile(
    r"(покой|огранич|не кормить|поить|наблюдать|изоляц|в клинику|"
    r"repouso|limitar|n[aã]o alimentar|hidratar|observar|isolar|cl[ií]nica|"
    r"pumzika|punguza|usipe chakula|mpe maji|fuatilia|tenga|kwenda kliniki)",
    re.I,
)



def _split_lines(text: str):
    lines = [ln.strip(" -*•\t") for ln in text.splitlines() if ln.strip()]
    out = []
    for ln in lines:
        if re.match(r"^(\d+[\).]|[-*•])\s+", ln):
            out.append(ln)
        elif ln.endswith(":") or ln.lower() in RUS_HEADINGS:
            out.append(ln)
        elif len(ln) > 20:
            out.append(ln)
    return out


def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text or "")
    return [c.strip() for c in chunks if c and c.strip()]


def _trim_sentence(s: str, max_len: int = 180) -> str:
    return s.strip()[:max_len]


def _make_atom(concept_id: str, atom_type: str, text: str, b, cfg, read_run_id: str, now: str):
    nln = normalize_ru_text(text)
    atom_id = sha1_text(f"{concept_id}|{atom_type}|{nln}")
    return {
        "atom_id": atom_id,
        "run_id": cfg.run_id,
        "source_run_id": read_run_id,
        "concept_id": concept_id,
        "atom_type": atom_type,
        "text": text[:500],
        "norm_hash": sha1_text(nln),
        "source_refs": [
            {
                "source_doc_id": b["source_doc_id"],
                "block_id": b["block_id"],
                "text_hash": b["text_hash"],
                "title": b.get("title"),
                "source_locale": b.get("source_locale", "ru"),
            }
        ],
        "status": "draft",
        "created_at": now,
    }


def run(ctx):
    cfg = ctx["config"]
    wdb = ctx["mongo"].write_db
    cues = json.loads(Path("tools_vet_analytics/common/cues.json").read_text(encoding="utf-8"))
    read_run_id = cfg.active_run_id or cfg.run_id

    concepts = list(wdb["kb_concepts"].find({"run_id": read_run_id}))
    blocks_by_id = {b["block_id"]: b for b in wdb["evidence_blocks"].find({"run_id": read_run_id})}
    atoms = []
    by_type = defaultdict(list)
    now = datetime.now(timezone.utc).isoformat()

    for c in concepts:
        concept_atoms = []
        block_ids = (c.get("block_ids") or c.get("rep_block_ids") or [])[:200]
        for bid in block_ids:
            b = blocks_by_id.get(bid)
            if not b:
                continue
            text = b.get("text", "")

            for ln in _split_lines(text):
                nln = normalize_ru_text(ln)
                matched_types = [t for t, cue_list in cues.items() if any(cu in nln for cu in cue_list)]
                for atom_type in matched_types:
                    concept_atoms.append(_make_atom(c["concept_id"], atom_type, ln, b, cfg, read_run_id, now))

        # sentence fallback only if missing critical types
        present = {a["atom_type"] for a in concept_atoms}
        needs_diag = "diagnostic_step" not in present
        needs_red = "red_flag" not in present
        if needs_diag or needs_red:
            added = {"diagnostic_step": 0, "red_flag": 0, "triage_step": 0}
            seen = set()
            for bid in block_ids:
                b = blocks_by_id.get(bid)
                if not b:
                    continue
                for sent in _split_sentences(b.get("text", "")):
                    if len(sent.split()) < 6:
                        continue
                    item = _trim_sentence(sent)
                    key_norm = normalize_ru_text(item)
                    if DIAG_RE.search(item) and needs_diag and added["diagnostic_step"] < 30:
                        hk = sha1_text(f"diagnostic_step|{key_norm}")
                        if hk not in seen:
                            seen.add(hk)
                            concept_atoms.append(_make_atom(c["concept_id"], "diagnostic_step", item, b, cfg, read_run_id, now))
                            added["diagnostic_step"] += 1
                    if RED_FLAG_RE.search(item) and needs_red and added["red_flag"] < 30:
                        hk = sha1_text(f"red_flag|{key_norm}")
                        if hk not in seen:
                            seen.add(hk)
                            concept_atoms.append(_make_atom(c["concept_id"], "red_flag", item, b, cfg, read_run_id, now))
                            added["red_flag"] += 1
                    if TRIAGE_RE.search(item) and added["triage_step"] < 30:
                        hk = sha1_text(f"triage_step|{key_norm}")
                        if hk not in seen:
                            seen.add(hk)
                            concept_atoms.append(_make_atom(c["concept_id"], "triage_step", item, b, cfg, read_run_id, now))
                            added["triage_step"] += 1

        for atom in concept_atoms:
            atoms.append(atom)
            by_type[atom["atom_type"]].append(atom)

    safe_upsert_many(wdb["kb_atoms"], atoms, "atom_id", cfg.run_id, dry_run=cfg.dry_run)

    dedup_docs = []
    for t, arr in by_type.items():
        groups = defaultdict(list)
        for a in arr:
            groups[a["norm_hash"]].append(a)
        for h, members in groups.items():
            gid = sha1_text(f"exact|{t}|{h}")
            dedup_docs.append(
                {
                    "dedup_id": f"atom_exact::{gid}",
                    "run_id": cfg.run_id,
                    "source_run_id": read_run_id,
                    "dedup_type": "atom",
                    "atom_type": t,
                    "group_id": gid,
                    "representative_atom_id": members[0]["atom_id"],
                    "members": [m["atom_id"] for m in members][:100],
                    "method": "exact",
                    "created_at": now,
                }
            )

        texts = [a["text"] for a in arr]
        if len(texts) > 1:
            _, mat = build_tfidf(texts, max_features=5000)
            sim = cosine_similarity(mat)
            used = set()
            for i in range(len(arr)):
                if i in used:
                    continue
                near = [j for j in range(len(arr)) if i != j and sim[i, j] >= 0.9]
                if near:
                    mem = [arr[i]["atom_id"]] + [arr[j]["atom_id"] for j in near]
                    used.update([i] + near)
                    gid = sha1_text(f"near|{t}|{'|'.join(sorted(mem))}")
                    dedup_docs.append(
                        {
                            "dedup_id": f"atom_near::{gid}",
                            "run_id": cfg.run_id,
                            "source_run_id": read_run_id,
                            "dedup_type": "atom",
                            "atom_type": t,
                            "group_id": gid,
                            "representative_atom_id": arr[i]["atom_id"],
                            "members": mem[:100],
                            "method": "near_tfidf_0.9",
                            "created_at": now,
                        }
                    )

    safe_upsert_many(wdb["dedup_groups"], dedup_docs, "dedup_id", cfg.run_id, dry_run=cfg.dry_run)

    summary = {
        "atoms_total": len(atoms),
        "by_type": {k: len(v) for k, v in by_type.items()},
        "dedup_groups": len(dedup_docs),
        "source_run_id": read_run_id,
    }
    Path("reports/atoms_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    Path("reports/atoms_summary.md").write_text("# Atoms\n\n" + "\n".join([f"- {k}: {v}" for k, v in summary["by_type"].items()]), encoding="utf-8")
