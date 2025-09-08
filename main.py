from api import app


if __name__ == "__main__":
    # db = Database()
    # db.create_tables()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)