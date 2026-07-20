-- silver/silver_artworks.sql
-- Limpeza, tipagem e padronização dos dados brutos
-- Remove duplicatas, trata nulos e normaliza campos de texto

WITH deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY _extracted_at DESC
        ) AS rn
    FROM {{ ref('bronze_artworks') }}
    WHERE id IS NOT NULL
),

cleaned AS (
    SELECT
        id,

        -- Texto: trim e nulos explícitos
        NULLIF(TRIM(title), '')                AS title,
        NULLIF(TRIM(artist_title), '')         AS artist_title,
        NULLIF(TRIM(artist_display), '')       AS artist_display,

        -- Datas: mantém inteiros, valida range mínimo
        CASE
            WHEN date_start BETWEEN -5000 AND 2100 THEN date_start
            ELSE NULL
        END                                     AS date_start,
        CASE
            WHEN date_end BETWEEN -5000 AND 2100 THEN date_end
            ELSE NULL
        END                                     AS date_end,
        NULLIF(TRIM(date_display), '')          AS date_display,

        -- Classificações
        NULLIF(TRIM(medium_display), '')        AS medium_display,
        NULLIF(TRIM(artwork_type_title), '')    AS artwork_type_title,
        NULLIF(TRIM(department_title), '')      AS department_title,
        NULLIF(TRIM(place_of_origin), '')       AS place_of_origin,
        NULLIF(TRIM(style_title), '')           AS style_title,
        NULLIF(TRIM(classification_title), '')  AS classification_title,
        NULLIF(TRIM(dimensions), '')            AS dimensions,
        NULLIF(TRIM(credit_line), '')           AS credit_line,

        -- Booleans com default false
        COALESCE(is_public_domain, FALSE)       AS is_public_domain,
        COALESCE(is_on_view, FALSE)             AS is_on_view,

        -- Colorfulness: nulo para valores negativos ou absurdos
        CASE
            WHEN colorfulness >= 0 THEN ROUND(colorfulness, 4)
            ELSE NULL
        END                                     AS colorfulness,

        -- term_titles: mantém como string JSON para Silver
        term_titles,

        -- Período histórico calculado a partir do date_start
        -- NULL explícito primeiro para evitar que NULLs caiam no ELSE
        CASE
            WHEN date_start IS NULL  THEN 'Período Desconhecido'
            WHEN date_start < 0      THEN 'Antes de Cristo'
            WHEN date_start < 1400   THEN 'Medieval e Anterior'
            WHEN date_start < 1600   THEN 'Renascimento'
            WHEN date_start < 1800   THEN 'Barroco e Iluminismo'
            WHEN date_start < 1900   THEN 'Século XIX'
            WHEN date_start < 1945   THEN 'Início Século XX'
            WHEN date_start < 2000   THEN 'Pós-Guerra e Contemporâneo'
            WHEN date_start >= 2000  THEN 'Século XXI'
            ELSE 'Período Desconhecido'
        END                                     AS historical_period,

        _extracted_at,
        _source

    FROM deduped
    WHERE rn = 1
)

SELECT * FROM cleaned