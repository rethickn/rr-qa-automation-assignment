import re

from playwright.sync_api import expect

from utils.logger import get_logger

log = get_logger("pages.discover")


class DiscoverPage:

    BASE_URL = "https://tmdb-discover.surge.sh/"

    # Search
    SEARCH_BOX = "input[name='search']"

    # Filter dropdown containers (react-select)
    TYPE_DROPDOWN = "div.css-2b097c-container >> nth=0"
    GENRE_DROPDOWN = "div.css-2b097c-container >> nth=1"
    FROM_YEAR = "div.css-2b097c-container >> nth=2"
    TO_YEAR = "div.css-2b097c-container >> nth=3"

    # Rendered values
    SINGLE_VALUE = ".css-1uccc91-singleValue"   # Type, From year, To year
    MULTI_VALUE = "[class*='multiValue']"        # Genre (multi-select)
    OPTION = "div[class*='-option']"             # Open dropdown option

    # Rating
    RATING_STARS = "li.rc-rate-star"

    # Results grid
    RESULT_GRID = "div.grid"
    RESULT_CARDS = "div.grid > *"
    RESULT_POSTERS = "img[src*='image.tmdb.org']"

    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(self.BASE_URL)

    def go_to_slug(self, slug: str):
        """Navigate directly to a category slug (e.g. '/top').

        Used by the negative slug tests to mimic a hard refresh / deep link.
        """
        log.info("Direct navigation to slug: %s", slug)
        self.page.goto(self.BASE_URL.rstrip("/") + slug)

    def get_url(self) -> str:
        return self.page.url

    # -----------------------------
    # Results
    # -----------------------------

    def wait_for_results(self):
        log.info("Waiting for result grid to populate")
        self.page.locator(self.RESULT_POSTERS).first.wait_for(
            state="visible", timeout=10000
        )

    def result_count(self) -> int:
        return self.page.locator(self.RESULT_POSTERS).count()

    def poster_sources(self) -> list[str]:
        return [
            self.page.locator(self.RESULT_POSTERS).nth(i).get_attribute("src")
            for i in range(self.result_count())
        ]

    def result_texts(self) -> list[str]:
        cards = self.page.locator(self.RESULT_CARDS)
        return [cards.nth(i).inner_text() for i in range(cards.count())]

    # Result-card accessors (0-based index) ------------------------------

    def result_card(self, index: int):
        """Locator for the Nth result card (0-based)."""
        return self.page.locator(self.RESULT_CARDS).nth(index)

    def result_title(self, index: int) -> str:
        """Bold title line of the Nth card."""
        return self.result_card(index).locator("p").nth(0).inner_text()

    def result_meta(self, index: int) -> str:
        """Genre/year line of the Nth card (e.g. 'Animation, 2026')."""
        return self.result_card(index).locator("p").nth(1).inner_text()

    def click_result(self, index: int):
        """Choose (click) the Nth result card, simulating a user pick.

        NOTE: the current SUT renders non-navigable cards (clicking opens no
        detail view), so this is used to focus/select the card within the
        end-to-end flow; callers assert on the rendered card afterwards.
        """
        log.info("Choosing result card #%s", index + 1)
        self.result_card(index).click()

    # Year extraction (used to validate the year filter) -----------------

    def result_years(self) -> list[int]:
        """Release year shown on each visible result card (0 if unparsed)."""
        cards = self.page.locator(self.RESULT_CARDS)
        years = []
        for i in range(cards.count()):
            match = re.search(r"(?:19|20)\d{2}", cards.nth(i).inner_text())
            years.append(int(match.group(0)) if match else 0)
        return years

    def out_of_range_years(self, from_year: int, to_year: int) -> list[int]:
        """Years currently shown that fall outside [from_year, to_year]."""
        return [
            y for y in self.result_years()
            if y and (y < from_year or y > to_year)
        ]

    # Internal helper -------------------------------------------------

    def _pick_option(self, text):
        """Click an option in the currently open react-select dropdown."""
        self.page.locator(self.OPTION).filter(has_text=text).first.click()

    # -----------------------------
    # Search
    # -----------------------------

    def search_movie(self, movie_name):
        self.page.fill(self.SEARCH_BOX, movie_name)

    def verify_search(self, movie_name):
        expect(
            self.page.locator(f"text={movie_name}").first
        ).to_be_visible()

    # -----------------------------
    # Type Filter
    # -----------------------------

    def select_type(self, movie_type):
        self.page.click(self.TYPE_DROPDOWN)
        self.page.wait_for_timeout(5000)
        self._pick_option(movie_type)

    def verify_type(self, movie_type):
        expect(
            self.page.locator(self.SINGLE_VALUE).nth(0)
        ).to_contain_text(movie_type)

    # -----------------------------
    # Genre Filter (multi-select)
    # -----------------------------

    def select_genre(self, genre):
        self.page.click(self.GENRE_DROPDOWN)
        self._pick_option(genre)

    def verify_genre(self, genre):
        expect(
            self.page.locator(self.MULTI_VALUE).first
        ).to_contain_text(genre)

    # -----------------------------
    # Year Filter
    # -----------------------------

    def select_from_year(self, year):
        self.page.click(self.FROM_YEAR)
        self._pick_option(year)

    def select_to_year(self, year):
        self.page.click(self.TO_YEAR)
        self._pick_option(year)

    def verify_from_year(self, year):
        # single values: 0=Type, 1=From year, 2=To year
        expect(
            self.page.locator(self.SINGLE_VALUE).nth(1)
        ).to_have_text(year)

    def verify_to_year(self, year):
        expect(
            self.page.locator(self.SINGLE_VALUE).nth(2)
        ).to_have_text(year)

    # -----------------------------
    # Rating Filter
    # -----------------------------

    def select_rating(self, rating):
        # Click the right half of the target star to select a FULL star.
        second = self.page.locator(self.RATING_STARS).nth(
            rating - 1
        ).locator(".rc-rate-star-second")
        box = second.bounding_box()
        second.click(
            position={"x": box["width"] - 2, "y": box["height"] / 2},
            force=True,
        )

    def verify_rating(self, rating):
        expect(
            self.page.locator(self.RATING_STARS).nth(rating - 1)
        ).to_have_class(re.compile(r"rc-rate-star-full"))
