import pytest
from playwright.sync_api import Page

from utils.api_helper import NetworkMonitor
from utils.logger import get_logger
from utils.screenshot import attach_to_allure, take_screenshot

log = get_logger("conftest")


@pytest.fixture
def browser_page(page: Page):
    """
    Shared browser page fixture for the entire test suite.
    """

    # Default timeout
    page.set_default_timeout(10000)

    # Browser size
    page.set_viewport_size({
        "width": 1366,
        "height": 900
    })

    log.info("Browser launched successfully")
    log.info("Viewport set to 1366 x 900")

    yield page

    log.info("Closing browser page")


@pytest.fixture
def api_request(playwright):
    """
    Playwright API Request Context
    """

    ctx = playwright.request.new_context()

    log.info("API Request Context Created")

    yield ctx

    ctx.dispose()

    log.info("API Request Context Closed")


@pytest.fixture
def network_monitor(browser_page: Page):
    """
    Monitor all network calls.
    """

    monitor = NetworkMonitor(browser_page)

    log.info("Network Monitor Attached")

    yield monitor

    monitor.detach()

    log.info("Network Monitor Detached")


@pytest.fixture
def logger():
    """
    Logger Fixture
    """
    return get_logger("test")


# Automatically capture screenshot on test failure
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield

    report = outcome.get_result()

    # Capture evidence only for tests that genuinely failed (real failures
    # and strict XFAILs). A plain XPASS is a passing result and must not
    # produce a misleading "Test Failed" log or a spurious screenshot.
    failed = report.when == "call" and report.failed

    if failed:

        page = item.funcargs.get("browser_page")

        if page:

            label = "XFAIL" if getattr(report, "wasxfail", False) else "FAIL"

            path = take_screenshot(
                page,
                f"{label}_{item.name}"
            )

            if path:

                attach_to_allure(
                    path,
                    f"{label} Screenshot - {item.name}"
                )

                log.error(
                    "Test Failed : %s | Screenshot : %s",
                    item.name,
                    path
                )