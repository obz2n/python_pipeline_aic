from datetime import datetime, timezone
from loguru import logger

from api_client import fetch_all_pages
from extractor import save_bronze_json, load_to_bronze

# ============================================================
# Pipeline principal
# ============================================================

def run() -> None:
    """
    Ponto de entrada da extração.
    Carrega variáveis de ambiente, extrai da API,
    salva JSON bruto e persiste normalizado no Bronze.
    """
    # Timestamp UTC da extração
    extracted_at = datetime.now(timezone.utc)
    extracted_at_str = extracted_at.strftime("%Y%m%dT%H%M%SZ")

    logger.info(f"Extração iniciada em {extracted_at_str}")
    # Extrai todos os registros da API
    records = fetch_all_pages()
    logger.info(f"Extração concluída: {len(records)} registros obtidos.")

    logger.info("Salvando registros brutos e carregando no Bronze...")
    # Salva JSON bruto para auditoria
    save_bronze_json(records, extracted_at_str)
    logger.info("Registros brutos salvos com sucesso.")

    logger.info("Carregando registros no Bronze do DuckDB...")
    # Persiste no Bronze do DuckDB
    load_to_bronze(records, extracted_at)
    logger.info("Registros carregados no Bronze com sucesso.")
    logger.info("Pipeline de extração concluído.")

    resumo = {
        "extracted_at": extracted_at_str,
        "total_records": len(records),
    }
    logger.info(f"Resumo da extração: {resumo}")

if __name__ == "__main__":
    run()
