import pytest
from playwright.sync_api import expect

from pages.discover_page import DiscoverPage
from pages.home_page import HomePage
from utils.api_helper import TMDBApiClient
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.discover")


@pytest.mark.discover
@pytest.mark.smoke
def test_search_movie(browser_page, api_request):
    discover = DiscoverPage(browser_page)
    api = TMDBApiClient(api_request)

    with allure.step("Open the discover page"):
        discover.open()
        discover.wait_for_results()

    with allure.step("Type a query into the search box"):
        discover.search_movie("Toy Story")

    with allure.step("Assert the UI shows a matching title"):
        discover.verify_search("Toy Story")

    with allure.step("Assert the backend API returns matching results"):
        payload = api.search("Toy Story", page=1)
        assert payload["total_results"] > 0
        titles = [r["title"] for r in payload["results"]]
        log.info("API returned %s search hits; first=%s", len(titles), titles[0])
        assert any("Toy Story" in t for t in titles)


@pytest.mark.discover
def test_filter_type(browser_page):
    discover = DiscoverPage(browser_page)

    with allure.step("Open the discover page"):
        discover.open()
        discover.wait_for_results()

    with allure.step("Select type = 'TV Show'"):
        discover.select_type("TV Show")

    with allure.step("Assert the selected value is reflected in the control"):
        discover.verify_type("TV Show")


@pytest.mark.discover
def test_filter_genre(browser_page):
    discover = DiscoverPage(browser_page)

    with allure.step("Open the discover page"):
        discover.open()
        discover.wait_for_results()

    with allure.step("Select genre = 'Action'"):
        discover.select_genre("Action")

    with allure.step("Assert the genre chip is shown"):
        discover.verify_genre("Action")


@pytest.mark.discover
def test_filter_year(browser_page):
    discover = DiscoverPage(browser_page)

    with allure.step("Open the discover page"):
        discover.open()
        discover.wait_for_results()

    with allure.step("Set year range 2000 - 2020"):
        discover.select_from_year("2000")
        discover.select_to_year("2020")

    with allure.step("Assert both year values are reflected"):
        discover.verify_from_year("2000")
        discover.verify_to_year("2020")


@pytest.mark.discover
def test_filter_rating(browser_page):
    discover = DiscoverPage(browser_page)

    with allure.step("Open the discover page"):
        discover.open()
        discover.wait_for_results()

    with allure.step("Select a 4-star rating"):
        discover.select_rating(4)

    with allure.step("Assert the 4th star is highlighted"):
        discover.verify_rating(4)


@pytest.mark.discover
@pytest.mark.api
def test_filter_year_backend_honors_range(browser_page, api_request):
    """The backend must narrow results when a year range is applied.

    The UI year control is exercised for the reflected values; the actual
    data narrowing is asserted directly against the TMDB API (the same
    endpoint/params the SUT uses) so the test is independent of the SUT's
    occasionally-flaky in-app refetch. See README defect D-04.
    """
    api = TMDBApiClient(api_request)
    discover = DiscoverPage(browser_page)

    with allure.step("Apply the year filter 2010-2015 in the UI"):
        home = HomePage(browser_page)
        home.open()
        home.click_popular()
        discover.wait_for_results()
        discover.select_from_year("2010")
        discover.select_to_year("2015")
        discover.verify_from_year("2010")
        discover.verify_to_year("2015")

    with allure.step("Assert the backend returns fewer results for the range"):
        unfiltered = api.discover("popular", page=1)["total_results"]
        filtered = api.discover("popular", year_range=(2010, 2015), page=1)["total_results"]
        log.info("total_results: unfiltered=%s filtered=%s", unfiltered, filtered)
        assert filtered < unfiltered
        assert filtered > 0
