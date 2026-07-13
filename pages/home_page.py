from utils.constants import BASE_URL


class HomePage:

    def __init__(self, page):
        self.page = page

        # Category Locators
        self.popular = page.locator("a[href='/popular']")
        self.trending = page.locator("a[href='/trend']")
        self.newest = page.locator("a[href='/new']")
        self.top_rated = page.locator("a[href='/top']")

    def open(self):
        self.page.goto(BASE_URL)

    def get_title(self):
        return self.page.title()

    def click_popular(self):
        self.popular.click()

    def click_trending(self):
        self.trending.click()

    def click_newest(self):
        self.newest.click()

    def click_top_rated(self):
        self.top_rated.click()