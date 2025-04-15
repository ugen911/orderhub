from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from db_connection import get_db_engine
from nomenklatura.routes import router as nomenklatura_router
from nomenklatura.service import get_nomenklatura_full

app = FastAPI()

# 📁 Путь к шаблонам
templates = Jinja2Templates(directory="templates")

# 🔌 Подключение роутов
app.include_router(nomenklatura_router)


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


# 🖼️ HTML-страница карточки
@app.get("/nomenklatura/{kod}/view", response_class=HTMLResponse)
def render_nomenklatura_view(kod: str, request: Request):
    try:
        data = get_nomenklatura_full(kod)
        if "error" in data:
            return HTMLResponse(content="Ошибка: товар не найден", status_code=404)
        return templates.TemplateResponse(
            "nomenklatura.html", {"request": request, "data": data}
        )
    except Exception as e:
        return HTMLResponse(content=f"Ошибка: {str(e)}", status_code=500)
