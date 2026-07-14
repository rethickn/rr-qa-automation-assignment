# TMDB Discover — Test Automation: Answers & Documentation

**TMDB Discover** end‑to‑end test automation framework. It covers strategy, the cases that were generated and why, the framework/libraries, how to run everything, the design techniques and coding patterns used, and the defects that were found.

---

## 1. Testing Strategy

**Testing Strategy**

Built a black-box E2E test suite (Playwright + Chromium) for a React SPA backed by the TMDB API, combining three layers:

- **UI E2E testing** – simulates real user flows (navigation, search, filters, pagination) and validates rendered results.
- **API contract testing** – validates the underlying TMDB API responses independently, ensuring data correctness beyond the UI.
- **Network monitoring** – verifies actual HTTP traffic to confirm UI–backend integration.

Testing effort was prioritized around the core user journeys (category navigation, search, filters, pagination), with one known defect explicitly documented via an expected-failure test rather than hidden.

Every run generates HTML, JUnit, and Allure reports with automatic failure screenshots — making results CI-ready and easy to review.

---

## 2. Test Cases Generated (and why)

**Test Coverage Summary**

23 automated tests across 6 modules — 18 passing, 5 flagged as expected failures (`xfail`) to document known SUT defects rather than hide them.

**Highlights:**
- **API contract tests** – validate TMDB backend responses (catalogue structure, genre filtering, live network traffic) independent of the UI.
- **Category navigation** – parametrized tests across Popular, Trending, Newest, Top Rated.
- **Search & filters** – search, type/genre/year/rating filters, with API cross-checks for backend accuracy.
- **Pagination** – next/previous/multi-page navigation and boundary checks (e.g., previous disabled on page 1).
- **Full E2E user journey** – filter → verify → select → confirm persistence, validated at both UI and API level.
- **Known defects documented, not hidden:**
  - Direct deep-link navigation to category slugs renders empty pages (4 `xfail` cases).
  - Year filter occasionally leaks out-of-range movies into results (1 `xfail`, intermittent).

**Testing techniques used:** positive/happy-path testing, boundary value analysis, and negative testing via expected-failure (`xfail`) cases — ensuring known bugs remain visible in reports instead of being silently skipped.

---

## 3. Test Automation Framework (libraries & structure)

**Tech stack**

- **Python 3.14** — core language
- **Playwright (≥1.47)** — browser automation (sync API) + `APIRequestContext` for HTTP calls, using the same engine for both UI and API checks for consistency
- **pytest (≥8.3)** — test runner, fixtures, markers, hooks
- **pytest-html (≥4.1)** — self-contained HTML reports
- **allure-pytest (≥2.13)** — rich, step-based reporting with attachments

**Project structure (Page Object Model)**
```
TMDB-Automation/
├── pages/            # Page Objects — locators + actions
│   ├── home_page.py
│   ├── discover_page.py
│   └── pagination_page.py
├── tests/            # Test cases (one file per feature area)
│   ├── test_api.py
│   ├── test_categories.py
│   ├── test_discover.py
│   ├── test_pagination.py
│   └── test_slugs.py
├── utils/            # Reusable helpers
│   ├── api_helper.py   # TMDBApiClient + NetworkMonitor
│   ├── logger.py       # Structured logging
│   ├── report.py       # Safe Allure re‑export (noop fallback)
│   ├── screenshot.py   # Failure screenshots + Allure attach
│   └── constants.py    # BASE_URL, API key, genre/category maps
├── conftest.py       # Shared fixtures + failure‑screenshot hook
├── pytest.ini        # Runner config, markers, reporting, logging
├── requirements.txt  # Pinned dependencies
└── README.md
```

**Dependency & Environment Management**

All runtime dependencies are pinned in `requirements.txt` (`pip install -r requirements.txt`), with Playwright browsers installed once via `playwright install`. A central `pytest.ini` config manages markers and reporting, ensuring a reproducible environment.

**Reporting & Execution**

`pytest.ini` wires up HTML, Allure, JUnit, and console/file logging in one place — a single `pytest` run produces all artefacts. Screenshots, reports, and logs are saved into dedicated, git-ignored folders (`screenshots/`, `reports/`, `allure-results/`, `logs/`).

---

## 4. How to Run the Tests
# 1. Create/activate a virtual environment (recommended)
python3 -m venv .venv && source .venv/bin/activate
# 2. Install dependencies
pip install -r requirements.txt
# 3. Install the browser engine (one-time)
playwright install
# 4. Run the full suite (headless, Chromium)
pytest -v
# 4b. Run headed (visible browser)
pytest -v --headed
# Run a single module / feature
pytest tests/test_discover.py -v
pytest tests/test_api.py -v
pytest tests/test_pagination.py -v
# Run by marker (e.g. only smoke / api / categories)
pytest -m smoke -v
pytest -m api -v
# Generate reports
pytest --html=reports/report.html --self-contained-html    # HTML
pytest --alluredir=allure-results                          # Allure raw
allure serve allure-results                                # Serve Allure

**Prerequisites:** internet access (the SUT and TMDB API are public endpoints).

---

## 5. Test Design Techniques Used

**Testing Techniques Applied**

- **Equivalence Partitioning / Boundary Value Analysis** — year range (2000–2020), first-page boundary for the disabled "previous" button, direct page jump (page 3).
- **State Transition Testing** — pagination (next → prev → jump) and category routing (home → tab → slug).
- **Positive vs Negative Testing** — happy-path flows assert success; slug tests assert a known defect and are marked `xfail`.
- **Cross-checking / Triangulation** — `test_search_movie` and `test_filter_year_backend_honors_range` compare UI output against backend data, catching mismatches the DOM alone would miss.
- **Data-driven Testing** — `pytest.mark.parametrize` used for categories (4 tabs) and slugs (4 routes), reducing duplication and improving coverage per line of code.
- **Contract Testing** — validates API payload schema/fields independent of the UI.
- **Observational/Integration Testing** — live network monitoring confirms real SUT traffic.
- **Smoke Tagging** — the critical happy-path (`test_search_movie`) is tagged `smoke` for fast, isolated feedback.
---

## 6. Coding Patterns Used

- **Page Object Model (POM)** — `pages/` classes encapsulate locators and
  actions; tests only express *intent* (`discover.search_movie(...)`), never raw
  selectors. This is the dominant maintainability pattern.
- **Centralised Locators & Constants** — selectors live at the top of each Page
  Object; URLs, API key, and genre/category maps live in `utils/constants.py`,
  so changes to the SUT require edits in one place.
- **Fixture reuse (`conftest.py`)** — `browser_page`, `api_request`,
  `network_monitor`, `logger` are shared fixtures, keeping tests DRY.
- **Hook for automatic evidence capture** — `pytest_runtest_makereport` takes a
  screenshot on failure/`xfail` and attaches it to Allure, with zero per‑test
  boilerplate.
- **Safe library re‑export** — `utils/report.py` wraps Allure in a no‑op
  fallback so tests run even if `allure-pytest` isn't installed.
- **Step‑based reporting** — `with allure.step(...)` blocks make the Allure
  report read like an executable spec.
- **Single Responsibility** — each Page Object method does one thing
  (select vs verify); a small `_pick_option` helper removes duplication across
  the react‑select dropdowns.
- **Explicit waiting over sleeps** — Playwright `expect`/`wait_for` auto‑wait on
  state (`visible`) instead of fixed `time.sleep`, reducing flakiness.
- **Logging** — every meaningful action is logged via a shared logger for
  traceability.

---

## 7. Defects Found

**Known Defects**

**D-01 — Deep-link/slug navigation renders an empty page** *(reproduced, documented)*
- **Symptom:** Directly navigating to or refreshing a category slug (`/popular`, `/trend`, `/new`, `/top`) loads a blank page — no genre list, no results.
- **Root cause:** The SPA's data-load effect only triggers on client-side tab clicks, not on hard navigation/deep links — the route mounts but never fetches data.
- **Evidence:** 4 parametrised `test_slug_direct_access_renders_results` cases assert results exist but find 0 cards — reported as strict `xfail`, with a screenshot per slug.
- **Severity:** Medium-High — breaks refresh, bookmarks, and shared links.
- **Recommended fix:** Trigger the initial fetch in a `useEffect` keyed on the route param so deep links/refreshes hydrate correctly.

**D-02 — Year filter UI refetch can be flaky** *(mitigated in tests)*
- **Symptom:** Applying a year range occasionally doesn't narrow visible results immediately.
- **Handling:** `test_filter_year_backend_honors_range` validates narrowing at the reliable API layer instead of the flaky UI refetch; UI reflection is checked separately in `test_filter_year`.
- **Recommended fix:** Ensure the in-app refetch is awaited/retried on filter change, using the same query params as the API client.

**D-03 — Year filter leaks out-of-range movies into the grid** *(reproduced, documented)*
- **Symptom:** With a 2001–2025 filter applied, the grid still shows titles outside that range (notably 2026, and often 1978/1979), even though the filter control itself displays correctly.
- **Root cause:** The in-app refetch doesn't reliably honour year bounds (a more severe form of D-02) — when slow/skipped, stale unfiltered results remain. Behaviour is intermittent: a manual probe reproduced the leak 3/3 times, while the full UI flow occasionally lets the refetch succeed.
- **Evidence:** `test_year_filter_excludes_out_of_range_movies` asserts no visible card falls outside 2001–2025. Marked `xfail(strict=False)` — reports **XFAIL** when the bug appears, **XPASS** (still green) when the refetch succeeds. Screenshot captured on XFAIL.
- **Severity:** High — defeats the core purpose of the year filter; directly matches the reported issue (2026 titles under a 2001–2025 filter).
- **Recommended fix:** Derive `release_date.gte/lte` strictly from active filter state on every refetch, discard stale results, and add a client-side safety check to drop out-of-range results.

> **Current run status:** `18 passed, 4 xfailed, 1 xpassed` (23 tests). The `xpassed` is D-03 on a run where the refetch succeeded; on runs where out-of-range years leak through, it reports XFAIL instead. The 4 strict `xfail` cases are D-01. The suite is green either way.

---

## 8. Quality, Maintainability & Understandability Notes

**Strengths**

- Clean POM separation → tests read like specifications; centralised locators/constants minimise blast radius when the SUT changes.
- Multiple, complementary reporting formats (HTML, Allure, JUnit, logs) — consumable by both humans and CI.
- Automatic screenshots + structured logging enable fast failure triage.
- Strict `xfail` keeps known defects visible instead of hiding them.
- Safe Allure fallback keeps the suite runnable in minimal environments.

**Suggestions for Further Hardening**

- **Cross-browser:** Currently Chromium-only (via `pytest-playwright`). Need to add Firefox/WebKit via the `browser` fixture for broader coverage.
- **Secret hygiene:** `TMDB_API_KEY` is hardcoded in `utils/constants.py`. It's a read-only demo key, but for production-grade code, move it to an env var/secrets manager and confirm it's not a leaked key.
- **Locators:** Some selectors rely on volatile `css-2b097c-container` / positional `nth=` indices (react-select generated classes). These may break on UI library upgrades — prefer stable `data-testid` attributes where possible.
- **CI integration:** Wire `reports/junit.xml` into a CI pipeline and run the `smoke` marker on every push for fast feedback.
- **Parallelism:** For a larger suite, consider `pytest-xdist` (note: shared `reports/` paths would need per-worker isolation).
