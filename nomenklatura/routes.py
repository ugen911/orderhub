from fastapi import APIRouter, Request, Form
from sqlalchemy import text
from fastapi.responses import RedirectResponse
from .service import get_nomenklatura_full, get_prev_next_kod, search_kod_by_artikul
from starlette.status import HTTP_303_SEE_OTHER

router = APIRouter()


@router.get("/nomenklatura/{kod}")
def get_nomenklatura_detail(kod: str):
    return get_nomenklatura_full(kod)


@router.post("/nomenklatura/{kod}/toggle/{flag}")
def toggle_flag(kod: str, flag: str):
    from db_connection import get_db_engine

    engine = get_db_engine()
    valid_flags = [
        "ne_ispolzuetsya_v_zakaze",
        "nelikvid",
        "list_ozhidaniya",
        "zafiksirovat_minimalki",
    ]
    if flag not in valid_flags:
        return {"error": "Invalid flag"}

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT " + flag + " FROM accessdata WHERE TRIM(kod) = :kod"),
            {"kod": kod.strip()},
        ).fetchone()
        if result is not None:
            new_value = not bool(result[0])
            conn.execute(
                text(
                    f"""
                    UPDATE accessdata
                    SET {flag} = :val
                    WHERE TRIM(kod) = :kod
                """
                ),
                {"val": int(new_value), "kod": kod.strip()},
            )
            conn.commit()
    return RedirectResponse(
        url=f"/nomenklatura/{kod}/view", status_code=HTTP_303_SEE_OTHER
    )


@router.get("/nomenklatura/{kod}/prev")
def prev_kod(kod: str):
    prev = get_prev_next_kod(kod, direction="prev")
    return RedirectResponse(
        url=f"/nomenklatura/{prev}/view", status_code=HTTP_303_SEE_OTHER
    )


@router.get("/nomenklatura/{kod}/next")
def next_kod(kod: str):
    next_ = get_prev_next_kod(kod, direction="next")
    return RedirectResponse(
        url=f"/nomenklatura/{next_}/view", status_code=HTTP_303_SEE_OTHER
    )


@router.get("/nomenklatura/search")
def search_view(kod: str = "", artikul: str = ""):
    if kod:
        return RedirectResponse(
            url=f"/nomenklatura/{kod}/view", status_code=HTTP_303_SEE_OTHER
        )
    elif artikul:
        found = search_kod_by_artikul(artikul)
        if found:
            return RedirectResponse(
                url=f"/nomenklatura/{found}/view", status_code=HTTP_303_SEE_OTHER
            )
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/nomenklatura/{kod}/update_field")
async def update_field(kod: str, field: str = Form(...), value: str = Form(...)):
    from db_connection import get_db_engine

    engine = get_db_engine()

    allowed_fields = ["minimal"]  # ← разрешены только эти поля
    if field not in allowed_fields:
        return {"error": "Field not allowed"}

    try:
        value = float(value)
    except ValueError:
        return {"error": "Invalid value"}

    with engine.connect() as conn:
        conn.execute(
            text(
                f"""
                UPDATE accessdata
                SET {field} = :val
                WHERE TRIM(kod) = :kod
            """
            ),
            {"val": value, "kod": kod.strip()},
        )
        conn.commit()

    return {"status": "ok", "field": field, "value": value}
