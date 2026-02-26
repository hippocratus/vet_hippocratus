from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConfigurationError


@dataclass
class MongoBundle:
    read_client: MongoClient
    write_client: MongoClient
    read_db: Any
    write_db: Any


REQUIRED_WRITE_DB = "vet_analytics"


def _dns_json_resolve(name: str, rtype: str) -> Dict[str, Any]:
    url = f"https://dns.google/resolve?name={urllib.parse.quote(name)}&type={rtype}"
    with urllib.request.urlopen(url, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _srv_to_direct_uri(uri: str) -> str:
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "mongodb+srv":
        return uri

    base_host = parsed.hostname or ""
    if not base_host:
        return uri

    srv = _dns_json_resolve(f"_mongodb._tcp.{base_host}", "SRV")
    answers = srv.get("Answer", [])
    hosts: List[str] = []
    for ans in answers:
        parts = str(ans.get("data", "")).split()
        if len(parts) >= 4:
            hosts.append(parts[3].rstrip("."))
    hosts = sorted(set(hosts))
    if not hosts:
        return uri

    txt = _dns_json_resolve(base_host, "TXT")
    txt_answer = txt.get("Answer", [])
    txt_opts = ""
    if txt_answer:
        txt_opts = str(txt_answer[0].get("data", "")).strip('"')

    existing_q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    existing_keys = {k for k, _ in existing_q}

    merged = []
    if txt_opts:
        merged.extend(urllib.parse.parse_qsl(txt_opts, keep_blank_values=True))
    merged.extend(existing_q)

    if "tls" not in existing_keys and "ssl" not in existing_keys:
        merged.append(("tls", "true"))

    query = urllib.parse.urlencode(merged, doseq=True)

    user = ""
    if parsed.username is not None:
        u = urllib.parse.quote_plus(urllib.parse.unquote_plus(parsed.username))
        p = urllib.parse.quote_plus(urllib.parse.unquote_plus(parsed.password or ""))
        user = f"{u}:{p}@"

    return f"mongodb://{user}{','.join(hosts)}/?{query}"


def _make_client(uri: str) -> MongoClient:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        client.admin.command("ping")
        return client
    except ConfigurationError as exc:
        msg = str(exc).lower()
        if "dns query" in msg or "nxdomain" in msg:
            direct_uri = _srv_to_direct_uri(uri)
            if direct_uri != uri:
                client = MongoClient(direct_uri, serverSelectionTimeoutMS=10000)
                client.admin.command("ping")
                return client
        raise


def connect_mongo(uri_read: str, uri_write: str, db_read: str, db_write: str) -> MongoBundle:
    if db_write != REQUIRED_WRITE_DB:
        raise RuntimeError(f"Write DB must be {REQUIRED_WRITE_DB}, got {db_write}")

    read_client = _make_client(uri_read)
    write_client = _make_client(uri_write)
    read_db_obj = read_client[db_read]
    write_db_obj = write_client[db_write]
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
