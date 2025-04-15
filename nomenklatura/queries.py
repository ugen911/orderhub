MAIN_QUERY = """
SELECT TRIM(n.kod) AS kod, n.artikul, n.proizvoditel, n.edizm, n.stellazh,
       n.naimenovanie, n.pometkaudalenija, fs.gruppa_analogov, fs.type_detail,
       fs.abc, fs.xyz, fs.total_sales_last_12_months, fs.total_sales_last_3_months, fs.min_stock AS minimal_raschet,
       p.tsenazakup, p.tsenarozn, mp.middleprice, mp.maxprice,
       s.osnsklad, s.zakazy_sklad, d.stock AS delivery_stock, d.price AS delivery_price, d.sklad AS delivery_sklad,
       a.ne_ispolzuetsya_v_zakaze, a.nelikvid, a.zafiksirovat_minimalki, a.list_ozhidaniya, a.minimal
FROM nomenklaturaold n
LEFT JOIN full_statistic fs ON TRIM(n.kod) = TRIM(fs.kod)
LEFT JOIN priceold p ON TRIM(n.kod) = TRIM(p.kod)
LEFT JOIN middlemaxprice mp ON TRIM(n.kod) = TRIM(mp.kod)
LEFT JOIN stockold s ON TRIM(n.kod) = TRIM(s.kod)
LEFT JOIN deliveryminprice d ON TRIM(n.kod) = TRIM(d.kod)
LEFT JOIN accessdata a ON TRIM(n.kod) = TRIM(a.kod)
WHERE TRIM(n.kod) = :kod
LIMIT 1;
"""


STATS_QUERY = """
SELECT all_months.kod, all_months.year_month,
       SUM(all_months.sales) AS sales, SUM(all_months.salesum) AS salesum,
       SUM(all_months.stock) AS stock, MAX(all_months.tsena) AS tsena,
       SUM(all_months.sup) AS sup, SUM(all_months.supsum) AS supsum
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
GROUP BY all_months.kod, all_months.year_month;
"""

ORDERS_QUERY = """
SELECT data_prinatia_zakaza, artikul, edinicy_izmerenia, zakup, kolicestvo,
       summa, status, roznica, nacenka, primecanie, postavsik, sklad, oplata,
       "scet_№" AS schet_no, data_sceta
FROM orders
WHERE TRIM(kod) = :kod
ORDER BY data_prinatia_zakaza DESC;
"""

ANALOGS_QUERY = """
SELECT TRIM(n.kod) AS kod, n.artikul, n.proizvoditel, n.edizm, n.stellazh,
       n.naimenovanie, n.pometkaudalenija, fs.gruppa_analogov, fs.type_detail,
       fs.abc, fs.xyz, fs.total_sales_last_12_months, fs.total_sales_last_3_months, fs.min_stock,
       p.tsenazakup, p.tsenarozn, mp.middleprice, mp.maxprice,
       s.osnsklad, s.zakazy_sklad, d.stock AS delivery_stock, d.price AS delivery_price, d.sklad AS delivery_sklad
FROM nomenklaturaold n
LEFT JOIN full_statistic fs ON TRIM(n.kod) = TRIM(fs.kod)
LEFT JOIN priceold p ON TRIM(n.kod) = TRIM(p.kod)
LEFT JOIN middlemaxprice mp ON TRIM(n.kod) = TRIM(mp.kod)
LEFT JOIN stockold s ON TRIM(n.kod) = TRIM(s.kod)
LEFT JOIN deliveryminprice d ON TRIM(n.kod) = TRIM(d.kod)
WHERE fs.gruppa_analogov = :group AND TRIM(n.kod) != :kod;
"""
