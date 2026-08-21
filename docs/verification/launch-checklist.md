# Phase 10 launch checklist

## Launch gate summary

Phase 10 VL-05 is the coordinated pre-launch, smoke, rollback-readiness, and activation gate for the five-tool trilingual catalogue. Launch requires evidence across VL-01 through VL-05 and an explicit owner decision under G-3. The gate covers English, Spanish, and Indonesian routes and the five tools: compress, merge, split, JPG to PDF, and PDF to JPG.

This checklist applies DEC-140's coordinated trilingual launch gate and preserves the privacy and release controls in DEC-096, DEC-160, DEC-177, and DEC-178. CI is evidence, not authorization; production activation remains an owner-approved operator action.

## Preconditions

- [ ] The release commit, backend release reference, frontend deployment URL, and frontend BUILD_ID are recorded.
- [ ] R-23 disposition is recorded: the launch owner has documented the applicable production-risk decision and any accepted limitations.
- [ ] R-26 disposition is recorded: the owner has confirmed the VPS, credentials, DNS/TLS, and deployment state out of band without placing secrets in this repository.
- [ ] The gate entry contains links or references for VL-01 through VL-05 evidence.
- [ ] `bash scripts/check-launch.sh` passes offline from the repository root.
- [ ] `bash scripts/check-launch.sh rollback-preflight` passes and its evidence is attached to the release record.
- [ ] No launch artifact contains credentials, signed URLs, filenames, object keys, or full image digests.

## Per-workstream verification status

| Workstream | Required evidence | Status | Release reference |
| --- | --- | --- | --- |
| VL-01 E2E gate | Five-tool flows pass in EN/ES/ID, including upload, processing, result, and download behavior where applicable. | [ ] Pending / [ ] Pass | |
| VL-02 accessibility | Shell, tool pages, localized routes, keyboard, focus, and automated accessibility checks pass. | [ ] Pending / [ ] Pass | |
| VL-03 visual | Desktop and mobile visual review passes for the catalogue, states, ads, legal/support pages, and localized copy. | [ ] Pending / [ ] Pass | |
| VL-04 performance/CWV | Production build and performance evidence meet the approved LCP, INP, CLS, and supporting thresholds. | [ ] Pending / [ ] Pass | |
| VL-05 smoke/rollback | Offline preflight, public smoke, rollback evidence, and activation readiness pass. | [ ] Pending / [ ] Pass | |

## Production activation steps

### Backend

- [ ] Confirm the previous API, worker, and ClamAV digest-form image references are recorded before activation.
- [ ] Stage the reviewed release under `/opt/mypapyr/releases/<name>` and provision `PAPYR_ENV_FILE=/opt/mypapyr/production/.env` out of band.
- [ ] Run the release checklist Section 5 backend command with the staged release:

```bash
docker compose -p papyr-app --project-directory <rel>/deploy --env-file <rel>/deploy/image-manifest.env -f docker-compose.yml -f /opt/mypapyr/production/compose.override.yml --profile app --profile queue up -d --pull never
```

- [ ] Confirm all `papyr-app-*` containers are healthy and `curl localhost:3016/health` returns 200.
- [ ] Confirm `/health/ready` is ready and `/api/v1/capabilities` returns 200.

### Frontend

- [ ] Deploy the reviewed frontend through the authorized Vercel release process.
- [ ] Record the pre-activation and post-activation Vercel production URLs and BUILD_ID values.
- [ ] Confirm `budgezen.com` is attached to the approved production deployment.

### Cutover and rollback readiness

- [ ] Confirm legacy `mypapyr.com` and `www.mypapyr.com` host-level 308 behavior before and after cutover.
- [ ] Run `nginx -t` before any authorized reload; do not reload on failure.
- [ ] Preserve the rollback file at `/etc/nginx/sites-available/mypapyr.bak-cutover-<UTC timestamp>`.
- [ ] Confirm the backend rollback manifest restores `PAPYR_API_IMAGE`, `PAPYR_WORKERS_IMAGE`, and `PAPYR_CLAMD_IMAGE` together, using the procedure in [upgrade.md](../upgrade.md#rollback).
- [ ] Do not use `down`, remove volumes, rebuild destructively, or alter Redis persistence during rollback.

### Post-activation verification

- [ ] Run `bash scripts/check-launch.sh smoke` from a networked client.
- [ ] Verify `/`, `/en`, `/es`, and `/id`, one representative tool route, `/sitemap.xml`, and `/robots.txt`.
- [ ] Verify the API health, readiness, and capabilities endpoints through `https://api.mypapyr.com`.
- [ ] Verify the five-tool trilingual route matrix and the approved ad, canonical, hreflang, and legal markers.
- [ ] Record any accepted limitation and its owner disposition; do not silently downgrade a failed gate.

## Owner authorization

G-3 is a manual owner action. The release manager may prepare evidence, but must not infer authorization from green CI or a passing smoke test.

- **Owner decision:** [ ] Authorize launch  [ ] Hold launch  [ ] Authorize with recorded limitations
- **Owner name/role:**
- **Decision timestamp (UTC):**
- **Backend release reference:**
- **Frontend deployment URL:**
- **Frontend BUILD_ID:**
- **Rollback record reference:**
- **Limitations / follow-up owner:**
- **Signature or approval reference:**

## Rollback readiness summary

Record rollback pointers without publishing the full digest values.

| Component | Current release reference | Rollback point recorded | Evidence |
| --- | --- | --- | --- |
| API | release name + masked digest | [ ] | |
| Workers | release name + masked digest | [ ] | |
| ClamAV | release name + masked digest | [ ] | |
| Frontend | production URL + BUILD_ID | [ ] | |
| Legacy nginx cutover | active vhost + timestamped backup path | [ ] | |

The backend rollback is a coordinated three-image re-up through Compose. The frontend rollback is an authorized Vercel alias/deployment move. The legacy host rollback restores the timestamped nginx configuration only after `nginx -t` passes. All rollback actions remain non-destructive and preserve the Redis/R2 lifecycle contracts.
