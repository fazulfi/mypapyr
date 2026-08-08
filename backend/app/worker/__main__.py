"""Run the worker with ``python -m app.worker`` (Dockerfile.worker CMD)."""

from app.worker.entrypoint import main

raise SystemExit(main())
