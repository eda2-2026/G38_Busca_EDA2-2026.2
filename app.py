from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from imdb_search import SearchEngine, load_titles
from imdb_search.algorithms import SearchResult
from imdb_search.dataset import DEFAULT_DATASET


st.set_page_config(page_title="Buscador de Filmes", layout="wide")


@st.cache_resource(show_spinner=False)
def get_engine(path: str) -> SearchEngine:
    return SearchEngine(load_titles(path))


def format_records(result: SearchResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Titulo": record.primary_title,
                "Tipo": record.title_type,
                "Ano": record.start_year,
                "Generos": ", ".join(record.genres),
                "Nota": record.average_rating,
                "Votos": record.num_votes,
                "IMDb": record.imdb_url,
            }
            for record in result.records
        ]
    )


def metric_row(result: SearchResult) -> None:
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Resultados", len(result.records))
    col_b.metric("Comparacoes", f"{result.comparisons:,}".replace(",", "."))
    col_c.metric("Tempo", f"{result.elapsed_ms:.4f} ms")


st.title("Buscador de Filmes")
st.caption("Busca de filmes e series reais do IMDb com estruturas implementadas em memoria.")

dataset_path = ROOT / DEFAULT_DATASET
if not dataset_path.exists():
    st.warning("A base processada ainda nao foi gerada.")
    st.code("py scripts/build_dataset.py --limit 50000", language="powershell")
    st.stop()

engine = get_engine(str(dataset_path))

with st.sidebar:
    st.header("Base carregada")
    st.metric("Titulos", f"{len(engine.records):,}".replace(",", "."))
    st.metric("Buckets da hash", f"{engine.hash_table.capacity:,}".replace(",", "."))
    st.metric("Colisoes", f"{engine.hash_table.collisions:,}".replace(",", "."))

query = st.text_input("Titulo, palavra ou prefixo", value="matrix")
algorithm = st.radio(
    "Algoritmo",
    ["Busca Sequencial", "Busca Binaria por Prefixo", "Tabela Hash"],
    horizontal=True,
)
limit = st.slider("Limite de resultados", min_value=5, max_value=100, value=25, step=5)

if not query.strip():
    st.info("Digite um termo para iniciar a busca.")
    st.stop()

if algorithm == "Busca Sequencial":
    result = engine.linear(query, limit)
    metric_row(result)
    st.dataframe(format_records(result), use_container_width=True, hide_index=True)
elif algorithm == "Busca Binaria por Prefixo":
    result = engine.binary(query, limit)
    metric_row(result)
    st.dataframe(format_records(result), use_container_width=True, hide_index=True)
elif algorithm == "Tabela Hash":
    result = engine.hash_exact(query)
    metric_row(result)
    st.dataframe(format_records(result), use_container_width=True, hide_index=True)
