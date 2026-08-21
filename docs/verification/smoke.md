# Phase 10 smoke test

This smoke test is the VL-05 public read-only check for the Phase 10 launch gate. It checks the live API, canonical frontend, and legacy-host redirect contract without uploading a document or changing deployment state.

## Run

From the repository root, run:

```bash
bash scripts/check-launch.sh smoke
```

The command requires network access and `curl`. It does not require SSH access, Docker, deployment credentials, or a VPS shell. It exits non-zero on the first failed assertion.

## Coverage

The smoke mode verifies:

- `https://api.mypapyr.com/health` returns HTTP 200 with `status: "ok"`.
- `https://api.mypapyr.com/health/ready` returns HTTP 200 with `status: "ready"`.
- `https://api.mypapyr.com/api/v1/capabilities` returns HTTP 200 and includes `maxRetries` and `defaultTimeoutSeconds`.
- `https://budgezen.com/`, `/en`, `/sitemap.xml`, `/robots.txt`, and `/en/compress-pdf` return HTTP 200.
- `http://mypapyr.com/` and `http://www.mypapyr.com/` return HTTP 308 with a `Location` beginning `https://budgezen.com`.

Health and capability responses are fetched as JSON bodies. Redirect checks use headers only and do not follow redirects.

## Expected output

A successful run prints numbered sections and ends with:

```text
check-launch: PASS
```

The guard prints status and contract fields only. It never prints credentials, full image digests, filenames, object keys, signed URLs, or document-derived values. The check is read-only: it performs HTTP GET requests and does not deploy, reload nginx, SSH to the VPS, upload files, or mutate services.

## Related checks

Run `bash scripts/check-launch.sh` for the offline repository preflight. Run `bash scripts/check-launch.sh rollback-preflight` to confirm that frontend BUILD_ID evidence, the timestamped nginx cutover backup convention, and the three-image backend rollback pointer are documented.
