from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from imdb_search.models import TitleRecord
from imdb_search.search_engine import SearchEngine


def record(tconst: str, title: str, year: int) -> TitleRecord:
    return TitleRecord(
        tconst=tconst,
        title_type="movie",
        primary_title=title,
        original_title=title,
        start_year=year,
        runtime_minutes=120,
        genres=("Action",),
        average_rating=8.0,
        num_votes=1000,
    )


def test_linear_and_binary_find_same_prefix_results() -> None:
    engine = SearchEngine(
        [
            record("tt1", "Matrix", 1999),
            record("tt2", "Matrix Reloaded", 2003),
            record("tt3", "Batman Begins", 2005),
        ]
    )

    linear = engine.linear("mat", limit=10)
    binary = engine.binary("mat", limit=10)

    assert [item.primary_title for item in linear.records] == [
        item.primary_title for item in binary.records
    ]
    assert len(binary.records) == 2


def test_hash_search_is_exact_after_normalization() -> None:
    engine = SearchEngine([record("tt1", "O Auto da Compadecida", 2000)])
    result = engine.hash_exact("o auto da compadecida")

    assert len(result.records) == 1
    assert result.records[0].tconst == "tt1"


def test_hash_search_does_not_return_prefix() -> None:
    engine = SearchEngine([record("tt1", "Matrix", 1999)])
    result = engine.hash_exact("mat")

    assert result.records == []


def test_search_ignores_leading_article_in_title_keys() -> None:
    engine = SearchEngine([record("tt1", "The Matrix", 1999)])

    assert engine.linear("matrix", limit=10).records[0].primary_title == "The Matrix"
    assert engine.binary("matrix", limit=10).records[0].primary_title == "The Matrix"
    assert engine.hash_exact("matrix").records[0].primary_title == "The Matrix"
