import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from config import BASE_URL, FIELDS


# -- Parametros de retry para lidar com falhas temporárias da API --

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)

# -- Funções --

def fetch_page(page: int, limit: int = 100) -> dict:

    params = {
        "page": page,
        "limit": limit,
        "fields": FIELDS,
    }

    logger.info(f"Buscando página {page} (limit={limit})")
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def fetch_all_pages(max_pages: int = None, limit: int = 100) -> list[dict]:

    all_records = []
    page = 1

    while True:
        data = fetch_page(page=page, limit=limit)
        records = data.get("data", [])
        pagination = data.get("pagination", {})

        all_records.extend(records)
        logger.info(
            f"Página {page}/{pagination.get('total_pages')} — "
            f"{len(all_records)} registros acumulados"
        )

        # Verifica se existe próxima página
        if not pagination.get("next_url"):
            logger.info("Última página atingida.")
            break

        if max_pages and page >= max_pages:
            logger.info(f"Limite de {max_pages} páginas atingido.")
            break

        page += 1

    return all_records
