"""
extractor.py
Orquestra a extração: chama o api_client, salva o JSON bruto
e carrega os dados na camada Bronze do DuckDB.
"""

import json
import os
from pathlib import Path

import duckdb
from loguru import logger


def save_raw_json(records: list[dict], extracted_at_str: str) -> Path:
    """
    Persiste os registros brutos em JSON para auditoria.

    Args:
        records:          Lista de dicts retornada pela API.
        extracted_at_str: Timestamp formatado para uso no nome do arquivo.

    Returns:
        Caminho do arquivo JSON gerado.
    """
    raw_data_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    filename = raw_data_dir / f"artworks_{extracted_at_str}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info(f"JSON bruto salvo em: {filename}")
    return filename


def load_to_bronze(records: list[dict], extracted_at: datetime) -> None:
    """
    Carrega os registros brutos na tabela bronze.raw_artworks do DuckDB.
    Cria o schema e a tabela se não existirem.
    Ignora registros cujo id já existe na tabela (evita duplicatas).

    Args:
        records:      Lista de dicts retornada pela API.
        extracted_at: Datetime UTC do momento da extração.
    """
    duckdb_path = Path(os.getenv("DUCKDB_PATH", "data/warehouse/aic.duckdb"))
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    # Context manager garante fechamento mesmo em caso de erro
    with duckdb.connect(str(duckdb_path)) as con:

        con.execute("CREATE SCHEMA IF NOT EXISTS bronze")

        con.execute("""
            CREATE TABLE IF NOT EXISTS bronze.raw_artworks (
                id                   INTEGER,
                title                VARCHAR,
                artist_title         VARCHAR,
                artist_display       VARCHAR,
                date_start           INTEGER,
                date_end             INTEGER,
                date_display         VARCHAR,
                medium_display       VARCHAR,
                artwork_type_title   VARCHAR,
                department_title     VARCHAR,
                place_of_origin      VARCHAR,
                is_public_domain     BOOLEAN,
                is_on_view           BOOLEAN,
                colorfulness         DOUBLE,
                style_title          VARCHAR,
                classification_title VARCHAR,
                term_titles          VARCHAR,
                dimensions           VARCHAR,
                credit_line          VARCHAR,
                _extracted_at        TIMESTAMP,
                _source              VARCHAR
            )
        """)

        # Proteção contra duplicatas: busca ids já existentes na tabela
        existing_ids = {
            row[0]
            for row in con.execute(
                "SELECT id FROM bronze.raw_artworks"
            ).fetchall()
        }

        rows = []
        for r in records:
            if r.get("id") in existing_ids:
                continue
            rows.append((
                r.get("id"),
                r.get("title"),
                r.get("artist_title"),
                r.get("artist_display"),
                r.get("date_start"),
                r.get("date_end"),
                r.get("date_display"),
                r.get("medium_display"),
                r.get("artwork_type_title"),
                r.get("department_title"),
                r.get("place_of_origin"),
                r.get("is_public_domain"),
                r.get("is_on_view"),
                r.get("colorfulness"),
                r.get("style_title"),
                r.get("classification_title"),
                json.dumps(r.get("term_titles", []), ensure_ascii=False),
                r.get("dimensions"),
                r.get("credit_line"),
                extracted_at,        # datetime object → DuckDB TIMESTAMP
                "api.artic.edu",
            ))

        if not rows:
            logger.info(
                "Nenhum registro novo para inserir — "
                "todos já existem no Bronze."
            )
            return

        con.executemany("""
            INSERT INTO bronze.raw_artworks VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, rows)

        total = con.execute(
            "SELECT COUNT(*) FROM bronze.raw_artworks"
        ).fetchone()[0]

        logger.info(
            f"Bronze carregado: {len(rows)} novos registros | "
            f"Total na tabela: {total}"
        )
