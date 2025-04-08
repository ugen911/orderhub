from sqlalchemy import text
from db_connection import get_db_engine
from fastapi import FastAPI
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = FastAPI()


def get_nomenklatura_full(kod: str):
    engine = get_db_engine()
    with engine.connect() as conn:
        # Основной запрос по номенклатуре
        query = text(
            """
            SELECT 
                TRIM(n.kod) AS kod,
                n.artikul,
                n.proizvoditel,
                n.edizm,
                n.stellazh,
                n.naimenovanie,
                n.pometkaudalenija,

                fs.gruppa_analogov,
                fs.type_detail,
                fs.abc,
                fs.xyz,
                fs.total_sales_last_12_months,
                fs.total_sales_last_3_months,
                fs.min_stock,

                p.tsenazakup,
                p.tsenarozn,

                mp.middleprice,
                mp.maxprice,

                s.osnsklad,
                s.zakazy_sklad,

                d.stock AS delivery_stock,
                d.price AS delivery_price,
                d.sklad AS delivery_sklad

            FROM nomenklaturaold n
            LEFT JOIN full_statistic fs ON TRIM(n.kod) = TRIM(fs.kod)
            LEFT JOIN priceold p ON TRIM(n.kod) = TRIM(p.kod)
            LEFT JOIN middlemaxprice mp ON TRIM(n.kod) = TRIM(mp.kod)
            LEFT JOIN stockold s ON TRIM(n.kod) = TRIM(s.kod)
            LEFT JOIN deliveryminprice d ON TRIM(n.kod) = TRIM(d.kod)
            WHERE TRIM(n.kod) = :kod
            LIMIT 1;
        """
        )

        result = conn.execute(query, {"kod": kod.strip()})
        row = result.fetchone()

        if not row:
            return {"error": "Товар не найден"}

        data = dict(row._mapping)
        data["pometkaudalenija"] = True if data["pometkaudalenija"] == "Да" else False
        analog_group = data.get("gruppa_analogov")

        # Получаем месяцы от текущей даты назад на 36 месяцев
        now = datetime.now()
        start = now - relativedelta(months=35)
        months = [
            (start.year + (start.month + i - 1) // 12, (start.month + i - 1) % 12 + 1)
            for i in range(36)
        ]
        month_keys = [f"{y}-{m:02}" for y, m in months]

        stats_query = text(
            f"""
            SELECT all_months.kod, all_months.year_month,
                   SUM(all_months.sales) AS sales,
                   SUM(all_months.salesum) AS salesum,
                   SUM(all_months.stock) AS stock,
                   MAX(all_months.tsena) AS tsena,
                   SUM(all_months.sup) AS sup,
                   SUM(all_months.supsum) AS supsum
            FROM (
                SELECT TRIM(kod) AS kod, year_month, kolichestvo AS sales, summa AS salesum, 0 AS stock, 0 AS tsena, 0 AS sup, 0 AS supsum FROM salespivot
                UNION ALL
                SELECT TRIM(nomenklaturakod) AS kod, month AS year_month, 0, 0, balance, 0, 0, 0 FROM stockendmonth
                UNION ALL
                SELECT TRIM(kod) AS kod, data AS year_month, 0, 0, 0, tsena, 0, 0 FROM priceendmonth
                UNION ALL
                SELECT TRIM(kod) AS kod, year_month, 0, 0, 0, 0, kolichestvo, summa FROM suppliespivot
            ) all_months
            WHERE all_months.kod = :kod AND all_months.year_month IN :months
            GROUP BY all_months.kod, all_months.year_month
        """
        )

        stat_result = conn.execute(
            stats_query, {"kod": kod.strip(), "months": tuple(month_keys)}
        )
        stats_rows = stat_result.fetchall()

        stats_dict = {
            m: {
                "sales": 0,
                "salesum": 0,
                "stock": 0,
                "tsena": None,
                "sup": 0,
                "supsum": 0,
            }
            for m in month_keys
        }
        for row in stats_rows:
            ym = row.year_month
            stats_dict[ym] = {
                "sales": row.sales,
                "salesum": row.salesum,
                "stock": row.stock,
                "tsena": row.tsena,
                "sup": row.sup,
                "supsum": row.supsum,
            }

        data["monthly_stats"] = stats_dict

        # Загружаем заказы по товару
        orders_query = text(
            """
            SELECT 
                data_prinatia_zakaza,
                artikul,
                edinicy_izmerenia,
                zakup,
                kolicestvo,
                summa,
                status,
                roznica,
                nacenka,
                primecanie,
                postavsik,
                sklad,
                oplata,
                "scet_№" AS schet_no,
                data_sceta
            FROM orders
            WHERE TRIM(kod) = :kod
            ORDER BY data_prinatia_zakaza DESC
        """
        )

        orders_result = conn.execute(orders_query, {"kod": kod.strip()})
        orders_rows = [dict(row._mapping) for row in orders_result.fetchall()]
        data["orders"] = orders_rows

        # Загружаем аналоги по группе аналогов
        analogs_query = text(
            """
            SELECT 
                TRIM(n.kod) AS kod,
                n.artikul,
                n.proizvoditel,
                n.edizm,
                n.stellazh,
                n.naimenovanie,
                n.pometkaudalenija,

                fs.gruppa_analogov,
                fs.type_detail,
                fs.abc,
                fs.xyz,
                fs.total_sales_last_12_months,
                fs.total_sales_last_3_months,
                fs.min_stock,

                p.tsenazakup,
                p.tsenarozn,

                mp.middleprice,
                mp.maxprice,

                s.osnsklad,
                s.zakazy_sklad,

                d.stock AS delivery_stock,
                d.price AS delivery_price,
                d.sklad AS delivery_sklad

            FROM nomenklaturaold n
            LEFT JOIN full_statistic fs ON TRIM(n.kod) = TRIM(fs.kod)
            LEFT JOIN priceold p ON TRIM(n.kod) = TRIM(p.kod)
            LEFT JOIN middlemaxprice mp ON TRIM(n.kod) = TRIM(mp.kod)
            LEFT JOIN stockold s ON TRIM(n.kod) = TRIM(s.kod)
            LEFT JOIN deliveryminprice d ON TRIM(n.kod) = TRIM(d.kod)
            WHERE fs.gruppa_analogov = :group AND TRIM(n.kod) != :kod
        """
        )

        analogs_result = conn.execute(
            analogs_query, {"group": analog_group, "kod": kod.strip()}
        )
        analogs = [dict(row._mapping) for row in analogs_result.fetchall()]
        for analog in analogs:
            analog["pometkaudalenija"] = (
                True if analog["pometkaudalenija"] == "Да" else False
            )

        data["analogs"] = analogs

        return data


@app.get("/nomenklatura/{kod}")
def get_nomenklatura_detail(kod: str):
    try:
        return get_nomenklatura_full(kod)
    except Exception as e:
        return {"error": str(e)}
