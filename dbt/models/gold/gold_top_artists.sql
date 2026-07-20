-- gold/gold_top_artists.sql
-- Artistas com mais obras no acervo

SELECT
    COALESCE(artist_title, 'Desconhecido / Anônimo')   AS artist,
    COUNT(*)                                            AS total_artworks,
    COUNT(DISTINCT department_title)                    AS departments_count,
    COUNT(DISTINCT artwork_type_title)                  AS types_count,
    MIN(date_start)                                     AS earliest_work,
    MAX(date_end)                                       AS latest_work,
    SUM(CASE WHEN is_public_domain THEN 1 ELSE 0 END)  AS total_public_domain,
    ROUND(AVG(colorfulness), 2)                         AS avg_colorfulness
FROM {{ ref('silver_artworks') }}
GROUP BY artist_title
ORDER BY total_artworks DESC
LIMIT 100