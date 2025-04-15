MAIN_QUERY = """
SELECT n.kod AS kod, n.artikul, n.proizvoditel, n.edizm, n.stellazh,
       n.naimenovanie, n.pometkaudalenija, fs.gruppa_analogov, fs.type_detail,
       fs.abc, fs.xyz, fs.total_sales_last_12_months, fs.total_sales_last_3_months, fs.min_stock AS minimal_raschet,
       p.tsenazakup, p.tsenarozn, mp.middleprice, mp.maxprice,
       s.osnsklad, s.zakazy_sklad, d.stock AS delivery_stock, d.price AS delivery_price, d.sklad AS delivery_sklad,
       a.ne_ispolzuetsya_v_zakaze, a.nelikvid, a.zafiksirovat_minimalki, a.list_ozhidaniya, a.minimal
FROM nomenklaturaold n
LEFT JOIN full_statistic fs ON n.kod = fs.kod
LEFT JOIN priceold p ON n.kod = p.kod
LEFT JOIN middlemaxprice mp ON n.kod = mp.kod
LEFT JOIN stockold s ON n.kod = s.kod
LEFT JOIN deliveryminprice d ON n.kod = d.kod
LEFT JOIN accessdata a ON n.kod = a.kod
WHERE n.kod = :kod
LIMIT 1;
"""


STATS_QUERY = """
SELECT kod, year_month,
       SUM(all_months.sales) AS sales, SUM(all_months.salesum) AS salesum,
       SUM(all_months.stock) AS stock, MAX(all_months.tsena) AS tsena,
       SUM(all_months.sup) AS sup, SUM(all_months.supsum) AS supsum
FROM (
    SELECT kod, year_month, kolichestvo AS sales, summa AS salesum, 0 AS stock, 0 AS tsena, 0 AS sup, 0 AS supsum FROM salespivot
    UNION ALL
    SELECT nomenklaturakod AS kod, month AS year_month, 0, 0, balance, 0, 0, 0 FROM stockendmonth
    UNION ALL
    SELECT kod, data AS year_month, 0, 0, 0, tsena, 0, 0 FROM priceendmonth
    UNION ALL
    SELECT kod, year_month, 0, 0, 0, 0, kolichestvo, summa FROM suppliespivot
) all_months
WHERE all_months.kod = :kod AND all_months.year_month IN :months
GROUP BY all_months.kod, all_months.year_month;
"""


ORDERS_QUERY = """
SELECT data_prinatia_zakaza, artikul, edinicy_izmerenia, zakup, kolicestvo,
       summa, status, roznica, nacenka, primecanie, postavsik, sklad, oplata,
       "scet_№" AS schet_no, data_sceta
FROM orders
WHERE kod = :kod
ORDER BY data_prinatia_zakaza DESC;
"""

ANALOGS_QUERY = """
SELECT n.kod AS kod, n.artikul, n.proizvoditel, n.edizm, n.stellazh,
       n.naimenovanie, n.pometkaudalenija, fs.gruppa_analogov, fs.type_detail,
       fs.abc, fs.xyz, fs.total_sales_last_12_months, fs.total_sales_last_3_months, fs.min_stock,
       p.tsenazakup, p.tsenarozn, mp.middleprice, mp.maxprice,
       s.osnsklad, s.zakazy_sklad, d.stock AS delivery_stock, d.price AS delivery_price, d.sklad AS delivery_sklad
FROM nomenklaturaold n
LEFT JOIN full_statistic fs ON n.kod = fs.kod
LEFT JOIN priceold p ON n.kod = p.kod
LEFT JOIN middlemaxprice mp ON n.kod = mp.kod
LEFT JOIN stockold s ON n.kod = s.kod
LEFT JOIN deliveryminprice d ON n.kod = d.kod
WHERE fs.gruppa_analogov = :group AND n.kod != :kod;
"""
