-- gold/gold_artworks_by_type.sql
-- Distribuição de obras por tipo (pintura, escultura, gravura, etc.)

SELECT
    COALESCE(artwork_type_title, 'Não Classificado')  AS artwork_type,
    COUNT(*)                                           AS total_artworks,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    SUM(CASE WHEN is_public_domain THEN 1 ELSE 0 END)  AS total_public_domain,
    ROUND(AVG(colorfulness), 2)                        AS avg_colorfulness
FROM {{ ref('silver_artworks') }}
GROUP BY artwork_type_title
ORDER BY total_artworks DESC