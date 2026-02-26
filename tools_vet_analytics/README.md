# Vet Analytics Toolkit

RU-first analytics pipeline that reads from `vet_database` and writes only to `vet_analytics`.

## Run

```bash
python -m tools_vet_analytics.run_all \
  --sample-per-collection 200 \
  --chunk-size-chars 1500 \
  --overlap-chars 250 \
  --k-clusters 50
```

## Safety

- Read operations use `MONGO_URI_READ` + `MONGO_DB_READ`.
- Write operations are guarded to allow only DB `vet_analytics`.
- Pipeline uses deterministic IDs and upserts for idempotent reruns.
- SRV DNS resolution for `mongodb+srv://` requires `dnspython` (included in `requirements-analytics.txt`).

## Outputs

- Mongo collections in `vet_analytics`: inventory, dedup, evidence blocks, concepts, atoms, QA units, eval, run report.
- Local reports in `./reports/*.md` and `./reports/*.json`.
