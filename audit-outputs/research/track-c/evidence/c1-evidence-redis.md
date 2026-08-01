# C1 Evidence — Redis (current authoritative docs)

- **Access date:** 2026-07-31
- **Purpose:** primary-source evidence for `c1-queue-workers-redis.md` (queue, workers, Redis)
- **Method:** read-only fetch of official redis.io documentation. No installs, no Redis instances, no remote access.

## 1. Current version

- `https://redis.io/downloads/` (accessed 2026-07-31): **Redis Open Source 8.8** listed as the current open-source release; "The latest stable release is always available at the fixed https://download.redis.io/redis-stable.tar.gz".
- Note: several official doc pages describe features from newer series — the persistence page documents the **BACKUP command family introduced in Redis 8.10.0** (`https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/`), and the eviction page documents **LRM policies added in Redis 8.6** (`https://redis.io/docs/latest/develop/reference/eviction/`). Pin the exact minor version at implementation time; 8.x is the current series.

## 2. Persistence

Source: `https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/` (accessed 2026-07-31).

- Four options: RDB snapshots, AOF (append-only file), no persistence, or RDB + AOF combined.
- RDB: point-in-time snapshots; "RDB is NOT good if you need to minimize the chance of data loss"; can lose the latest minutes of data; fork() cost; single compact file ideal for backups/DR.
- AOF: logs every write op; `appendfsync` options: `always` (every command, "very very slow, very safe"), `everysec` (default and suggested: "you may lose 1 second of data"), `no` (OS flush, up to ~30 s). "The suggested (and default) policy is to fsync every second."
- AOF rewrite is background and safe; multi-part AOF since Redis 7.0 (base file + incremental files + manifest, under `appenddirname`).
- Combining AOF + RDB: "The general indication you should use both persistence methods is if you want a degree of data safety comparable to what PostgreSQL can provide you." On restart with both enabled, AOF is used to reconstruct state (it is guaranteed most complete).
- Truncated/corrupt AOF: latest Redis loads a truncated AOF discarding the malformed tail (`aof-load-truncated` default on); corrupt AOF may require `redis-check-aof --fix`.
- Redis 8.10 BACKUP command family (`BACKUP START/SEAL/LIST/CLEANUP/STATUS/ABORT`) produces self-contained BASE+INCR+manifest backups; restore via startup-only `preload-file` setting. (Recent addition; available if the deployed version is ≥ 8.10.)
- Backups: hourly/daily RDB copies off-machine recommended; disaster recovery = transfer snapshots to a far location.

## 3. Eviction / maxmemory

Source: `https://redis.io/docs/latest/develop/reference/eviction/` (accessed 2026-07-31).

- `maxmemory` directive; default 0 (unlimited) on 64-bit.
- Policies: `noeviction`, `allkeys-lru`, `allkeys-lrm` (8.6+), `allkeys-lfu`, `allkeys-random`, `volatile-lru`, `volatile-lrm`, `volatile-lfu`, `volatile-random`, `volatile-ttl`.
- `noeviction`: "Keys are not evicted but the server will return an error when you try to execute commands that cache new data… commands that only read existing data still work as normal." Read-only ops keep working; writes fail with OOM error.
- `volatile-ttl`: evicts keys with shortest remaining TTL (only keys with an expiration).
- "The volatile-xxx policies behave like noeviction if no keys have an associated expiration."
- With persistence/replication, `maxmemory` should leave RAM for AOF/replica buffers; not necessary for `noeviction`.
- Monitoring: `INFO stats` `evicted_keys`, `expired_keys`, `keyspace_hits/misses`; `commandstats` shows commands rejected by maxmemory.

## 4. TTL / expiry mechanics

- Expiry applies to keys with an associated `expire` value; a key is removed when its TTL elapses. TTL expiration is a background (active) + lazy process; it is not a precisely-timed, scheduler-guaranteed boundary — applications must not rely on TTL alone as a hard deadline.
- (Documented in `https://redis.io/docs/latest/develop/using-keyspace/` and the `EXPIRE`/`PEXPIRE` command pages; the practical implication — TTL is complementary, not authoritative, for a hard one-hour boundary — is a design conclusion recorded in the C1 brief, not a doc quote.)

## 5. Streams (queue primitive)

Source: `https://redis.io/docs/latest/develop/data-types/streams/` (accessed 2026-07-31) and command pages `xadd`, `xreadgroup`, `xack`, `xautoclaim`, `xgroup`, `xlen`, `xrange`, `xtrim`.

- Streams are append-only logs of entries; entry IDs `ms-seq`.
- Consumer groups: `XGROUP CREATE`, consumers read with `XREADGROUP` (new or historical entries); delivered messages tracked in the **Pending Entries List (PEL)** per consumer; `XACK` confirms processing; `XAUTOCLAIM` automatically reclaims messages stuck in the PEL of a failed consumer (delivery counter increments); `XNACK` releases a message back to the group (Redis 8.2+); `XREADGROUP` supports `NOACK`.
- Capped streams: `XADD ... MAXLEN` trims; trimming can be consumer-group-aware (`MINID`/`MAXLEN` options) in recent versions.
- Persistence/replication and message safety section: with AOF, stream data survives restarts like other keys.
- The streams page is the canonical "Introduction to Redis Streams" and documents the consumer-group pattern used in this design.

## 6. Atomicity

- `MULTI`/`EXEC` transactions and `WATCH` for optimistic locking: `https://redis.io/docs/latest/develop/reference/transactions/`.
- Lua scripting (`EVAL`/`SCRIPT`): `https://redis.io/docs/latest/develop/programmability/` — scripts execute atomically and are the recommended mechanism for multi-step state transitions (e.g., cancel-vs-claim).

## 7. Security

- `requirepass`, ACLs (users, permissions per command/key), TLS support, `protected-mode`, `bind`/`protected-mode yes` for local binding: `https://redis.io/docs/latest/operate/oss_and_stack/management/security/`.
- Design implication: queue Redis binds to the internal Docker network only, never published (arch §7.2, DEC-162).

## 8. Memory sizing and INFO

- `INFO memory` (`used_memory`, `used_memory_dataset`), `MEMORY USAGE key`; `maxmemory` enforcement per eviction docs. Small metadata records have per-key overhead (key, value, expire metadata); the 384 MB `maxmemory` figure in the C1 brief is a design choice sized against queue-depth caps, not a measured value (DEC-066).

## 9. Docker / ops references

- Official image on Docker Hub: `redis` (hub.docker.com/_/redis). Persistence via a mounted volume at `/data`; disable persistence with `--save ""` and `appendonly no` when volatile.
- Healthcheck pattern: `redis-cli ping` (command documented at `https://redis.io/docs/latest/commands/ping/`).

## Uncertainties

- Exact stable minor version to pin (8.8 vs newer 8.x with BACKUP): confirm at implementation time.
- Whether `XNACK` and consumer-group-aware trimming details are needed depends on the final queue design (C1 brief records the intended usage).

## Source list

| # | URL | Accessed |
|---|---|---|
| 1 | https://redis.io/downloads/ | 2026-07-31 |
| 2 | https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ | 2026-07-31 |
| 3 | https://redis.io/docs/latest/develop/reference/eviction/ | 2026-07-31 |
| 4 | https://redis.io/docs/latest/develop/data-types/streams/ | 2026-07-31 |
| 5 | https://redis.io/docs/latest/develop/reference/transactions/ | 2026-07-31 (referenced) |
| 6 | https://redis.io/docs/latest/develop/programmability/ | 2026-07-31 (referenced) |
| 7 | https://redis.io/docs/latest/operate/oss_and_stack/management/security/ | 2026-07-31 (referenced) |
