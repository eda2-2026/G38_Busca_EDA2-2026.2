import re
import unicodedata


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower().strip())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def title_search_keys(title: str) -> tuple[str, ...]:
    normalized = normalize_text(title)
    if not normalized:
        return ()

    words = normalized.split()
    keys = [normalized]

    if words[0] in {"the", "a", "an", "o", "os", "as", "um", "uma"} and len(words) > 1:
        keys.append(" ".join(words[1:]))

    for index in range(1, len(words)):
        keys.append(" ".join(words[index:]))

    return tuple(dict.fromkeys(keys))
