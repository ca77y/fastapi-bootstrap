#!/bin/bash
LOG_LEVEL=critical uv run scripts/migrate.py
uv run uvicorn server.main:app --host 0.0.0.0 --port 3000
