"""
tasks/transform_task.py
Task Prefect responsável por executar o dbt (Bronze → Silver → Gold).
"""

import os
import subprocess
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


def _get_dbt_dir() -> Path:
    """
    Retorna o diretório do projeto dbt conforme o ambiente.
    Avaliado em runtime para garantir o path correto
    tanto no Docker quanto localmente.
    """
    # Variável de ambiente tem prioridade (Docker via .env)
    if os.getenv("DBT_PROJECT_DIR"):
        return Path(os.getenv("DBT_PROJECT_DIR"))
    # Fallback: path Docker padrão
    if os.path.exists("/app/transform"):
        return Path("/app/transform")
    # Fallback local: sobe da pasta tasks até a raiz do projeto
    return Path(__file__).resolve().parents[3] / "transform"


@task(
    name="run_dbt",
    description="Executa dbt run para transformar Bronze → Silver → Gold.",
    retries=1,
    retry_delay_seconds=10,
    tags=["transform", "dbt", "silver", "gold"],
)
def run_dbt(extracted_at: str) -> None:
    """
    Executa o pipeline dbt completo.

    Args:
        extracted_at: Timestamp do run atual (usado apenas para logging).
    """
    logger = get_run_logger()
    dbt_dir = _get_dbt_dir()

    logger.info(f"Iniciando dbt run | extracted_at={extracted_at}")
    logger.info(f"dbt project dir: {dbt_dir}")

    result = subprocess.run(
        [
            "dbt", "run",
            "--project-dir", str(dbt_dir),
            "--profiles-dir", str(dbt_dir),
        ],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )

    if result.stdout:
        for line in result.stdout.strip().splitlines():
            logger.info(f"[dbt] {line}")

    # Loga stderr sempre — pode ter warnings úteis mesmo sem erro
    if result.stderr:
        for line in result.stderr.strip().splitlines():
            logger.warning(f"[dbt stderr] {line}")

    if result.returncode != 0:
        raise RuntimeError(f"dbt run falhou com código {result.returncode}")

    logger.info("dbt run concluído com sucesso")


@task(
    name="run_dbt_test",
    description="Executa dbt test para validar os modelos Silver e Gold.",
    retries=1,
    retry_delay_seconds=5,
    tags=["test", "dbt"],
)
def run_dbt_test() -> None:
    """Roda os testes definidos no sources.yml (unique, not_null, etc.)."""
    logger = get_run_logger()
    dbt_dir = _get_dbt_dir()

    logger.info("Iniciando dbt test")

    result = subprocess.run(
        [
            "dbt", "test",
            "--project-dir", str(dbt_dir),
            "--profiles-dir", str(dbt_dir),
        ],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )

    if result.stdout:
        for line in result.stdout.strip().splitlines():
            logger.info(f"[dbt test] {line}")

    if result.stderr:
        for line in result.stderr.strip().splitlines():
            logger.warning(f"[dbt test stderr] {line}")

    if result.returncode != 0:
        # Não interrompe o pipeline — apenas avisa
        logger.warning("Alguns testes falharam — verifique os logs acima.")
    else:
        logger.info("Todos os testes passaram")