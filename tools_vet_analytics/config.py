from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class AnalyticsConfig:
    mongo_uri_read: str
    mongo_uri_write: str
    mongo_db_read: str = "vet_database"
    mongo_db_write: str = "vet_analytics"
    sample_per_collection: int = 200
    limit: int = 0
    chunk_size_chars: int = 1500
    overlap_chars: int = 250
    k_clusters: int = 50
    dry_run: bool = False
    resume: bool = False
    run_id: str = ""
    active_run_id: str = ""
    from_step: int = 1
    to_step: int = 8
    include_locales: List[str] | None = None
    allow_overwrite_run: bool = False
    recompute_titles_only: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["mongo_uri_read"] = "***"
        data["mongo_uri_write"] = "***"
        return data


def load_env_config() -> AnalyticsConfig:
    shared_uri = (
        os.environ.get("MONGODB_URI")
        or os.environ.get("MONGO_URI")
        or os.environ.get("MONGO_URL")
        or ""
    )
    read_uri = os.environ.get("MONGO_URI_READ") or shared_uri
    write_uri = os.environ.get("MONGO_URI_WRITE") or shared_uri
    if not read_uri or not write_uri:
        raise RuntimeError(
            "Set MONGO_URI_READ/MONGO_URI_WRITE or MONGODB_URI (or MONGO_URI). "
            "For GitHub Actions set repository secret MONGODB_URI."
        )

    return AnalyticsConfig(
        mongo_uri_read=read_uri,
        mongo_uri_write=write_uri,
        mongo_db_read=os.environ.get("MONGO_DB_READ", "vet_database"),
        mongo_db_write=os.environ.get("MONGO_DB_WRITE", "vet_analytics"),
    )
