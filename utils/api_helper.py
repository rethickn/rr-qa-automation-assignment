import re
import time

"""Helpers for exercising and asserting the TMDB backend API.

The brief explicitly asks to demonstrate *browser API calls and how they are
asserted*. We support that in two complementary ways:

1. ``TMDBApiClient`` - wraps Playwright's ``APIRequestContext`` (an in-process
   HTTP client, the same engine the browser uses) so a test can call the exact
   endpoints the UI calls and assert on the JSON payload. This lets us
   cross-check "what the UI shows" against "what the API returned".

2. ``NetworkMonitor`` - attaches to a live ``Page`` and records every response
   from ``api.themoviedb.org``. A test can then assert the *real* request the
   application issued (status code, query params) matches expectations, i.e.
   we assert the network traffic the SUT generated.
"""

from utils.constants import (
    TMDB_API_BASE,
    TMDB_API_KEY,
    CATEGORY_SORT,
    genre_names_to_ids,
)
from utils.logger import get_logger

log = get_logger("utils.api_helper")


class TMDBApiClient:
    """Thin, read-only client mirroring the demo app's TMDB requests."""

    def __init__(self, request_context):
        self._api = request_context

    def _get(self, path: str, params: dict) -> dict:
        query = {"api_key": TMDB_API_KEY, **params}
        log.info("API GET %s %s", path, {k: v for k, v in params.items()})
        response = self._api.get(f"{TMDB_API_BASE}/{path}", params=query)
        assert response.status == 200, (
            f"TMDB API {path} returned HTTP {response.status}"
        )
        body = response.json()
        log.debug("API %s -> total_results=%s total_pages=%s page=%s",
                  path, body.get("total_results"),
                  body.get("total_pages"), body.get("page"))
        return body

    def discover(
        self,
        category: str = "popular",
        year_range: tuple[int, int] | None = None,
        rating_range: tuple[float, float] | None = None,
        genres: list[str] | None = None,
        page: int = 1,
    ) -> dict:
        """Replicate the app's ``discover/movie`` call.

        Mirrors the parameter construction found in the app bundle:
        sort_by (category), release_date.gte/lte (year), vote_average.gte/lte
        (rating) and with_genres.
        """
        params = {
            "sort_by": CATEGORY_SORT[category],
            "page": page,
        }
        if year_range:
            params["release_date.gte"] = f"{year_range[0]}-01-01"
            params["release_date.lte"] = f"{year_range[1]}-12-31"
        if rating_range:
            params["vote_average.gte"] = rating_range[0]
            params["vote_average.lte"] = rating_range[1]
        if genres:
            params["with_genres"] = ",".join(
                str(g) for g in genre_names_to_ids(genres)
            )
        return self._get("discover/movie", params)

    def search(self, query: str, page: int = 1) -> dict:
        return self._get("search/movie", {"query": query, "page": page})


class NetworkMonitor:
    """Records TMDB API responses emitted by the application under test."""

    # Endpoints that return catalogue items (movies/shows). Anything else
    # (e.g. /genre/... lists) is metadata, not result data.
    _CATALOG_RE = re.compile(
        r"/discover/movie|/movie/(popular|top_rated|now_playing|upcoming)"
        r"|/tv/(popular|top_rated)|/trending/|/search/movie"
    )

    def __init__(self, page):
        self._page = page
        self.responses = []
        self._handler = lambda response: self._responses_hook(response)
        page.on("response", self._handler)

    def _responses_hook(self, response):
        url = response.url
        if "api.themoviedb.org/3" in url:
            record = {
                "url": url,
                "status": response.status,
                "method": response.request.method,
                "json": None,
            }
            # Capture the JSON body so tests can compare UI <-> API exactly.
            if record["method"] == "GET" and self._CATALOG_RE.search(url):
                try:
                    record["json"] = response.json()
                except Exception:
                    record["json"] = None
            self.responses.append(record)
            log.debug("Network: %s %s -> %s",
                      record["method"], url, record["status"])

    def tmdb_responses(self) -> list[dict]:
        return self.responses

    def catalog_responses(self) -> list[dict]:
        return [r for r in self.responses if self._CATALOG_RE.search(r["url"])]

    def last_response(self) -> dict | None:
        tmdb = [r for r in self.responses if "api.themoviedb.org/3" in r["url"]]
        return tmdb[-1] if tmdb else None

    def last_catalog_payload(self) -> dict:
        """Parsed JSON of the most recent catalogue (results) call."""
        catalog = self.catalog_responses()
        assert catalog, "No TMDB catalogue response was captured"
        return catalog[-1]["json"]

    def assert_all_ok(self):
        """Assert every captured TMDB response was successful (HTTP 2xx)."""
        bad = [r for r in self.responses if r["status"] >= 400]
        assert not bad, f"Non-2xx TMDB responses observed: {bad}"

    def assert_catalog_ok(self):
        bad = [r for r in self.catalog_responses() if r["status"] >= 400]
        assert not bad, f"Non-2xx TMDB catalogue responses: {bad}"

    def last_discover_params(self) -> dict:
        """Parse query params of the most recent discover/movie call."""
        import urllib.parse

        discover = [r for r in self.responses if "discover/movie" in r["url"]]
        assert discover, "No discover/movie call was captured"
        url = discover[-1]["url"]
        return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))

    def wait_for_discover_params(self, expected: dict, timeout: int = 10000):
        """Poll until the most recent discover/movie call carries ``expected``
        query params. Guards against reading the network before the SUT has
        issued the request that reflects the latest UI action."""
        deadline = time.time() + timeout / 1000
        last_seen = None
        while time.time() < deadline:
            try:
                last_seen = self.last_discover_params()
                if all(last_seen.get(k) == v for k, v in expected.items()):
                    return
            except AssertionError:
                pass
            time.sleep(0.2)
        raise AssertionError(
            f"discover/movie params never matched {expected}; last seen {last_seen}"
        )

    def wait_for_catalog_page(self, page: int, timeout: int = 10000):
        """Poll until the most recent catalogue payload is for ``page``."""
        deadline = time.time() + timeout / 1000
        last_seen = None
        while time.time() < deadline:
            catalog = self.catalog_responses()
            if catalog and catalog[-1]["json"]:
                last_seen = catalog[-1]["json"].get("page")
                if last_seen == page:
                    return
            time.sleep(0.2)
        raise AssertionError(
            f"catalog page never reached {page}; last seen {last_seen}"
        )

    def detach(self):
        try:
            self._page.remove_listener("response", self._handler)
        except Exception:
            pass
