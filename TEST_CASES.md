# TMDB Discover — Test Case Specification

**Application under test:** https://tmdb-discover.surge.sh/ (demo movie/TV listing SPA)
**Backend:** public TMDB API (`api.themoviedb.org/3`)
**Suite:** `pytest` + Playwright (sync) — see `README.md` for setup & execution.

Legend — **Type:** `Positive` (happy path) · `Negative` (known-issue / boundary) · `API` (backend contract)
**Priority:** `P1` (core) · `P2` (important) · `P3` (edge)
**Design technique:** EP = Equivalence Partitioning · BVA = Boundary Value Analysis · ST = State Transition · DT = Decision Table · ET = Exploratory.

---

## Module 1 — Category navigation (home page)

| TC-ID | Title | Type | Pri | Technique |
|-------|-------|------|-----|-----------|
| CAT-01 | Popular tab routes to `/popular` and loads a grid | Positive | P1 | EP |
| CAT-02 | Trending tab routes to `/trend` | Positive | P1 | EP |
| CAT-03 | Newest tab routes to `/new` | Positive | P1 | EP |
| CAT-04 | Top Rated tab routes to `/top` | Positive | P1 | EP |

**CAT-01 (detailed)**
- *Preconditions:* browser at base URL, network reachable.
- *Steps:*
  1. Open `https://tmdb-discover.surge.sh/`.
  2. Click the **Popular** category link.
  3. Wait for the result grid to populate.
- *Expected:*
  - URL ends with `/popular`.
  - ≥ 1 result card (poster) is visible.
- *Assertions:* `page.url.endswith("/popular")`; `DiscoverPage.result_count() > 0`.

---

## Module 2 — Discover filters

| TC-ID | Title | Type | Pri | Technique |
|-------|-------|------|-----|-----------|
| DIS-01 | Search box filters by title | Positive | P1 | EP |
| DIS-02 | Type filter reflects "TV Show" | Positive | P2 | EP |
| DIS-03 | Genre filter shows "Action" chip | Positive | P1 | EP |
| DIS-04 | Year range 2000–2020 is applied | Positive | P1 | BVA |
| DIS-05 | Rating filter highlights 4th star | Positive | P2 | EP |
| DIS-06 | Year filter reaches backend with correct bounds | API | P1 | DT |
| DIS-07 | Genre filter reaches backend with `with_genres` | API | P2 | DT |

**DIS-01 (detailed)**
- *Steps:* open discover → type `Toy Story` in `input[name='search']` → assert a title containing "Toy Story" is visible → assert backend `search/movie` returns ≥ 1 hit whose title contains "Toy Story".
- *Expected:* UI match **and** API match.

**DIS-06 (detailed) — API cross-check**
- *Steps:* open discover → set From year = 2000, To year = 2020.
- *Expected:* captured network request to `discover/movie` carries
  `release_date.gte=2010-01-01` & `release_date.lte=2015-12-31`; UI card count equals `api.discover(popular, year_range=(2010,2015)).results` length.

---

## Module 3 — Pagination

| TC-ID | Title | Type | Pri | Technique |
|-------|-------|------|-----|-----------|
| PAG-01 | "Next" loads page 2 with different items | Positive | P1 | ST |
| PAG-02 | "Previous" returns to page 1 | Positive | P2 | ST |
| PAG-03 | Jump to a specific (numbered) page | **Negative** | P1 | EP |
| PAG-04 | Last page loads real results | **Negative** | P1 | BVA |

**PAG-01 (detailed)**
- *Steps:* open Popular → record page-1 poster paths → click **Next** → assert `current_page() == 2` → assert page-2 posters ≠ page-1 posters → assert page-2 posters == `api.discover(popular, page=2)` poster_paths.
- *Expected:* state transition works and UI == API.

**PAG-04 (detailed) — KNOWN ISSUE**
- *Steps:* open Popular → read `total_pages` from backend → click the last page button → wait for results.
- *Expected (intended):* UI lands on the final page and renders ≥ 1 card.
- *Actual (demo defect):* last few pages may render empty / wrong page. Test is tagged `@known_issue`; on failure it attaches a screenshot and is logged as a defect.

---

## Module 4 — Slug / deep-link access (NEGATIVE, known issue)

| TC-ID | Title | Type | Pri | Technique |
|-------|-------|------|-----|-----------|
| SLG-01 | Direct slug access renders results | **Negative** | P1 | DT |
| SLG-02 | (parametrised over `/popular`,`/trend`,`/new`,`/top`) | **Negative** | P1 | DT |

**SLG-01 (detailed) — KNOWN ISSUE**
- *Steps:* `page.goto(base + slug)` for each slug (simulates refresh / bookmark / deep link) → wait briefly → assert `result_count > 0`.
- *Expected (intended):* the grid renders results for the deep-linked category.
- *Actual (demo defect):* a hard navigation to **any** slug renders an empty
  page (no genre list fetched, no results grid) — the SPA's initial data-load
  effect does not run on a deep link. All parametrisations fail → each attaches
  a screenshot and is logged as defect D-01. (Contrast: clicking the same tab
  from the home page works — covered by CAT-01..04.)

---

## Module 5 — Backend API contract

| TC-ID | Title | Type | Pri | Technique |
|-------|-------|------|-----|-----------|
| API-01 | `discover/movie` returns well-formed payload | API | P1 | ET |
| API-02 | `with_genres` filter is honoured by backend | API | P2 | DT |
| API-03 | Live page emits a successful TMDB call | API | P1 | ET |

**API-01 (detailed)**
- *Steps:* `TMDBApiClient.discover("popular", page=1)`.
- *Expected:* HTTP 200; `page == 1`; `total_results > 0`; each result has `id`, `title`, `poster_path`, `vote_average`.

**API-03 (detailed) — asserting the browser's own traffic**
- *Steps:* drive the UI → `NetworkMonitor` records responses from `api.themoviedb.org`.
- *Expected:* a `discover/movie` call with `sort_by=popularity.desc&page=1` and HTTP 2xx is observed.

---

## Coverage matrix (requirement → tests)

| Requirement | Tests |
|-------------|-------|
| Categories (Popular/Trending/Newest/Top Rated) | CAT-01..04 |
| Title search | DIS-01 |
| Type (Movie / TV) | DIS-02 |
| Year of release | DIS-04, DIS-06 |
| Rating | DIS-05 |
| Genre | DIS-03, DIS-07, API-02 |
| Pagination | PAG-01..03 |
| Negative: slug access | SLG-01 (parametrised) |
| Negative: last pages | PAG-03 |
| Browser API calls + assertions | API-01..03, DIS-06, PAG-01/02 |
