# Vet Analytics Toolkit

RU/PT/SW analytics pipeline that reads from `vet_database` and writes only to `vet_analytics`.

## Mongo URI (GitHub Actions)

Use:

`mongodb+srv://<user>:<pass>@hipocratus.o6syp.mongodb.net/?authSource=admin&appName=Hipocratus`

If only `MONGODB_URI` is provided, pipeline uses it for both read/write clients while still enforcing DB separation (`vet_database` read, `vet_analytics` write). You can also provide split secrets `MONGO_URI_READ` and `MONGO_URI_WRITE`.

## Run

```bash
python -m tools_vet_analytics.run_all \
  --sample-per-collection 200 \
  --chunk-size-chars 1500 \
  --overlap-chars 250 \
  --k-clusters 50
```

## Rebuild existing run safely

```bash
python -m tools_vet_analytics.run_all \
  --run-id 97e32a35-415d-4b06-987a-2acbd362b7a7 \
  --allow-overwrite-run \
  --from-step 4 --to-step 8
```

To rebuild concepts/atoms/qa_units for an existing run_id, pass `--run-id <existing>`.

## Locale runs

```bash
python -m tools_vet_analytics.run_all --include-locales ru
python -m tools_vet_analytics.run_all --include-locales pt,pt-br
python -m tools_vet_analytics.run_all --include-locales sw
```

Locale matching is prefix-based (`sw` matches `sw-ke`, `sw-tz`).

## Dashboard export

```bash
python -m tools_vet_analytics.export_dashboard_data --out reports/dashboard_data.json --limit-runs 10
```

Open `hipocratus_pipeline_dashboard.html` locally; it reads `reports/dashboard_data.json` using `fetch()`.

## Safety

- Read operations use `MONGO_URI_READ` + `MONGO_DB_READ`.
- Write operations are guarded to allow only DB `vet_analytics`.
- Existing run IDs are never overwritten unless `--allow-overwrite-run` is passed.
- Pipeline uses deterministic IDs and upserts for idempotent reruns.
