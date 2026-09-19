# MonoFlight

MonoFlight is a flight-booking web application being developed with a full-stack
workflow:

- **Backend:** FastAPI, Python, `uv`, SQLAlchemy, and Alembic
- **Frontend:** Next.js and React
- **Database:** PostgreSQL (planned integration; SQLite is currently available
  in the backend dependencies for early development)
- **Deployment:** Docker Compose locally, Kubernetes later
- **Mobile:** Reserved for a future client in `mobile/`

This guide is the project setup and development runbook. Commands are written
for PowerShell on Windows unless stated otherwise.

## Current repository structure

```text
MonoFlight/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Versioned API routers and endpoints
│   │   ├── core/            # Configuration and shared application concerns
│   │   └── tests/           # Backend tests
│   ├── Dockerfile
│   ├── compose.yaml
│   ├── pyproject.toml
│   ├── uv.lock
│   └── README.md
├── frontend/                # Next.js application (to be initialized)
├── mobile/                  # Future mobile client
└── Readme.md
```

The initial backend health endpoint is:

```text
http://127.0.0.1:8000/api/v1/health
```

FastAPI's interactive API documentation is available at `/docs` when the
backend is running.

## Prerequisites

Install the following tools before starting:

- Git
- Python 3.14 or a compatible version accepted by
  [`backend/pyproject.toml`](backend/pyproject.toml)
- [`uv`](https://docs.astral.sh/uv/)
- Node.js LTS and npm
- Docker Desktop, including Docker Compose
- A code editor such as VS Code

Check the installations:

```powershell
git --version
python --version
uv --version
node --version
npm --version
docker --version
docker compose version
```

## 1. Initialize Git

If this is a new local copy rather than the existing repository, run these
commands from the project root:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial project setup"
```

Connect a remote only after creating the repository on your Git hosting
provider:

```powershell
git remote add origin https://github.com/<owner>/MonoFlight.git
git push -u origin main
```

Before committing, add local secrets and generated files to `.gitignore`.
Never commit `backend/.env`, credentials, API keys, `.venv/`, `node_modules/`,
or build output.

## 2. Set up the FastAPI backend with uv

The backend is already initialized and includes `pyproject.toml` and
`uv.lock`. To reproduce the setup from scratch:

```powershell
New-Item -ItemType Directory -Force backend
Set-Location backend
uv init --name backend
uv python install 3.14
uv python pin 3.14
uv venv
```

Activate the virtual environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation for the current user, use the
following command once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Install the core backend packages:

```powershell
uv add "fastapi[standard]" uvicorn sqlalchemy alembic python-dotenv
uv add pytest pytest-asyncio httpx
```

Install the PostgreSQL driver when PostgreSQL work begins:

```powershell
uv add psycopg2-binary
```

For an existing checkout, install exactly what is recorded in the lockfile:

```powershell
Set-Location backend
uv sync
```

Use `uv run` so commands always use the project environment:

```powershell
uv run fastapi dev app/main.py --host 127.0.0.1 --port 8000
uv run pytest
```

The compatibility launcher in the current backend also works:

```powershell
uv run python main.py
```

When dependencies or project metadata change, update and commit `uv.lock`:

```powershell
uv lock
uv sync
```

## 3. Initialize the Next.js frontend

From the repository root, initialize the existing `frontend` directory with
the recommended Next.js defaults:

```powershell
npx create-next-app@latest frontend
```

Recommended prompts for this project:

- TypeScript: **Yes**
- ESLint: **Yes**
- Tailwind CSS: **Yes**
- Use `src/` directory: **Yes**
- Use App Router: **Yes**
- Customize the import alias: **Yes**, use `@/*`  

If the directory is empty and you want a non-interactive setup, use:

```powershell
npx create-next-app@latest frontend `
  --typescript `
  --eslint `
  --tailwind `
  --src-dir `
  --app `
  --import-alias "@/*"
```

Start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Useful optional frontend components can be added later as requirements become
clear:

```powershell
# Forms and validation
npm install react-hook-form zod @hookform/resolvers

# Server-state fetching and caching
npm install @tanstack/react-query

# Accessible UI primitives
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# Dates, icons, and notifications
npm install date-fns lucide-react sonner

# End-to-end browser testing
npm install --save-dev playwright
npx playwright install
```

Do not add every optional package up front. Add a package when a feature
requires it and commit the resulting `package.json` and lockfile.

## 4. Run the application locally

Run the backend and frontend in separate terminals.

**Terminal 1:**

```powershell
Set-Location backend
uv run fastapi dev app/main.py --port 8000
```

**Terminal 2:**

```powershell
Set-Location frontend
npm run dev
```

The frontend should call the API through an environment variable rather than a
hard-coded URL. For example, create `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Keep environment files containing secrets out of Git.

## 5. Docker image

The current [`backend/Dockerfile`](backend/Dockerfile) uses a slim Python image,
copies `uv` into the image, installs the locked dependencies, runs as a
non-root user, and starts FastAPI:

```dockerfile
FROM python:3.14.6-slim

EXPOSE 8000
EXPOSE 3000

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app
RUN uv sync --frozen --no-cache

RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app
USER appuser

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
```

The application currently listens on port `80` inside the image. The Docker
commands below map host port `8000` to that internal port. If the container is
changed to listen on `8000`, update the `CMD` and port mappings together.

Build and run the backend image from the repository root:

```powershell
docker build -t monoflight-backend backend
docker run -d -p 8000:80 -p 3000:3000 --name monoflight monoflight-backend
```

## Container management commands

### View logs

```powershell
docker logs monoflight
docker logs -f monoflight
```

### Container status and details

```powershell
docker ps
docker ps -a
docker inspect monoflight
```

### Stop, start, and restart

```powershell
docker stop monoflight
docker start monoflight
docker restart monoflight
```

### Execute commands in the container

```powershell
docker exec -it monoflight /bin/bash
docker exec -it monoflight /app/.venv/bin/fastapi dev app/main.py
```

### Clean up

Stop the container before removing it:

```powershell
docker stop monoflight
docker rm monoflight
docker rmi monoflight-backend
```

The following removes unused Docker resources across the machine. Review the
prompt carefully before confirming:

```powershell
docker system prune
```

## Docker Compose

The current Compose file is [`backend/compose.yaml`](backend/compose.yaml).
Start it from the repository root:

```powershell
docker compose -f backend/compose.yaml up -d
docker compose -f backend/compose.yaml down
docker compose -f backend/compose.yaml logs -f
docker compose -f backend/compose.yaml restart
```

The Compose service is named `monoflight`. To rebuild after changing backend
code, dependencies, or the Dockerfile:

```powershell
docker compose -f backend/compose.yaml up -d --build
```

## 6. PostgreSQL (planned feature)

PostgreSQL will become the primary persistent store for users, airports,
airlines, flights, fares, inventory, bookings, and payments. The planned
development sequence is:

1. Add PostgreSQL to Compose with a named volume.
2. Add a SQLAlchemy async engine and session dependency.
3. Store the connection string in `backend/.env`, not in source control.
4. Create models and repositories by domain.
5. Add migrations with Alembic.
6. Add integration tests against a disposable PostgreSQL database.

A future local connection string will have this shape:

```dotenv
DATABASE_URL=postgresql+asyncpg://monoflight:<password>@localhost:5432/monoflight
```

The exact credentials and database service name should be defined in the
Compose configuration when PostgreSQL is introduced. Until then, do not assume
that a PostgreSQL container is running.

## 7. Alembic migrations (planned feature)

Alembic is already listed in the backend dependencies, but migrations should
be wired to the final SQLAlchemy metadata and database configuration before
running them in a shared environment.

The planned initialization commands, from `backend/`, are:

```powershell
uv run alembic init app/db/migrations
```

Configure `alembic.ini` and `app/db/migrations/env.py` with the project
database URL and `Base.metadata`, then create and apply migrations:

```powershell
uv run alembic revision --autogenerate -m "create initial booking tables"
uv run alembic upgrade head
uv run alembic current
uv run alembic history
```

For local rollback testing:

```powershell
uv run alembic downgrade -1
uv run alembic upgrade head
```

Review autogenerated migrations before applying them. Never edit an already
applied migration to change production history; create a new revision instead.

## 8. Kubernetes (planned feature)

Kubernetes will be covered after the Docker image and Compose workflow are
stable. The deployment plan is:

1. Publish versioned backend images to a container registry.
2. Create a `Deployment` and `Service` for the FastAPI API.
3. Add readiness and liveness endpoints.
4. Store database credentials in Kubernetes `Secret` resources.
5. Store non-sensitive configuration in `ConfigMap` resources.
6. Add PostgreSQL as a managed service or a separately operated workload.
7. Add ingress, TLS, resource limits, autoscaling, and observability.

Typical future commands will look like:

```powershell
kubectl cluster-info
kubectl apply -f deploy/kubernetes/
kubectl get deployments
kubectl get pods
kubectl get services
kubectl logs deployment/monoflight-backend
kubectl rollout status deployment/monoflight-backend
kubectl delete -f deploy/kubernetes/
```

These commands are intentionally not runnable yet because Kubernetes manifests
and a cluster configuration have not been added to this repository.

## Development workflow

For each feature:

1. Create a branch: `git switch -c feature/<short-name>`.
2. Update backend or frontend code in its own directory.
3. Run focused tests and formatters.
4. Run the backend and frontend locally.
5. Test the API through `/docs` or the frontend flow.
6. Build the Docker image when container behavior is affected.
7. Review the diff, commit, and push the branch.

Backend checks:

```powershell
Set-Location backend
uv run pytest
uv run ruff check .
uv run black --check .
```

Frontend checks, after Next.js is initialized:

```powershell
Set-Location frontend
npm run lint
npm run build
```

Review changed files before committing:

```powershell
git status
git diff --check
git diff
```

## Useful links

- Backend-specific notes: [`backend/README.md`](backend/README.md)
- Backend dependency manifest: [`backend/pyproject.toml`](backend/pyproject.toml)
- Backend container definition: [`backend/Dockerfile`](backend/Dockerfile)
- Local Compose definition: [`backend/compose.yaml`](backend/compose.yaml)
