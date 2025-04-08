from sqlalchemy import text
from db_connection import get_db_engine


def get_nomenklatura_full(kod: str):
    engine = get_db_engine()
    with engine.connect() as conn:
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

        # Преобразуем "Да" / "Нет" в bool
        data["pometkaudalenija"] = True if data["pometkaudalenija"] == "Да" else False

        return data
