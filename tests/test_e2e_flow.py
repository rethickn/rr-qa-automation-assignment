"""End-to-end user journey.

A user lands on the discover page, narrows the catalogue to movies released
between 2001 and 2025 using the year filter, and then picks the *second* movie
shown on screen.

The flow is validated both at the UI level (the filter control reflects the
chosen years and the chosen card renders its details) and at the backend level
(the same TMDB year-range query the app uses returns results), mirroring the
cross-check style used elsewhere in the suite.
"""

import pytest
from playwright.sync_api import expect

from pages.discover_page import DiscoverPage
from pages.home_page import HomePage
from utils.api_helper import TMDBApiClient
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.e2e_flow")

YEAR_FROM = "2001"
YEAR_TO = "2025"


@pytest.mark.e2e
@pytest.mark.smoke
def test_user_filters_by_year_and_selects_second_movie(browser_page, api_request):
    home = HomePage(browser_page)
    discover = DiscoverPage(browser_page)
    api = TMDBApiClient(api_request)

    with allure.step("Open the discover page"):
        home.open()
        discover.wait_for_results()

    with allure.step(f"Apply year filter {YEAR_FROM} - {YEAR_TO}"):
        discover.select_from_year(YEAR_FROM)
        discover.select_to_year(YEAR_TO)
        # The control must reflect the user's selection.
        discover.verify_from_year(YEAR_FROM)
        discover.verify_to_year(YEAR_TO)

    with allure.step(f"Assert the backend honours the {YEAR_FROM}-{YEAR_TO} range"):
        # Cross-check the filter at the data layer (the SUT's in-app refetch can
        # be flaky - see D-02 - so the narrowing is asserted against the API).
        filtered = api.discover(
            "popular", year_range=(int(YEAR_FROM), int(YEAR_TO)), page=1
        )["total_results"]
        log.info("total_results for %s-%s: %s", YEAR_FROM, YEAR_TO, filtered)
        assert filtered > 0, f"Year range {YEAR_FROM}-{YEAR_TO} returned no results"

    with allure.step("Read the second movie's details from the grid"):
        # Let any late in-app refetch of the filtered grid settle first, so the
        # card we read is the one actually shown when we click it (avoids a
        # read/click race caused by the SUT's async data load).
        browser_page.wait_for_timeout(1000)
        title = discover.result_title(1)  # 0-based index -> 2nd movie
        meta = discover.result_meta(1)
        log.info("Second movie on screen: %s (%s)", title, meta)
        assert title, "Second movie has no title"
        assert meta, "Second movie has no genre/year metadata"

    with allure.step("Choose (click) the second movie"):
        discover.click_result(1)
        # The SUT cards are not navigable; selecting keeps the card on screen.
        expect(discover.result_card(1)).to_be_visible()

    with allure.step("Assert the chosen movie is the one we read"):
        assert discover.result_title(1) == title, \
            "Chosen movie changed after selection"


@pytest.mark.e2e
@pytest.mark.known_issue
@pytest.mark.xfail(
    strict=False,
    reason="D-03: the UI year filter (2001-2025) leaks out-of-range titles "
    "(e.g. 2026, and often 1978/1979) into the grid because the SUT's "
    "in-app refetch does not reliably honour the year bounds. Expected "
    "failure = website defect reproduced; when the SUT refetch happens to "
    "succeed the test XPASSes (still green).",
)
def test_year_filter_excludes_out_of_range_movies(browser_page):
    """BUG D-03: applying the year filter 2001-2025 still shows 2026 movies.

    A user narrows the catalogue to 2001-2025. Every visible result must fall
    inside that range. The SUT instead leaks at least one out-of-range title
    into the grid, so this assertion FAILS - it is a website defect, not a
    test error. See answers.md (defect D-03).
    """
    home = HomePage(browser_page)
    discover = DiscoverPage(browser_page)

    with allure.step("Open the discover page"):
        home.open()
        discover.wait_for_results()

    with allure.step(f"Apply year filter {YEAR_FROM} - {YEAR_TO}"):
        discover.select_from_year(YEAR_FROM)
        discover.select_to_year(YEAR_TO)
        discover.verify_from_year(YEAR_FROM)
        discover.verify_to_year(YEAR_TO)

    with allure.step(f"Assert every visible movie is within {YEAR_FROM}-{YEAR_TO}"):
        offenders = discover.out_of_range_years(int(YEAR_FROM), int(YEAR_TO))
        log.info("Out-of-range years shown after filter: %s", offenders)
        assert not offenders, (
            f"Year filter {YEAR_FROM}-{YEAR_TO} leaked out-of-range movies: "
            f"{offenders}"
        )
