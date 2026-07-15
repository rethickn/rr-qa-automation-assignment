# TMDB Discover — Test Case Specification

**Application under test:** https://tmdb-discover.surge.sh/ (demo movie/TV listing SPA)
**Backend:** public TMDB API (`api.themoviedb.org/3`)
**Suite:** `pytest` + Playwright (sync) — see `README.md` for setup & execution.

Legend — **Type:** `Positive` (happy path) · `Negative` (known-issue / boundary) · `API` (backend contract)
**Priority:** `P1` (core) · `P2` (important) · `P3` (edge)
**Design technique:** EP = Equivalence Partitioning · BVA = Boundary Value Analysis · ST = State Transition · DT = Decision Table · ET = Exploratory.

---

## Test Cases (all modules)

| Module | Test case no | Title | Steps to reproduce | Expected result | Status |
|--------|--------------|-------|--------------------|-----------------|--------|
| 1 — Category navigation | CAT-01 | Popular tab routes to `/popular` and loads a grid | 1. Open `https://tmdb-discover.surge.sh/`. 2. Click the **Popular** category link. 3. Wait for the result grid to populate. | URL ends with `/popular`; ≥ 1 result card (poster) is visible. | Not Run |
| 1 — Category navigation | CAT-02 | Trending tab routes to `/trend` | 1. Open the base URL. 2. Click the **Trending** category link. 3. Wait for the result grid to populate. | URL ends with `/trend`; ≥ 1 result card is visible. | Not Run |
| 1 — Category navigation | CAT-03 | Newest tab routes to `/new` | 1. Open the base URL. 2. Click the **Newest** category link. 3. Wait for the result grid to populate. | URL ends with `/new`; ≥ 1 result card is visible. | Not Run |
| 1 — Category navigation | CAT-04 | Top Rated tab routes to `/top` | 1. Open the base URL. 2. Click the **Top Rated** category link. 3. Wait for the result grid to populate. | URL ends with `/top`; ≥ 1 result card is visible. | Not Run |
| 2 — Discover filters | DIS-01 | Search box filters by title | 1. Open the Discover page. 2. Type `Toy Story` in `input[name='search']`. 3. Assert a visible title contains "Toy Story" and the backend `search/movie` returns ≥ 1 hit containing "Toy Story". | UI match **and** API match for the search query. | Not Run |
| 2 — Discover filters | DIS-02 | Type filter reflects "TV Show" | 1. Open the Discover page. 2. Set the Type filter to "TV Show". 3. Observe the applied filter state. | The Type filter reflects "TV Show" and drives the correct request. | Not Run |
| 2 — Discover filters | DIS-03 | Genre filter shows "Action" chip | 1. Open the Discover page. 2. Select the "Action" genre. 3. Observe the active filter chips. | An "Action" chip is shown as an active filter. | Not Run |
| 2 — Discover filters | DIS-04 | Year range 2000–2020 is applied | 1. Open the Discover page. 2. Set From year = 2000 and To year = 2020. 3. Apply the filter. | Results are restricted to the 2000–2020 release window. | Not Run |
| 2 — Discover filters | DIS-05 | Rating filter highlights 4th star | 1. Open the Discover page. 2. Set the rating filter to 4 stars. 3. Observe the star widget. | The 4th star is highlighted as the selected rating. | Not Run |
| 2 — Discover filters | DIS-06 | Year filter reaches backend with correct bounds | 1. Open the Discover page. 2. Set From year = 2000, To year = 2020. 3. Capture the `discover/movie` network request. | Request carries `release_date.gte`/`release_date.lte` bounds; UI card count equals the API result length. | Not Run |
| 2 — Discover filters | DIS-07 | Genre filter reaches backend with `with_genres` | 1. Open the Discover page. 2. Select a genre. 3. Capture the `discover/movie` network request. | The request includes `with_genres`; returned results match the selected genre. | Not Run |
| 3 — Pagination | PAG-01 | "Next" loads page 2 with different items | 1. Open Popular. 2. Record page-1 poster paths. 3. Click **Next**. 4. Assert `current_page() == 2` and posters differ from page 1 and match `api.discover(popular, page=2)`. | State transition works and UI == API for page 2. | Not Run |
| 3 — Pagination | PAG-02 | "Previous" returns to page 1 | 1. Open Popular and click **Next** to page 2. 2. Click **Previous**. 3. Assert `current_page() == 1`. | Returns to page 1 with the original items. | Not Run |
| 3 — Pagination | PAG-03 | Jump to a specific (numbered) page | 1. Open Popular. 2. Enter a specific page number in the pagination control. 3. Submit and wait for results. | The entered page loads with items matching the API for that page. | Not Run |
| 3 — Pagination | PAG-04 | Last page loads real results | 1. Open Popular. 2. Read `total_pages` from the backend. 3. Click the last page button and wait for results. | UI lands on the final page and renders ≥ 1 card. (Known issue: last pages may render empty/wrong — tagged `@known_issue`, logs defect.) | Known Issue |
| 4 — Slug / deep-link | SLG-01 | Direct slug access renders results | 1. `page.goto(base + slug)` for a category slug (simulates refresh/bookmark/deep link). 2. Wait briefly. 3. Assert `result_count > 0`. | The grid renders results for the deep-linked category. (Known issue: hard navigation to any slug renders an empty page — defect D-01.) | Known Issue |
| 4 — Slug / deep-link | SLG-02 | Direct slug access across all categories (parametrised) | 1. For each slug `/popular`, `/trend`, `/new`, `/top`, `page.goto(base + slug)`. 2. Wait briefly. 3. Assert `result_count > 0`. | Each slug renders a populated grid. (Known issue: all parametrisations render empty — defect D-01.) | Known Issue |
| 5 — Backend API | API-01 | `discover/movie` returns well-formed payload | 1. Call `TMDBApiClient.discover("popular", page=1)`. 2. Inspect the response shape. | HTTP 200; `page == 1`; `total_results > 0`; each result has `id`, `title`, `poster_path`, `vote_average`. | Not Run |
| 5 — Backend API | API-02 | `with_genres` filter is honoured by backend | 1. Call `discover/movie` with a `with_genres` value. 2. Inspect returned results. | All returned results belong to the requested genre. | Not Run |
| 5 — Backend API | API-03 | Live page emits a successful TMDB call | 1. Drive the UI. 2. Use `NetworkMonitor` to record responses from `api.themoviedb.org`. | A `discover/movie` call with `sort_by=popularity.desc&page=1` and HTTP 2xx is observed. | Not Run |

---
