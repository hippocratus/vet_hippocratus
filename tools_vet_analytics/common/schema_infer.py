from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median
from typing import Any, Dict, List, Tuple


def _type_of(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "other"


def flatten_paths(doc: Dict[str, Any], max_depth: int = 3, prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in doc.items():
        path = f"{prefix}.{k}" if prefix else k
        out[path] = v
        if max_depth > 1 and isinstance(v, dict):
            out.update(flatten_paths(v, max_depth=max_depth - 1, prefix=path))
    return out


def infer_schema_profile(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(samples)
    if total == 0:
        return {"field_profiles": {}, "content_fields": [], "language_fields": [], "title_fields": []}

    field_profiles: Dict[str, Dict[str, Any]] = {}
    lengths: Dict[str, List[int]] = defaultdict(list)

    flat_samples = [flatten_paths(s, max_depth=3) for s in samples]
    all_paths = sorted({p for fs in flat_samples for p in fs.keys()})

    for p in all_paths:
        type_counter = Counter()
        missing = null = empty_string = empty_array = 0
        for fs in flat_samples:
            if p not in fs:
                missing += 1
                type_counter["missing"] += 1
                continue
            val = fs[p]
            t = _type_of(val)
            type_counter[t] += 1
            if val is None:
                null += 1
            if isinstance(val, str):
                if val.strip() == "":
                    empty_string += 1
                else:
                    lengths[p].append(len(val))
            if isinstance(val, list) and len(val) == 0:
                empty_array += 1
        lens = sorted(lengths.get(p, []))
        p50 = median(lens) if lens else 0
        p95 = lens[int(max(0, min(len(lens) - 1, round(0.95 * (len(lens) - 1)))))] if lens else 0
        field_profiles[p] = {
            "type_distribution": dict(type_counter),
            "missing_pct": missing / total,
            "null_pct": null / total,
            "empty_string_pct": empty_string / total,
            "empty_array_pct": empty_array / total,
            "avg_length": (sum(lens) / len(lens)) if lens else 0,
            "p50_length": p50,
            "p95_length": p95,
            "coverage_pct": 1 - (missing / total),
        }

    language_candidates = {"language", "lang", "locale", "output_locale", "source_locale"}
    title_candidates = {"title", "name", "filename", "doc_title"}
    content_candidates = {"content", "text", "body", "answer", "message"}

    language_fields = [p for p in all_paths if p.split(".")[-1].lower() in language_candidates]
    title_fields = [p for p in all_paths if p.split(".")[-1].lower() in title_candidates]

    content_fields: List[Tuple[str, float]] = []
    for p in all_paths:
        leaf = p.split(".")[-1].lower()
        prof = field_profiles[p]
        if prof["type_distribution"].get("string", 0) > 0 and (
            leaf in content_candidates or prof["avg_length"] > 250
        ):
            content_fields.append((p, prof["avg_length"]))
    content_fields.sort(key=lambda x: x[1], reverse=True)

    return {
        "field_profiles": field_profiles,
        "content_fields": [p for p, _ in content_fields],
        "language_fields": language_fields,
        "title_fields": title_fields,
    }
