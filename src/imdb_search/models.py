from dataclasses import dataclass


@dataclass(frozen=True)
class TitleRecord:
    tconst: str
    title_type: str
    primary_title: str
    original_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: tuple[str, ...]
    average_rating: float | None
    num_votes: int | None

    @property
    def imdb_url(self) -> str:
        return f"https://www.imdb.com/title/{self.tconst}/"
