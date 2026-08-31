from .algorithms import (
    HashTable,
    SearchResult,
    binary_prefix_search,
    linear_prefix_search,
    timed_search,
)
from .models import TitleRecord
from .normalization import normalize_text, title_search_keys


class SearchEngine:
    def __init__(self, records: list[TitleRecord]) -> None:
        self.records = records
        self.ordered_records = sorted(
            [
                (key, record)
                for record in records
                for key in title_search_keys(record.primary_title)
                if key
            ],
            key=lambda item: item[0],
        )
        self.hash_table = HashTable(capacity=max(2048, len(records) * 2))

        for normalized_title, record in self.ordered_records:
            self.hash_table.insert(normalized_title, record)

    def linear(self, query: str, limit: int = 25) -> SearchResult:
        normalized_query = normalize_text(query)
        return timed_search(
            "Busca Sequencial",
            query,
            lambda: linear_prefix_search(self.records, normalized_query, limit),
        )

    def binary(self, query: str, limit: int = 25) -> SearchResult:
        normalized_query = normalize_text(query)
        return timed_search(
            "Busca Binaria por Prefixo",
            query,
            lambda: binary_prefix_search(self.ordered_records, normalized_query, limit),
        )

    def hash_exact(self, query: str) -> SearchResult:
        normalized_query = normalize_text(query)
        return timed_search(
            "Tabela Hash",
            query,
            lambda: self.hash_table.search(normalized_query),
        )
