# TMDB Discover — Functional Test Automation

Automated functional test suite for the demo listing platform
**https://tmdb-discover.surge.sh/** (a movie/TV discovery SPA backed by the
public TMDB API).

# 🎬 TMDB Automation Framework

A robust End-to-End Test Automation Framework developed using **Playwright**, **Pytest**, and the **Page Object Model (POM)** to automate and validate the TMDB Discover web application.

This framework validates UI functionality, backend API responses, pagination, category navigation, search, filters, logging, reporting, and screenshot capture while following industry-standard automation practices.

---

# 🚀 Tech Stack

- Python 3.14
- Playwright
- Pytest
- Page Object Model (POM)
- Pytest HTML Report
- Allure Reporting
- Logging
- API Testing
- Network Monitoring

---

# 📁 Project Structure

```
TMDB-Automation/
│
├── pages/
│   ├── home_page.py
│   ├── discover_page.py
│   └── pagination_page.py
│
├── tests/
│   ├── test_categories.py
│   ├── test_discover.py
│   ├── test_api.py
│   ├── test_pagination.py
│   └── test_slugs.py
│
├── utils/
│   ├── api_helper.py
│   ├── logger.py
│   ├── report.py
│   ├── screenshot.py
│   └── constants.py
│
├── screenshots/
├── reports/
├── logs/
│
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# ✨ Features Covered

## Home Page

- Launch TMDB Discover application
- Verify page loads successfully
- Verify page title

---

## Category Navigation

- Popular
- Trending
- Newest
- Top Rated

---

## Discover Filters

### Search

- Search movies by title
- Verify search results

### Type Filter

- Movie
- TV Show

### Genre Filter

- Action
- Adventure
- Animation
- Comedy
- Crime
- Drama
- Fantasy
- Horror
- Romance
- Science Fiction
- Thriller

### Year Filter

- From Year
- To Year

### Rating Filter

- Select rating
- Verify selected rating

---

## Pagination

- Navigate to next page
- Navigate to previous page
- Navigate directly to a page
- Verify pagination controls
- Validate current page

---

## API Testing

The framework validates backend APIs using Playwright's APIRequestContext.

Checks include:

- HTTP Response Validation
- JSON Schema Validation
- Required Fields Validation
- Genre Validation
- Response Content Validation

---

## Network Monitoring

The framework captures live browser network traffic and validates:

- TMDB API requests
- HTTP Status Codes
- Response payloads
- Catalog API calls

---

## Logging

Framework generates detailed execution logs.

Example:

```
Browser launched successfully
Waiting for Discover page
Searching movie: Toy Story
Pagination: Navigating to page 2
API Response received
Test Passed
```

Logs are stored under:

```
logs/
```

---

## Screenshots

Screenshots are automatically captured when a test fails or an expected failure (XFAIL) occurs.

Location:

```
screenshots/
```

---

## Reports

### Pytest HTML Report

Generated using:

```bash
pytest --html=reports/report.html --self-contained-html
```

Open report:

```bash
open reports/report.html
```

---

### Allure Report

Generate results:

```bash
pytest --alluredir=allure-results
```

Serve report:

```bash
allure serve allure-results
```

---

# ⚙️ Installation

Clone repository

```bash
git clone https://github.com/rethickn/rr-qa-automation-assignment.git
```

Navigate into project

```bash
cd rr-qa-automation-assignment
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install Playwright browsers

```bash
playwright install
```

Set the TMDB API key (required)

The API key is **not** stored in the code. Provide it via the
`TMDB_API_KEY` environment variable (a read-only demo key is sufficient):

```bash
# macOS / Linux
export TMDB_API_KEY=your_read_only_tmdb_api_key

# Windows (PowerShell)
$env:TMDB_API_KEY="your_read_only_tmdb_api_key"
```

A `.env.example` is included - copy it to `.env` and fill in the key
(`.env` is git-ignored). Without this variable the suite raises a clear
error at startup.

---

# ▶️ Running Tests

Run entire suite

```bash
pytest -v
```

Run with browser

```bash
pytest -v --headed
```

Run specific test

```bash
pytest tests/test_discover.py -v
```

Run API tests

```bash
pytest tests/test_api.py -v
```

Run Pagination tests

```bash
pytest tests/test_pagination.py -v
```

---

# 📊 Test Coverage

| Module | Status |
|----------|--------|
| Home Page | ✅ |
| Categories | ✅ |
| Search | ✅ |
| Type Filter | ✅ |
| Genre Filter | ✅ |
| Year Filter | ✅ |
| Rating Filter | ✅ |
| Pagination | ✅ |
| API Validation | ✅ |
| Network Monitoring | ✅ |
| Logging | ✅ |
| Screenshot Capture | ✅ |
| HTML Reporting | ✅ |
| Allure Reporting | ✅ |

---

# 🐞 Known Defects

The framework intentionally documents known application defects using `pytest.mark.xfail`.

Example:

- Direct navigation to category routes (`/top`, `/trend`, `/new`) loads an empty page instead of rendering movie results.

These tests are marked as expected failures (XFAIL) to document current application behavior while allowing the test suite to continue.

---

# 🏗️ Framework Design

The framework follows the Page Object Model (POM) design pattern.

- Reusable Page Objects
- Centralized Locators
- Modular Utilities
- API Helper
- Network Monitoring
- Logging
- Screenshot Utility
- Reporting
- Pytest Fixtures

---

# 📌 Highlights

- Industry-standard Playwright framework
- Clean Page Object Model implementation
- UI and API validation
- Live network monitoring
- Automatic screenshot capture
- HTML and Allure reporting
- Structured logging
- Easy to maintain and extend

---

# 👨‍💻 Author

**Rethick Nagarajan**

GitHub:

https://github.com/rethickn

---
