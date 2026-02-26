from __future__ import annotations

import regex as re


def normalize_ru_text(text: str) -> str:
    t = (text or "").lower().replace("ё", "е")
    t = re.sub(r"[\t\r\f\v]+", " ", t)
    t = re.sub(r"([!?.,;:])\1{1,}", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^страница\s+\d+\s*$", "", t, flags=re.I)
    return t


def split_chunks(text: str, chunk_size: int = 1500, overlap: int = 250):
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(end - overlap, start + 1)
    return chunks
