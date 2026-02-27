from __future__ import annotations

from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf(texts: List[str], max_features: int = 30000):
    vec = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_features=max_features,
        token_pattern=r"(?u)\b\w+\b",
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
