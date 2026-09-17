## Monoflight backend

The backend is a FastAPI application organized as an importable `app` package.
Dependencies are managed with `uv` through `pyproject.toml` and `uv.lock`.

### Layout

- `app/main.py` creates the FastAPI application.
- `app/api/v1/` composes versioned route handlers.
- `app/core/` contains configuration and cross-cutting concerns.
- `app/crud/`, `app/models/`, `app/schemas/`, and `app/db/` are boundaries for
  database and domain code as those features are added.
- `app/tests/` contains backend tests.

### Run locally

From this directory:

```powershell
uv run uvicorn app.main:app --reload
```

The compatibility launcher also works:

```powershell
uv run python main.py
```

The initial health check is available at
`http://127.0.0.1:8000/api/v1/health`.