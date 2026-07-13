from pathlib import Path

from utils.logger import get_logger

log = get_logger("utils.screenshot")

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


def take_screenshot(page, name: str, full_page: bool = True) -> str | None:
    """Capture a PNG screenshot and persist it under ``screenshots/``.

    Returns the absolute path so the caller (or the pytest failure hook) can
    attach it to the Allure report and reference it from the defect log.

    Playwright raises if the page is already closed, so we guard the capture
    and return ``None`` instead of failing the teardown.
    """
    safe_name = name.replace("/", "_").replace(" ", "_")
    path = SCREENSHOT_DIR / f"{safe_name}.png"
    try:
        page.screenshot(path=str(path), full_page=full_page)
        log.info("Screenshot saved: %s", path)
        return str(path)
    except Exception as exc:  # pragma: no cover - defensive teardown guard
        log.warning("Screenshot skipped (%s): %s", name, exc)
        return None


def attach_to_allure(path: str, name: str = "Screenshot") -> None:
    """Best-effort attach a file to the current Allure test result."""
    try:
        from allure_commons.types import AttachmentType

        import allure

        allure.attach.file(path, name=name, attachment_type=AttachmentType.PNG)
    except Exception:
        # allure-pytest not installed / not in an allure run -> ignore silently
        pass
