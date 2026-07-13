import time

from playwright.sync_api import expect

from utils.logger import get_logger

log = get_logger("pages.pagination")


class PaginationPage:
    """
    Page Object for TMDB Pagination.
    Handles all pagination-related actions and validations.
    """

    CONTAINER = "#react-paginate"

    PAGE_LINKS = "#react-paginate li:not(.previous):not(.next):not(.break) a"

    PREVIOUS = "#react-paginate li.previous a"
    NEXT = "#react-paginate li.next a"

    PREVIOUS_LI = "#react-paginate li.previous"
    NEXT_LI = "#react-paginate li.next"

    ACTIVE = "#react-paginate li.selected"

    def __init__(self, page):
        self.page = page
        self.container = page.locator(self.CONTAINER)

    # ---------------------------------------------------------
    # Wait Methods
    # ---------------------------------------------------------

    def wait_visible(self):
        log.info("Waiting for pagination control")
        self.container.wait_for(state="visible", timeout=10000)

    def expect_visible(self):
        expect(self.container).to_be_visible()

    def is_visible(self):
        return self.container.is_visible()

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def click_next(self):
        log.info("Clicking Next page")
        self.page.locator(self.NEXT).click()

    def click_previous(self):
        log.info("Clicking Previous page")
        self.page.locator(self.PREVIOUS).click()

    def go_to_page(self, page_number: int):
        log.info("Navigating to page %s", page_number)

        self.page.locator(self.PAGE_LINKS).filter(
            has_text=str(page_number)
        ).first.click()

    def click_last(self):
        """
        Click the last available page button.
        Returns the page number clicked.
        """

        links = self.page.locator(self.PAGE_LINKS)

        count = links.count()

        last_page = links.nth(count - 1).inner_text()

        log.info("Last page button : %s", last_page)

        links.nth(count - 1).click()

        return int(last_page)

    # ---------------------------------------------------------
    # Page Validation
    # ---------------------------------------------------------

    def current_page(self):

        active = self.page.locator(self.ACTIVE).inner_text()

        return int(active)

    def wait_until_page(
        self,
        page_number: int,
        timeout: int = 10000
    ):
        """
        Wait until pagination reaches the expected page.
        """

        deadline = time.time() + timeout / 1000

        while time.time() < deadline:

            try:

                if self.current_page() == page_number:
                    return

            except Exception:
                pass

            # Better than time.sleep() in Playwright
            self.page.wait_for_timeout(200)

        raise TimeoutError(
            f"Pagination never reached page {page_number}. "
            f"Current page: {self.current_page()}"
        )

    # ---------------------------------------------------------
    # Button State
    # ---------------------------------------------------------

    def next_enabled(self):

        classes = self.page.locator(
            self.NEXT_LI
        ).get_attribute("class")

        return "disabled" not in (classes or "")

    def previous_enabled(self):

        classes = self.page.locator(
            self.PREVIOUS_LI
        ).get_attribute("class")

        return "disabled" not in (classes or "")

    # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------

    def highest_page_number(self):
        """
        Returns the largest numbered page button currently visible.
        """

        buttons = self.page.locator(self.PAGE_LINKS)

        highest = 1

        for i in range(buttons.count()):

            try:
                value = int(buttons.nth(i).inner_text())
                highest = max(highest, value)

            except ValueError:
                continue

        return highest