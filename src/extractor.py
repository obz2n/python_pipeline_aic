"""
extractor.py
Orquestra a extração: chama o api_client, salva o JSON bruto
e carrega os dados na camada Bronze do DuckDB.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import duckdb
from loguru import logger

from config import DUCKDB_PATH, BRONZE_PATH

# =================================================================
# -- Funções de extração e carga --
# =================================================================

def save_bronze_json(records: list[dict], extracted_at_str: str) -> Path:
    """
    Persiste os registros brutos em JSON para auditoria.

    Args:
        records:          Lista de dicts retornada pela API.
        extracted_at_str: Timestamp formatado para uso no nome do arquivo.

    Returns:
        Caminho do arquivo JSON gerado.
    """
    bronze_data_dir = Path(os.getenv("BRONZE_PATH", BRONZE_PATH))
    bronze_data_dir.mkdir(parents=True, exist_ok=True)

    filename = bronze_data_dir / f"artworks_{extracted_at_str}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info(f"JSON bruto salvo em: {filename}")
    return filename


def load_to_bronze(records: list[dict], extracted_at: datetime) -> None:
    """
    Carrega registros brutos na tabela bronze.raw_artworks do DuckDB.
    Cria dinamicamente o schema com todas as colunas dos dados.
    Adiciona colunas novas conforme necessário.
    Mantém proteção contra duplicatas por id.

    Args:
        records:      Lista de dicts retornada pela API.
        extracted_at: Datetime UTC do momento da extração.
    """
    if not records:
        logger.warning("Nenhum registro para inserir.")
        return

    duckdb_path = Path(os.getenv("DUCKDB_PATH", DUCKDB_PATH))
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(duckdb_path)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS bronze")

        # Detecta todas as colunas únicas nos dados
        all_keys = set()
        for r in records:
            all_keys.update(r.keys())
        all_keys = sorted(all_keys)

        # Verifica se tabela existe
        table_exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'bronze' AND table_name = 'bronze_artworks'"
        ).fetchone()[0] > 0

        if not table_exists:
            # Cria tabela com todas as colunas detectadas
            columns_def = ", ".join([f"{key} VARCHAR" for key in all_keys])
            con.execute(f"""
                CREATE TABLE bronze.bronze_artworks (
                    {columns_def},
                    _extracted_at TIMESTAMP,
                    _source VARCHAR
                )
            """)
            logger.info(f"Tabela criada com {len(all_keys)} colunas: {all_keys}")
        else:
            # Verifica quais colunas existem e adiciona as novas
            existing_cols = {
                row[0]
                for row in con.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'bronze' AND table_name = 'bronze_artworks'"
                ).fetchall()
            }

            new_cols = sorted(set(all_keys) - existing_cols)
            for col in new_cols:
                con.execute(f"ALTER TABLE bronze.bronze_artworks ADD COLUMN {col} VARCHAR")
                logger.info(f"Coluna adicionada: {col}")

        # Proteção contra duplicatas: busca ids já existentes
        try:
            existing_ids = {
                str(row[0])
                for row in con.execute(
                    "SELECT id FROM bronze.bronze_artworks WHERE id IS NOT NULL"
                ).fetchall()
            }
        except Exception as e:
            logger.warning(f"Erro ao buscar ids existentes: {e}")
            existing_ids = set()

        # Filtra registros novos
        new_records = [
            r for r in records
            if str(r.get("id", "")) not in existing_ids
        ]

        if not new_records:
            logger.info(
                "Nenhum registro novo para inserir — "
                "todos já existem no Bronze."
            )
            return

        # Prepara linhas para inserção
        rows = []
        for r in new_records:
            row = tuple(
                json.dumps(r.get(key), ensure_ascii=False)
                if isinstance(r.get(key), (list, dict))
                else str(r.get(key)) if r.get(key) is not None else ""
                for key in all_keys
            ) + (extracted_at, "api.artic.edu")
            rows.append(row)

        # Executa inserção dinâmica
        placeholders = ", ".join(["?" for _ in range(len(all_keys) + 2)])
        con.executemany(
            f"INSERT INTO bronze.bronze_artworks VALUES ({placeholders})",
            rows
        )

        total = con.execute(
            "SELECT COUNT(*) FROM bronze.bronze_artworks"
        ).fetchone()[0]

        logger.info(
            f"Bronze carregado: {len(new_records)} novos registros | "
            f"Total na tabela: {total}"
        )
