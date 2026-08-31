from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from .models import TitleRecord
from .normalization import title_search_keys


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    query: str
    records: list[TitleRecord]
    comparisons: int
    elapsed_ms: float


def timed_search(
    algorithm: str,
    query: str,
    search_fn: Callable[[], tuple[list[TitleRecord], int]],
) -> SearchResult:
    started = perf_counter()
    records, comparisons = search_fn()
    elapsed_ms = (perf_counter() - started) * 1000
    return SearchResult(algorithm, query, records, comparisons, elapsed_ms)


def linear_prefix_search(
    records: list[TitleRecord],
    normalized_query: str,
    limit: int,
) -> tuple[list[TitleRecord], int]:
    matches: list[TitleRecord] = []
    comparisons = 0

    for record in records:
        comparisons += 1
        if any(key.startswith(normalized_query) for key in title_search_keys(record.primary_title)):
            if len(matches) < limit:
                matches.append(record)

    return matches, comparisons


def lower_bound(
    ordered_records: list[tuple[str, TitleRecord]],
    target: str,
) -> tuple[int, int]:
    left = 0
    right = len(ordered_records)
    comparisons = 0

    while left < right:
        middle = (left + right) // 2
        comparisons += 1
        if ordered_records[middle][0] < target:
            left = middle + 1
        else:
            right = middle

    return left, comparisons


def binary_prefix_search(
    ordered_records: list[tuple[str, TitleRecord]],
    normalized_query: str,
    limit: int,
) -> tuple[list[TitleRecord], int]:
    start, comparisons = lower_bound(ordered_records, normalized_query)
    end, end_comparisons = lower_bound(
        ordered_records,
        normalized_query + chr(0x10FFFF),
    )
    comparisons += end_comparisons
    matches: list[TitleRecord] = []
    seen: set[str] = set()

    for _, record in ordered_records[start:end]:
        if record.tconst in seen:
            continue
        seen.add(record.tconst)
        matches.append(record)
        if len(matches) >= limit:
            break

    return matches, comparisons


class HashTable:
    def __init__(self, capacity: int = 2048) -> None:
        self.capacity = max(8, capacity)
        self.buckets: list[list[tuple[str, list[TitleRecord]]]] = [
            [] for _ in range(self.capacity)
        ]
        self.size = 0
        self.collisions = 0

    def _hash(self, key: str) -> int:
        value = 0
        for char in key:
            value = (value * 31 + ord(char)) % self.capacity
        return value

    def insert(self, key: str, record: TitleRecord) -> None:
        if self.size / self.capacity >= 0.75:
            self._resize()

        index = self._hash(key)
        bucket = self.buckets[index]
        if bucket:
            self.collisions += 1

        for position, (stored_key, records) in enumerate(bucket):
            if stored_key == key:
                bucket[position] = (stored_key, records + [record])
                return

        bucket.append((key, [record]))
        self.size += 1

    def search(self, key: str) -> tuple[list[TitleRecord], int]:
        bucket = self.buckets[self._hash(key)]
        comparisons = 0

        for stored_key, records in bucket:
            comparisons += 1
            if stored_key == key:
                return records, comparisons

        return [], comparisons

    def _resize(self) -> None:
        entries = [
            (key, record)
            for bucket in self.buckets
            for key, records in bucket
            for record in records
        ]
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        self.collisions = 0

        for key, record in entries:
            self.insert(key, record)
