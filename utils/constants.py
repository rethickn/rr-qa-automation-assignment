# ---------------------------------------------------------------------------
# Application under test
# ---------------------------------------------------------------------------
BASE_URL = "https://tmdb-discover.surge.sh/"

# Default Playwright wait ceiling (ms)
TIMEOUT = 10000

# ---------------------------------------------------------------------------
# Backend API (the demo proxies to the public TMDB API). The API key is NOT
# hardcoded here - it must be supplied via the TMDB_API_KEY environment variable
# (e.g. export TMDB_API_KEY=... or a local .env file). A read-only demo key is
# fine; never commit a real secret.
# ---------------------------------------------------------------------------
import os
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (no external dependency). Reads KEY=VALUE pairs from
    a local .env file and imports any that are not already set in the
    environment, so a project-local .env works without manual `export`.
    Comments and blank lines are ignored.
    """
    try:
        with open(Path(path), "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
    except FileNotFoundError:
        return


_load_dotenv()

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise RuntimeError(
        "TMDB_API_KEY environment variable is not set. Export it "
        "(export TMDB_API_KEY=your_key), or create a local .env file "
        "(see .env.example) before running the tests."
    )
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"

# How the UI maps its category tabs to a TMDB `sort_by` value.
CATEGORY_SORT = {
    "popular": "popularity.desc",
    "trend": "vote_count.desc",
    "new": "release_date.desc",
    "top": "vote_average.desc",
}

# Slugs the home page links to (also used by the negative slug tests).
CATEGORY_SLUGS = {
    "popular": "/popular",
    "trending": "/trend",
    "newest": "/new",
    "top_rated": "/top",
}

# TMDB movie genre id <-> name mapping (static reference catalogue).
GENRE_IDS = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "SciFi": 878,
    "TV": 10770,
    "Thriller": 53,
    "War": 10752,
    "Western": 37,
}


def genre_name_to_id(name: str) -> int:
    return GENRE_IDS[name]


def genre_names_to_ids(names) -> list[int]:
    return [GENRE_IDS[n] for n in names]
