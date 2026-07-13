"""Negative tests for direct / deep-link slug access.

KNOWN ISSUE (brief): "Refreshing / accessing the page using specific slugs
(e.g. /popular) may not work as expected."

Diagnosis (see README 'Defects'): a hard navigation / refresh to any category
slug renders an **empty page** - no genre list is fetched and no results grid
is rendered (the SPA's initial data-load effect does not run on a deep link,
even though the catch-all route mounts the component). Clicking the same tab
from the home page works fine, which isolates the defect to slug access.

These tests pin that behaviour: they expect the *correct* behaviour (results
load) and therefore FAIL on the demo, producing a screenshot attachment and a
reported defect.
"""

import pytest

from pages.discover_page import DiscoverPage
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.slugs")

SLUGS = ["/popular", "/trend", "/new", "/top"]


@pytest.mark.slugs
@pytest.mark.known_issue
@pytest.mark.xfail(
    reason="D-01: hard navigation / refresh to any category slug renders an "
    "empty page (no genre list, no results) - the SPA's initial "
    "data-load effect does not run on a deep link; clicking the same "
    "tab from the home page works. Expected failure = defect reproduced.",
    strict=True,
)
@pytest.mark.parametrize("slug", SLUGS, ids=SLUGS)
def test_slug_direct_access_renders_results(browser_page, slug):
    discover = DiscoverPage(browser_page)

    with allure.step(f"Hard-navigate directly to {slug} (deep link / refresh)"):
        discover.go_to_slug(slug)
        # Give the (broken) app a chance; correct behaviour would render fast.
        browser_page.wait_for_timeout(3000)

    with allure.step("Assert the result grid rendered"):
        count = discover.result_count()
        log.info("Direct slug %s rendered %s cards", slug, count)
        assert count > 0, (
            f"Direct navigation to {slug} rendered no results "
            "(known defect: deep-link / refresh does not load data)"
        )
