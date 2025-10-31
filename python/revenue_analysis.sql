-- Load the CSV and isolate the Revenue row
WITH revenue_row AS (
    SELECT *
    FROM read_csv_auto('final_output.csv', header = TRUE)
    WHERE concept = 'Revenue'
),
-- Turn the wide columns into (period, revenue) rows
revenue_unpivot AS (
    SELECT period, CAST(revenue AS DOUBLE) AS revenue
    FROM revenue_row
    UNPIVOT (revenue FOR period IN (
        "2013-09-29", "2014-09-28", "2015-09-27", "2016-10-02",
        "2017-10-01", "2018-09-30", "2019-09-29", "2020-09-27",
        "2021-10-03", "2022-10-02", "2023-10-01", "2024-09-29"
    ))
),
-- Compute period-over-period change
revenue_with_change AS (
    SELECT
        period,
        revenue,
        LAG(revenue) OVER (ORDER BY period) AS previous_revenue
    FROM revenue_unpivot
)
SELECT
    period,
    revenue,
    previous_revenue,
    CASE
        WHEN previous_revenue IS NOT NULL AND previous_revenue <> 0
            THEN ROUND((revenue - previous_revenue) / previous_revenue * 100, 2)
        ELSE NULL
    END AS revenue_change_percent
FROM revenue_with_change
ORDER BY period;