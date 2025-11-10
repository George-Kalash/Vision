WITH revenue_row AS (
    SELECT *
    FROM read_csv_auto('final_output.csv', header = TRUE) AS f
    WHERE f."concept" = 'Revenue'
),
revenue_unpivot AS (
    SELECT period, CAST(revenue AS DOUBLE) AS revenue
    FROM revenue_row
    UNPIVOT (revenue FOR period IN (
        "2013-09-29", "2014-09-28", "2015-09-27", "2016-10-02",
        "2017-10-01", "2018-09-30", "2019-09-29", "2020-09-27",
        "2021-10-03", "2022-10-02", "2023-10-01", "2024-09-29"
    ))
),
revenue_metrics AS (
    SELECT
        period,
        revenue,
        LAG(revenue) OVER (ORDER BY period) AS previous_revenue,
        AVG(revenue) OVER (ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3yr_avg,
        SUM(revenue) OVER (ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3yr_sum,
        ROW_NUMBER() OVER (ORDER BY period) AS rn,
        COUNT(*) OVER () AS total_periods
    FROM revenue_unpivot
),
revenue_growth AS (
    SELECT
        period,
        revenue,
        previous_revenue,
        rolling_3yr_avg,
        rolling_3yr_sum,
        CASE
            WHEN previous_revenue IS NOT NULL AND previous_revenue <> 0
                THEN (revenue - previous_revenue) / previous_revenue
            ELSE NULL
        END AS growth_rate,
        rn,
        total_periods
    FROM revenue_metrics
),
cagr AS (
    SELECT
        EXP(SUM(LN(1 + growth_rate)) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / rn) - 1 AS cumulative_cagr,
        period,
        revenue,
        previous_revenue,
        growth_rate,
        rolling_3yr_avg,
        rolling_3yr_sum
    FROM revenue_growth
)
SELECT
    period,
    revenue,
    previous_revenue,
    ROUND(growth_rate * 100, 2) AS growth_rate_percent,
    ROUND(rolling_3yr_avg, 2) AS rolling_3yr_avg,
    ROUND(rolling_3yr_sum, 2) AS rolling_3yr_sum,
    ROUND(cumulative_cagr * 100, 2) AS cumulative_cagr_percent,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM cagr
ORDER BY period;