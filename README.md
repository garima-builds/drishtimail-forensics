# DrishtiMail Forensics

An institutional email-forensics platform. This repository starts the documented stack with a React analyst dashboard, FastAPI service, PostgreSQL evidence schema, Redis worker queue, and MinIO evidence store.

## Run locally

1. Copy `.env.example` to `.env` and replace local secrets.
2. Run `docker compose up --build`.
3. Open `http://localhost:5173`; the API docs are at `http://localhost:8000/docs` and the MinIO console at `http://localhost:9001`.

The initial API seeds two representative messages and a local admin account (`admin@drishtimail.local` / `ChangeMe!2026`) on its first start. Change both the JWT secret and this bootstrap account before sharing the deployment. The Compose database uses a non-owner application role with only `SELECT` and `INSERT` access to the evidence ledger; an immutable trigger independently rejects all update and delete attempts.

## Useful commands

```powershell
docker compose up --build
docker compose down
```

For development without containers, see `backend/README.md` and `frontend/README.md`.
