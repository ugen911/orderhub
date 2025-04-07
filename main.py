from fastapi import FastAPI
from db_connection import get_db_engine
from sqlalchemy import text

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Добро пожаловать в систему заказов"}


@app.get("/nomenklatura")
def get_nomenklatura():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM nomenklatura LIMIT 5"))
            rows = [dict(row._mapping) for row in result]
        return {"data": rows}
    except Exception as e:
        return {"error": str(e)}
