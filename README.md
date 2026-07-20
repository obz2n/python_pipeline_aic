# AIC ELT Pipeline

Pipeline de dados com arquitetura medalhão utilizando a API pública do **Art Institute of Chicago**, construído como projeto de portfólio em Engenharia de Dados.

---

## Arquitetura

![img](https://i.postimg.cc/9XYc4zxp/Captura-de-tela-de-2026-03-08-22-05-55.png)


### Camadas Medalhão

| Camada | Materialização | Descrição |
|--------|---------------|-----------|
| 🥉 **Bronze** | `view` | Dados brutos da API, sem alterações. Preserva histórico. |
| 🥈 **Silver** | `table` | Limpeza, tipagem, deduplicação e campo `historical_period`. |
| 🥇 **Gold** | `table` | Agregações analíticas prontas para consumo. |

---

## Stack

| Ferramenta | Função |
|-----------|--------|
| **Python 3.11** | Extração e carga |
| **DuckDB** | Banco de dados local (warehouse) |
| **dbt-duckdb** | Transformações SQL (Silver + Gold) |
| **Prefect 2** | Orquestração do pipeline |
| **Docker** | Containerização |

---

## Estrutura de Pastas

```
aic-elt-pipeline/
├── src/
│   ├── api_client.py      # Comunicação com a API (retry + paginação)
│   ├── extractor.py       # Orquestra extração → JSON bruto → Bronze
│   └── utils.py           # Logging e helpers
│
├── data/
│   ├── raw/                   # JSONs brutos (gerado em runtime)
│   └── warehouse/
│       └── aic.duckdb         # Banco DuckDB (gerado em runtime)
│
├── docker/
│   ├── dockerfile-src
│   ├── dockerfile-prefect
│   └── dockerfile-dbt
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml
│       ├── bronze/
│       │   └── bronze_artworks.sql
│       ├── silver/
│       │   └── silver_artworks.sql
│       └── gold/
│           ├── gold_artworks_by_type.sql
│           ├── gold_artworks_by_period.sql
│           ├── gold_artworks_by_department.sql
│           └── gold_top_artists.sql
│
├── pieplines/
│   ├── requirements.txt
│   └── flows/
│       ├── main_flow.py       # Flow principal ELT
│       └── tasks/
│           ├── extract_task.py
│           ├── load_task.py
│           └── transform_task.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/aic-elt-pipeline.git
cd aic-elt-pipeline
```

### 2. Configure o ambiente

```bash
cp .env.example .env
```

Para testes rápidos, mantenha `MAX_PAGES=2` no `.env` (~200 obras).
Para extração completa (~131k obras), ajuste para `MAX_PAGES=0`.

### 3. Suba os containers

```bash
docker-compose up --build
```

O pipeline irá:
1. Subir o Prefect Server (UI disponível em `http://localhost:4200`)
2. Executar o flow: Extract → Load → dbt run → dbt test

### 4. Execução local (sem Docker)

```bash
# Extração
cd extraction
pip install -r requirements.txt
python src/extractor.py

# Transformação
cd ../transform
pip install -r requirements.txt
dbt run --profiles-dir .

# Orquestração
cd ../orchestration
pip install -r requirements.txt
python flows/main_flow.py
```

---

## Modelos Gold

| Modelo | Descrição |
|--------|-----------|
| `gold_artworks_by_type` | Distribuição por tipo de obra com % do total |
| `gold_artworks_by_period` | Obras por período histórico (Medieval → Século XXI) |
| `gold_artworks_by_department` | Obras por departamento com obras em exibição |
| `gold_top_artists` | Top 100 artistas com mais obras no acervo |

---

## Fonte de Dados

[Art Institute of Chicago API](https://api.artic.edu/docs/) — API pública com mais de 131.000 obras de arte, sem necessidade de autenticação.

---

## Autor

[Juliano Laurentino](https://www.linkedin.com/in/julianolaurentinodasilva/)
