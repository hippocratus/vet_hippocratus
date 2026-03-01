from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS_DIR = Path(__file__).with_name("stopwords")


@lru_cache(maxsize=1)
def load_stopwords_by_locale() -> dict[str, frozenset[str]]:
    out: dict[str, frozenset[str]] = {}
    if not STOPWORDS_DIR.exists():
        return out
    for fp in STOPWORDS_DIR.glob("*.txt"):
        locale = fp.stem.lower()
        words = {
            ln.strip().lower()
            for ln in fp.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        }
        out[locale] = frozenset(words)
    return out


def get_stopwords_for_locales(locales: Optional[Iterable[str]] = None) -> list[str]:
    by_loc = load_stopwords_by_locale()
    if not locales:
        merged = set()
        for vals in by_loc.values():
            merged.update(vals)
        return sorted(merged)

    merged = set()
    for loc in locales:
        key = (loc or "").lower().split("-")[0]
        if key in by_loc:
            merged.update(by_loc[key])
    return sorted(merged)


def stopword_hit_count(text: str, locale: str) -> int:
    words = load_stopwords_by_locale().get(locale.lower().split("-")[0], frozenset())
    tokens = [t.strip().lower() for t in (text or "").split()]
    return sum(1 for t in tokens if t in words)


def build_tfidf(
    texts: List[str],
    max_features: int = 30000,
    use_stopwords: bool = True,
    locales: Optional[Iterable[str]] = None,
):
    vec = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_features=max_features,
        token_pattern=r"(?u)\b[^\W\d_]{2,}\b",
        stop_words=get_stopwords_for_locales(locales) if use_stopwords else None,
    )
    mat = vec.fit_transform(texts)
    return vec, mat


def top_terms_for_row(vec: TfidfVectorizer, row, top_n: int = 20) -> List[Tuple[str, float]]:
    if row.nnz == 0:
        return []
    arr = row.toarray()[0]
    idx = arr.argsort()[::-1][:top_n]
    feats = vec.get_feature_names_out()
    return [(feats[i], float(arr[i])) for i in idx if arr[i] > 0]
