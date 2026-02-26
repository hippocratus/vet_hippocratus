from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from pymongo import MongoClient
from pymongo.collection import Collection


@dataclass
class MongoBundle:
    read_client: MongoClient
    write_client: MongoClient
    read_db: Any
    write_db: Any


REQUIRED_WRITE_DB = "vet_analytics"


def connect_mongo(uri_read: str, uri_write: str, db_read: str, db_write: str) -> MongoBundle:
    read_client = MongoClient(uri_read)
    write_client = MongoClient(uri_write)
    read_db_obj = read_client[db_read]
    write_db_obj = write_client[db_write]
    if db_write != REQUIRED_WRITE_DB:
        raise RuntimeError(f"Write DB must be {REQUIRED_WRITE_DB}, got {db_write}")
    return MongoBundle(read_client, write_client, read_db_obj, write_db_obj)


def assert_safe_write_target(collection: Collection) -> None:
    db_name = collection.database.name
    if db_name != REQUIRED_WRITE_DB:
        raise RuntimeError(f"Refusing to write outside {REQUIRED_WRITE_DB}: {db_name}")


def safe_upsert_many(
    collection: Collection,
    docs: Iterable[Dict[str, Any]],
    key_field: str,
    run_id: str,
    dry_run: bool = False,
) -> int:
    assert_safe_write_target(collection)
    n = 0
    if dry_run:
        return sum(1 for _ in docs)
    for doc in docs:
        key_val = doc.get(key_field)
        if key_val is None:
            continue
        filter_query = {key_field: key_val, "run_id": run_id}
        collection.update_one(filter_query, {"$set": doc}, upsert=True)
        n += 1
    return n


def safe_insert_one(collection: Collection, doc: Dict[str, Any], dry_run: bool = False) -> Optional[Any]:
    assert_safe_write_target(collection)
    if dry_run:
        return None
    return collection.insert_one(doc)
