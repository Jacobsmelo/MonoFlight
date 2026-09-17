import uvicorn

from app.main import app


def main() -> None:
    uvicorn.run("app.main:app", reload=True)


if __name__ == "__main__":
    main()
