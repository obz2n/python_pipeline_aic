
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

from api_client import fetch_all_pages
from extractor import save_raw_json, load_to_bronze
from loguru import logger


# ============================================================
# Pipeline principal
# ============================================================

def run() -> None:
    """
    Ponto de entrada da extração.
    Carrega variáveis de ambiente, extrai da API,
    salva JSON bruto e persiste no Bronze.
    """
    # Carrega .env aqui para garantir que as variáveis estejam disponíveis
    # independente de como o módulo foi importado (ex: pelo Prefect)
    load_dotenv()

    max_pages = int(os.getenv("MAX_PAGES", 0)) or None

    extracted_at     = datetime.now(timezone.utc)
    extracted_at_str = extracted_at.strftime("%Y%m%dT%H%M%SZ")

    logger.info(f"Iniciando extração — {extracted_at_str}")

    records = fetch_all_pages(max_pages=max_pages)
    logger.info(f"Total extraído da API: {len(records)} registros")

    save_raw_json(records, extracted_at_str)
    load_to_bronze(records, extracted_at)

    logger.info("Extração concluída com sucesso.")


if __name__ == "__main__":
    run()
