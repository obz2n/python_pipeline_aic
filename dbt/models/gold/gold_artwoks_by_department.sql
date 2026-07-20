-- gold/gold_artworks_by_department.sql
-- Distribuição de obras por departamento do museu

SELECT
    COALESCE(department_title, 'Não Informado')        AS department,
    COUNT(*)                                            AS total_artworks,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    COUNT(DISTINCT artist_title)                        AS total_artists,
    SUM(CASE WHEN is_on_view THEN 1 ELSE 0 END)        AS currently_on_view,
    SUM(CASE WHEN is_public_domain THEN 1 ELSE 0 END)  AS total_public_domain,
    ROUND(AVG(colorfulness), 2)                         AS avg_colorfulness
FROM {{ ref('silver_artworks') }}
GROUP BY department_title
ORDER BY total_artworks DESC