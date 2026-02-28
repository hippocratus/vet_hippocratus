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
- If local SRV DNS fails, the toolkit attempts DoH-based SRV/TXT resolution and retries with a direct `mongodb://host1,host2...` URI.

## Outputs

- Mongo collections in `vet_analytics`: inventory, dedup, evidence blocks, concepts, atoms, QA units, eval, run report.
- Local reports in `./reports/*.md` and `./reports/*.json`.


## Rebuild for an existing run

To rebuild concepts/atoms/qa_units for existing run_id, pass `--run-id <existing>` (and optional step bounds):

```bash
python -m tools_vet_analytics.run_all --run-id 97e32a35-415d-4b06-987a-2acbd362b7a7 --from-step 4 --to-step 8
```

For read-only reuse of previous intermediate outputs while writing a new run, pass `--active-run-id <existing_run_id>`.
