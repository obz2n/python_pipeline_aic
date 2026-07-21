"""
tasks/load_task.py
Task Prefect responsável por salvar o JSON bruto e carregar no Bronze.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from prefect import task
from loguru import logger

sys.path.append(str(Path(__file__).resolve().parents[3] / "extraction" / "src"))  # local
sys.path.append("/app/extraction/src")  # docker

from extractor import save_raw_json, load_to_bronze


@task(
    name="load_to_bronze",
    description="Salva JSON bruto em disco e carrega na camada Bronze do DuckDB.",
    retries=2,
    retry_delay_seconds=5,
    tags=["load", "bronze", "duckdb"],
)
def load_artworks(records: list[dict]) -> str:
    """
    Persiste os registros brutos e carrega no Bronze.

    Args:
        records: Lista de dicts retornada pela extract_task.

    Returns:
        Timestamp da extração no formato ISO (usado como identificador do run).
    """
    extracted_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    logger.info(f"Salvando JSON bruto | extracted_at={extracted_at}")
    save_raw_json(records, extracted_at)

    logger.info("Carregando registros no Bronze")
    load_to_bronze(records, extracted_at)

    return extracted_at