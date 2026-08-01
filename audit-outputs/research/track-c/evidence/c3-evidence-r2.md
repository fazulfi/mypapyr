# C3 Evidence — Cloudflare R2 (current authoritative docs)

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c3-r2-lifecycle.md` (R2 lifecycle and retention enforcement)
- **Method:** read-only fetch of official developers.cloudflare.com R2 documentation (with the `cloudflare` skill guidance). No provider auth, no account actions, no bucket access.

## 1. Object lifecycle rules

Source: `https://developers.cloudflare.com/r2/buckets/object-lifecycles/` (accessed 2026-07-31; page "Last updated Apr 21, 2026"). Note: the URL is `/r2/buckets/object-lifecycles/` (an earlier guess `/r2/buckets/lifecycle-rules/` returns 404).

Key facts:

- "Object lifecycles determine the retention period of objects… A lifecycle configuration is a collection of lifecycle rules."
- Rule conditions: **prefix-based** targeting; actions: **expire/delete objects** and **transition to Infrequent Access** storage class; `AbortIncompleteMultipartUpload` (days after initiation). Expiration can be by `Days` (age) or absolute `Date`.
- **Critical timing behavior:** "Objects will typically be removed from a bucket within 24 hours of the `x-amz-expiration` value." Existing objects may experience delay when a rule is (re)applied; "Most objects will be transitioned within 24 hours but may take longer depending on the number of objects in the bucket."
- Minimum age granularity is **whole days** (`Expiration: {Days: N}`); there is no hour-level or exact-time deletion. A lifecycle rule therefore **cannot enforce a one-hour deadline**.
- Buckets have a **default lifecycle rule to expire multipart uploads seven days after initiation**.
- Rules maximum: 1000 per bucket.
- When a rule applies that deletes objects, new objects' `x-amz-expiration` value immediately reflects the rule; the header can be observed on objects (useful for verifying rule application).
- Storage-class transition to Infrequent Access incurs a Class A operation; when a transition and an expire conflict within a 24-hour period, the expire (delete) wins.
- Configuration surfaces: dashboard (bucket → Settings → Object Lifecycle Rules), Wrangler CLI (`wrangler r2 bucket lifecycle add/list/remove/set`), S3 API (`putBucketLifecycleConfiguration`/`getBucketLifecycleConfiguration`/`deleteBucketLifecycle`), and the Cloudflare API (`/r2/buckets/{bucket}/lifecycle`).
- Managing lifecycles requires an API token with the **Workers R2 Storage Write** permission group.

## 2. S3 API, boto3, presigned URLs

Source: `https://developers.cloudflare.com/r2/examples/aws/boto3/` (accessed 2026-07-31; page "Last updated Jun 8, 2026").

- boto3 client: `endpoint_url="https://<ACCOUNT_ID>.r2.cloudflarestorage.com"`, `region_name="auto"`, SigV4, access key/secret.
- Common ops: `head_object`, `get_object`, `upload_fileobj`, `delete_object`.
- Multipart upload API (`create_multipart_upload`, `upload_part`, `complete_multipart_upload`, `abort_multipart_upload`); part sizes, performance guidance; cross-reference: "Upload objects" page (`https://developers.cloudflare.com/r2/objects/upload-objects/`).
- **Presigned URLs:** `generate_presigned_url("get_object", Params={"Bucket","Key"}, ExpiresIn=seconds)`; example uses `ExpiresIn=3600`; the signed URL carries `X-Amz-Expires=<seconds>`. PUT presigned URLs can restrict Content-Type (signature includes it) and combine with CORS rules.
- Upload objects page (referenced): multipart part size limits and lifecycle of incomplete multipart uploads.

## 3. Pricing (Standard and Infrequent Access)

Source: `https://developers.cloudflare.com/r2/pricing/` (accessed 2026-07-31; page "Last updated May 28, 2026").

- Standard storage: $0.015/GB-month; Class A ops $4.50/million; Class B ops $0.36/million; **egress free**.
- Infrequent Access: $0.01/GB-month; Class A $9.00/million; Class B $0.90/million; data retrieval $0.01/GB; **30-day minimum storage duration**.
- **Free tier:** 10 GB-month storage, 1 million Class A ops/month, 10 million Class B ops/month, free egress. Free tier applies to Standard storage only.
- **Free operations:** `DeleteObject`, `DeleteBucket`, `AbortMultipartUpload` are free (lifecycle-rule deletions remove objects — `DeleteObject` semantics — and are therefore not billed as a Class A/B operation; this is the natural reading of the free-operations list and should be confirmed against the current pricing page before relying on it).
- Class A includes `PutObject`, `CopyObject`, `ListObjects`, multipart ops, `PutBucketLifecycleConfiguration`, `LifecycleStorageTierTransition`. Class B includes `GetObject`, `HeadObject`, `GetBucketLifecycleConfiguration`.
- Unauthorized requests (401) are not charged.
- GB-month billing averages peak daily storage over the month.

## 4. Consistency, limits, and related pages (referenced)

- R2 is strongly consistent for reads/writes on the S3 API surface (documented in R2 docs; verify current wording at `https://developers.cloudflare.com/r2/reference/` — referenced, not re-fetched).
- Object size limits and per-second operation limits are documented in the R2 limits/reference pages (referenced; not re-fetched).
- API tokens and permission groups: `https://developers.cloudflare.com/r2/api/tokens/` (referenced) — least privilege via bucket-scoped tokens with Workers R2 Storage Write/Read permission groups.

## Uncertainties

- Whether lifecycle deletions count as billed operations (free `DeleteObject` list suggests free; confirm against current docs/dashboard at implementation).
- Exact per-second operation limits and object size cap (referenced pages not re-fetched; C2 handles per-tool size ceilings anyway).
- `x-amz-expiration` exposure on objects: the docs state new objects immediately reflect the rule; exact header behavior confirmed at implementation.

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://developers.cloudflare.com/r2/buckets/object-lifecycles/ | 2026-07-31 |
| 2 | https://developers.cloudflare.com/r2/examples/aws/boto3/ | 2026-07-31 |
| 3 | https://developers.cloudflare.com/r2/pricing/ | 2026-07-31 |
| 4 | https://developers.cloudflare.com/r2/objects/upload-objects/ | 2026-07-31 (referenced) |
| 5 | https://developers.cloudflare.com/r2/api/tokens/ | 2026-07-31 (referenced) |
| 6 | https://developers.cloudflare.com/api/resources/r2/subresources/buckets/subresources/lifecycle/ | 2026-07-31 (referenced) |
