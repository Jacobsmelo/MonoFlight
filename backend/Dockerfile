# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.14.6-slim


EXPOSE 8000
EXPOSE 3000


# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set app configuration from .env values
ENV DATABASE_URL=sqlite+aiosqlite:///./monoflight.db
ENV ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
ENV APP_NAME=MonoFlight

WORKDIR /app
COPY . .
   
# Install depenedencies
RUN uv sync --frozen --no-cache

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--port", "80", "--host", "0.0.0.0"]
