from __future__ import annotations

import argparse
import csv
import gzip
import shutil
import urllib.request
from pathlib import Path


BASE_URL = "https://datasets.imdbws.com"
RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/imdb_titles.csv")
TITLE_BASICS = "title.basics.tsv.gz"
TITLE_RATINGS = "title.ratings.tsv.gz"
TITLE_TYPES = {"movie", "tvSeries"}


def download(filename: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    if path.exists():
        return path

    with urllib.request.urlopen(f"{BASE_URL}/{filename}") as response:
        with path.open("wb") as file:
            shutil.copyfileobj(response, file)

    return path


def load_ratings(path: Path, min_votes: int) -> dict[str, tuple[str, str]]:
    ratings: dict[str, tuple[str, str]] = {}

    with gzip.open(path, "rt", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            votes = int(row["numVotes"])
            if votes >= min_votes:
                ratings[row["tconst"]] = (row["averageRating"], row["numVotes"])

    return ratings


def build_dataset(limit: int, min_votes: int) -> None:
    ratings_path = download(TITLE_RATINGS)
    basics_path = download(TITLE_BASICS)
    ratings = load_ratings(ratings_path, min_votes)
    rows: list[dict[str, str]] = []

    with gzip.open(basics_path, "rt", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            if row["titleType"] not in TITLE_TYPES:
                continue
            if row["isAdult"] == "1":
                continue
            rating = ratings.get(row["tconst"])
            if rating is None:
                continue

            average_rating, num_votes = rating
            rows.append(
                {
                    "tconst": row["tconst"],
                    "titleType": row["titleType"],
                    "primaryTitle": row["primaryTitle"],
                    "originalTitle": row["originalTitle"],
                    "startYear": row["startYear"],
                    "runtimeMinutes": row["runtimeMinutes"],
                    "genres": row["genres"],
                    "averageRating": average_rating,
                    "numVotes": num_votes,
                }
            )

    rows.sort(key=lambda item: int(item["numVotes"]), reverse=True)
    rows = rows[:limit]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "tconst",
            "titleType",
            "primaryTitle",
            "originalTitle",
            "startYear",
            "runtimeMinutes",
            "genres",
            "averageRating",
            "numVotes",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Base gerada em {OUTPUT_FILE} com {len(rows)} titulos.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera uma base local a partir do IMDb.")
    parser.add_argument("--limit", type=int, default=50000)
    parser.add_argument("--min-votes", type=int, default=1000)
    args = parser.parse_args()
    build_dataset(limit=args.limit, min_votes=args.min_votes)


if __name__ == "__main__":
    main()
