from .queries import MAIN_QUERY, STATS_QUERY, ORDERS_QUERY, ANALOGS_QUERY
from .helpers import generate_last_months
from db_connection import get_db_engine
from sqlalchemy import text


def get_nomenklatura_full(kod: str):
    engine = get_db_engine()
    with engine.connect() as conn:
        # Основной блок
        result = conn.execute(text(MAIN_QUERY), {"kod": kod.strip()})
        row = result.fetchone()
        if not row:
            return {"error": "Товар не найден"}

        data = dict(row._mapping)
        data["pometkaudalenija"] = data["pometkaudalenija"] == "Да"

        # Преобразование логических полей из accessdata
        for field in [
            "ne_ispolzuetsya_v_zakaze",
            "nelikvid",
            "zafiksirovat_minimalki",
            "list_ozhidaniya",
        ]:
            if field in data:
                data[field] = bool(data[field])

        # Статистика за 36 месяцев
        months = generate_last_months()
        stat_result = conn.execute(
            text(STATS_QUERY), {"kod": kod.strip(), "months": tuple(months)}
        )

        stats_dict = {
            m: {
                "sales": 0,
                "salesum": 0,
                "stock": 0,
                "tsena": None,
                "sup": 0,
                "supsum": 0,
            }
            for m in months
        }
        for row in stat_result.fetchall():
            stats_dict[row.year_month] = {
                "sales": row.sales,
                "salesum": row.salesum,
                "stock": row.stock,
                "tsena": row.tsena,
                "sup": row.sup,
                "supsum": row.supsum,
            }
        data["monthly_stats"] = stats_dict

        # Заказы
        orders_result = conn.execute(text(ORDERS_QUERY), {"kod": kod.strip()})
        data["orders"] = [dict(row._mapping) for row in orders_result.fetchall()]

        # Аналоги
        analogs_result = conn.execute(
            text(ANALOGS_QUERY),
            {"group": data.get("gruppa_analogov"), "kod": kod.strip()},
        )
        analogs = [dict(row._mapping) for row in analogs_result.fetchall()]
        for analog in analogs:
            analog["pometkaudalenija"] = analog["pometkaudalenija"] == "Да"
        data["analogs"] = analogs

        return data
