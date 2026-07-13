"""Safe re-export of Allure so tests can use ``allure.step`` / ``allure.tag``
without hard-failing when ``allure-pytest`` is not installed (e.g. a quick
local run with only pytest + pytest-html)."""

try:
    import allure
except ImportError:  # pragma: no cover - only used when allure is absent

    class _NoopCtx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class _AllureFallback:
        def step(self, title=""):
            return _NoopCtx()

        def title(self, text):
            pass

        def description(self, text):
            pass

        def description_html(self, text):
            pass

        def severity(self, level):
            pass

        def tag(self, *tags):
            pass

        def link(self, url, name=None, link_type=None):
            pass

    allure = _AllureFallback()
