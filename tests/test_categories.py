import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.categories")

CATEGORIES = [
    ("popular", "/popular"),
    ("trending", "/trend"),
    ("newest", "/new"),
    ("top_rated", "/top"),
]


@pytest.mark.categories
@pytest.mark.parametrize(
    "name, slug",
    CATEGORIES,
    ids=[c[0] for c in CATEGORIES],
)
def test_category_navigation(browser_page, name, slug):
    """Clicking a category tab routes to the matching slug and loads results."""
    home = HomePage(browser_page)

    with allure.step(f"Open home and click '{name}'"):
        home.open()
        getattr(home, f"click_{name}")()

    with allure.step("Assert the URL ends with the expected slug"):
        # Auto-wait for the SPA route to settle (guards intermittent races).
        expect(browser_page).to_have_url(re.compile(rf".*{re.escape(slug)}$"))
        log.info("Navigated to %s", browser_page.url)

    with allure.step("Assert the result grid rendered"):
        from pages.discover_page import DiscoverPage

        DiscoverPage(browser_page).wait_for_results()
