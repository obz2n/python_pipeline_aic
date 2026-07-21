"""
tasks/extract_task.py
Task Prefect responsável pela extração da API do AIC.
"""

import sys
from pathlib import Path

from prefect import task
from loguru import logger

# Permite importar o módulo de extração
sys.path.append(str(Path(__file__).resolve().parents[3] / "extraction" / "src"))  # local
sys.path.append("/app/extraction/src")  # docker

from api_client import fetch_all_pages


@task(
    name="extract_artworks",
    description="Extrai obras de arte da API do Art Institute of Chicago.",
    retries=3,
    retry_delay_seconds=10,
    tags=["extract", "api"],
)
def extract_artworks(max_pages: int = None) -> list[dict]:
    """
    Busca todos os registros da API do AIC.

    Args:
        max_pages: Limite de páginas (None = todas). Use 2-3 para testes.

    Returns:
        Lista de dicts com os registros brutos.
    """
    logger.info(f"Iniciando extração | max_pages={max_pages}")
    records = fetch_all_pages(max_pages=max_pages)
    logger.info(f"Extração concluída: {len(records)} registros")
    return records