from api import app

from database import create_table


if __name__ == "__main__":
    create_table()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)