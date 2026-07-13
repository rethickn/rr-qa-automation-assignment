import pytest

from pages.discover_page import DiscoverPage
from pages.home_page import HomePage
from utils.api_helper import TMDBApiClient
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.api")


@pytest.mark.api
def test_api_discover_popular_is_well_formed(api_request):
    """
    Verify the Discover Popular API returns a valid payload.
    """

    api = TMDBApiClient(api_request)

    with allure.step("Fetch Popular movies"):
        payload = api.discover("popular", page=1)

    with allure.step("Validate API response"):

        assert payload["page"] == 1, "Expected page number should be 1"

        assert payload["total_results"] > 0, \
            "Expected total_results greater than zero"

        assert len(payload["results"]) > 0, \
            "Expected at least one movie"

        first = payload["results"][0]

        required_fields = [
            "id",
            "title",
            "poster_path",
            "vote_average"
        ]

        for field in required_fields:
            assert field in first, f"Missing required field : {field}"

        log.info(
            "Popular API returned %s movies. First movie : %s",
            len(payload["results"]),
            first["title"]
        )


@pytest.mark.api
def test_api_genre_filter_is_applied(api_request):
    """
    Verify Action genre filter is applied correctly.
    """

    api = TMDBApiClient(api_request)

    ACTION_GENRE_ID = 28

    with allure.step("Fetch Action movies"):
        payload = api.discover(
            "popular",
            genres=["Action"],
            page=1
        )

    with allure.step("Validate Action genre"):

        assert payload["results"], \
            "API returned empty results"

        for movie in payload["results"]:

            assert ACTION_GENRE_ID in movie["genre_ids"], \
                f"{movie['title']} does not contain Action genre."


@pytest.mark.api
def test_network_monitor_captures_app_traffic(
    browser_page,
    network_monitor
):
    """
    Verify application sends valid TMDB API requests.
    """

    home = HomePage(browser_page)
    discover = DiscoverPage(browser_page)

    with allure.step("Open application"):

        home.open()

    with allure.step("Open Popular category"):

        home.click_popular()

    with allure.step("Wait for results"):

        discover.wait_for_results()

    with allure.step("Validate captured network calls"):

        catalog = network_monitor.catalog_responses()

        assert catalog, \
            "No catalogue API request was captured."

        network_monitor.assert_catalog_ok()

        payload = network_monitor.last_catalog_payload()

        assert payload["page"] == 1, \
            "Expected first page"

        assert len(payload["results"]) > 0, \
            "Expected catalogue results"

        log.info(
            "Captured %s TMDB responses (%s catalogue responses)",
            len(network_monitor.tmdb_responses()),
            len(catalog)
        )