from __future__ import annotations

import csv
from pathlib import Path

from .models import TitleRecord


DEFAULT_DATASET = Path("data/imdb_titles.csv")


def parse_int(value: str) -> int | None:
    if not value or value == r"\N":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value: str) -> float | None:
    if not value or value == r"\N":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_genres(value: str) -> tuple[str, ...]:
    if not value or value == r"\N":
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def load_titles(path: str | Path = DEFAULT_DATASET) -> list[TitleRecord]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(dataset_path)

    with dataset_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            TitleRecord(
                tconst=row["tconst"],
                title_type=row["titleType"],
                primary_title=row["primaryTitle"],
                original_title=row["originalTitle"],
                start_year=parse_int(row["startYear"]),
                runtime_minutes=parse_int(row["runtimeMinutes"]),
                genres=parse_genres(row["genres"]),
                average_rating=parse_float(row.get("averageRating", "")),
                num_votes=parse_int(row.get("numVotes", "")),
            )
            for row in reader
        ]
