from __future__ import annotations

import json
from typing import Any

from .hashing import sha1_text


def canonical_hash(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha1_text(s)
