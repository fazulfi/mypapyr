"""Public processing routes will be added with their concrete implementations."""

from __future__ import annotations

import hashlib

from fastapi import Request


def _resolve_origin(request: Request) -> str:
    """One-way SHA-256 origin fingerprint of the calling client (I3).

    Privacy-preserving, deterministic per-client identity for fair-use
    admission: the ``CF-Connecting-IP`` header when present (Cloudflare —
    set by the edge, never spoofable at the app), else the first
    ``x-forwarded-for`` value, else the direct socket peer
    (``request.client.host``). The raw address never leaves this function:
    only the hex digest reaches the queue and the fair-use counter keyspace
    (``fingerprint_origin``).
    """
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return hashlib.sha256(cf_ip.encode("utf-8")).hexdigest()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first = forwarded.split(",", 1)[0].strip()
        if first:
            return hashlib.sha256(first.encode("utf-8")).hexdigest()
    client = request.client
    if client is not None and client.host:
        return hashlib.sha256(client.host.encode("utf-8")).hexdigest()
    return hashlib.sha256(b"").hexdigest()