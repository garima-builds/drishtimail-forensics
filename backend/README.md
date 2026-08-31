# Backend

Create a virtual environment with Python 3.11, install `requirements.txt`, set `DATABASE_URL` to a PostgreSQL instance, then run:

```powershell
uvicorn app.main:app --reload
```

`POST /api/v1/messages` creates an analyst-queue item. `GET /api/v1/messages` and `GET /api/v1/dashboard/summary` drive the dashboard.
