from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import text
from starlette.status import HTTP_303_SEE_OTHER, HTTP_204_NO_CONTENT
from db_connection import get_db_engine
from .service import get_nomenklatura_full, search_kod_by_artikul

router = APIRouter()


def get_prev_next_kod(kod: str, direction="next"):
    engine = get_db_engine()
    with engine.connect() as conn:
        order = "ASC" if direction == "next" else "DESC"
        result = conn.execute(
            text(
                f"""
                SELECT kod FROM nomenklaturaold
                WHERE kod {( '>' if direction == "next" else '<')} :kod
                ORDER BY kod {order}
                LIMIT 1
                """
            ),
            {"kod": kod},
        ).fetchone()
        return result[0] if result else kod


@router.get("/nomenklatura/{kod}")
def get_nomenklatura_detail(kod: str):
    return get_nomenklatura_full(kod)


@router.post("/nomenklatura/{kod}/toggle/{flag}")
def toggle_flag(kod: str, flag: str):
    print(f"[DEBUG] kod={kod}, flag={flag}")

    engine = get_db_engine()
    valid_flags = [
        "ne_ispolzuetsya_v_zakaze",
        "nelikvid",
        "list_ozhidaniya",
        "zafiksirovat_minimalki",
    ]
    if flag not in valid_flags:
        print(f"[ERROR] Invalid flag received: {flag}")
        return JSONResponse(content={"error": f"Invalid flag: {flag}"}, status_code=400)

    with engine.connect() as conn:
        try:
            result = conn.execute(
                text(f'SELECT "{flag}" FROM accessdata WHERE kod = :kod'), {"kod": kod}
            ).fetchone()

            if result is None:
                print(f"[WARN] No such kod in accessdata: {kod}")
                return JSONResponse(
                    content={"error": f"kod {kod} not found in accessdata"},
                    status_code=404,
                )

            current_value = result[0]
            print(
                f"[DEBUG] current DB value: {current_value} (type: {type(current_value)})"
            )

            current_bool = str(current_value).strip().lower() in [
                "1",
                "true",
                "t",
                "да",
                "y",
            ]
            new_value = not current_bool

            conn.execute(
                text(f'UPDATE accessdata SET "{flag}" = :val WHERE kod = :kod'),
                {"val": new_value, "kod": kod},  # ← теперь это BOOLEAN
            )
            conn.commit()

            print(f"[INFO] Flag {flag} for kod {kod} updated to {new_value}")
            return JSONResponse(content={"new_value": new_value})

        except Exception as e:
            print(f"[ERROR] toggle_flag failed: {e}")
            return JSONResponse(
                content={"error": f"Internal error: {str(e)}"}, status_code=500
            )


@router.post("/nomenklatura/{kod}/update_field")
async def update_field(kod: str, field: str = Form(...), value: str = Form(...)):
    print(f"[DEBUG] kod={kod}, field={field}, value={value}")

    engine = get_db_engine()
    allowed_fields = ["minimal"]
    if field not in allowed_fields:
        print(f"[ERROR] Field not allowed: {field}")
        return JSONResponse(content={"error": "Field not allowed"}, status_code=400)

    try:
        value = float(value)
    except ValueError:
        print(f"[ERROR] Invalid value type: {value}")
        return JSONResponse(content={"error": "Invalid value"}, status_code=400)

    with engine.connect() as conn:
        try:
            conn.execute(
                text(f'UPDATE accessdata SET "{field}" = :val WHERE kod = :kod'),
                {"val": value, "kod": kod},
            )
            conn.commit()
            print(f"[INFO] Поле {field} обновлено для kod={kod}: {value}")
            return JSONResponse(
                content={"status": "ok", "field": field, "value": value}
            )
        except Exception as e:
            print(f"[ERROR] update_field failed: {e}")
            return JSONResponse(
                content={"error": f"Internal error: {str(e)}"}, status_code=500
            )


@router.get("/nomenklatura/search")
def search_view(kod: str = "", artikul: str = ""):
    print(">>> search_view() STARTED")
    print(f"[DEBUG] kod={kod}, artikul={artikul}")

    if kod:
        print(f"[INFO] Поиск по коду: {kod}")
        return RedirectResponse(
            url=f"/nomenklatura/{kod}/view", status_code=HTTP_303_SEE_OTHER
        )

    elif artikul:
        found = search_kod_by_artikul(artikul)
        if found:
            print(f"[INFO] Найден артикул {artikul} → kod={found}")
            return RedirectResponse(
                url=f"/nomenklatura/{found}/view", status_code=HTTP_303_SEE_OTHER
            )
        else:
            print(f"[WARN] Артикул не найден: {artikul}")

    else:
        print(f"[WARN] Пустой запрос поиска")

    return JSONResponse(
        status_code=HTTP_204_NO_CONTENT, content={"message": "not found"}
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
