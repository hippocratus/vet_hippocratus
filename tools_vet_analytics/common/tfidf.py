from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


@lru_cache(maxsize=1)
def load_ru_stopwords() -> frozenset[str]:
    path = Path(__file__).with_name("stopwords_ru.txt")
    if not path.exists():
        return frozenset()
    words = {ln.strip().lower() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")}
    return frozenset(words)


def build_tfidf(texts: List[str], max_features: int = 30000, use_stopwords: bool = True):
    vec = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_features=max_features,
        token_pattern=r"(?u)\b[а-яА-Яa-zA-Z]{2,}\b",
        stop_words=list(load_ru_stopwords()) if use_stopwords else None,
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
