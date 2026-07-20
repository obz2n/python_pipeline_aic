-- gold/gold_artworks_by_period.sql
-- Distribuição de obras por período histórico

SELECT
    historical_period,
    COUNT(*)                                            AS total_artworks,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    MIN(date_start)                                     AS earliest_year,
    MAX(date_end)                                       AS latest_year,
    SUM(CASE WHEN is_public_domain THEN 1 ELSE 0 END)  AS total_public_domain,
    ROUND(AVG(colorfulness), 2)                         AS avg_colorfulness
FROM {{ ref('silver_artworks') }}
WHERE historical_period IS NOT NULL
GROUP BY historical_period
ORDER BY MIN(date_start) ASC NULLS LAST