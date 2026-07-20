-- bronze/bronze_artworks.sql
-- View sobre a tabela bruta carregada pelo extractor.py
-- Nenhuma transformação — apenas expõe os dados como vieram da API

SELECT
    id,
    title,
    artist_title,
    artist_display,
    date_start,
    date_end,
    date_display,
    medium_display,
    artwork_type_title,
    department_title,
    place_of_origin,
    is_public_domain,
    is_on_view,
    colorfulness,
    style_title,
    classification_title,
    term_titles,
    dimensions,
    credit_line,
    _extracted_at,
    _source
FROM bronze.raw_artworks