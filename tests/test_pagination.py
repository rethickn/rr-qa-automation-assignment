import pytest

from pages.home_page import HomePage
from pages.pagination_page import PaginationPage
from utils.logger import get_logger
from utils.report import allure

log = get_logger("tests.pagination")


@pytest.mark.pagination
def test_user_can_navigate_to_next_page(browser_page):

    home = HomePage(browser_page)
    pagination = PaginationPage(browser_page)

    with allure.step("Open TMDB"):
        home.open()

    with allure.step("Wait for pagination"):
        pagination.wait_visible()

    with allure.step("Navigate to next page"):
        pagination.click_next()
        pagination.wait_until_page(2)

    assert pagination.current_page() == 2, \
        "Expected to navigate to page 2"

    log.info("Successfully navigated to page 2")


@pytest.mark.pagination
def test_user_can_navigate_to_previous_page(browser_page):

    home = HomePage(browser_page)
    pagination = PaginationPage(browser_page)

    home.open()

    pagination.wait_visible()

    pagination.click_next()
    pagination.wait_until_page(2)

    pagination.click_previous()
    pagination.wait_until_page(1)

    assert pagination.current_page() == 1, \
        "Expected to return to page 1"

    log.info("Successfully returned to page 1")


@pytest.mark.pagination
def test_user_can_navigate_multiple_pages(browser_page):

    home = HomePage(browser_page)
    pagination = PaginationPage(browser_page)

    home.open()

    pagination.wait_visible()

    pagination.go_to_page(3)

    pagination.wait_until_page(3)

    assert pagination.current_page() == 3, \
        "Expected to navigate to page 3"

    log.info("Successfully navigated to page 3")


@pytest.mark.pagination
def test_previous_button_disabled_on_first_page(browser_page):

    home = HomePage(browser_page)
    pagination = PaginationPage(browser_page)

    home.open()

    pagination.wait_visible()

    assert not pagination.previous_enabled(), \
        "Previous button should be disabled on page 1"

    log.info("Previous button is disabled on first page")