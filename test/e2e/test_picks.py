from pathlib import Path

from playwright.sync_api import Page, expect
from pytest import fixture


@fixture(autouse=True)
def open_pick_pen(page: Page):
    page.goto("/community/picks/")


def test_pick_pen_exposes_discovery_controls_and_count(page: Page):
    expect(page.get_by_label("Search picks")).to_be_visible()
    expect(page.get_by_label("Show")).to_be_visible()
    expect(page.get_by_label("License")).to_be_visible()
    expect(page.get_by_label("Sort picks")).to_be_visible()
    expect(page.get_by_role("button", name="Reset filters")).to_be_visible()
    expect(page.locator("#pick-results-count")).to_have_text("177 picks")


def test_search_matches_title_and_description(page: Page):
    search = page.get_by_label("Search picks")

    search.fill("actual budget")
    expect(page.locator(".pick:visible")).to_have_count(1)
    expect(page.locator(".pick:visible h2, .pick:visible h4")).to_contain_text(
        "Actual Budget"
    )
    expect(page.locator("#pick-results-count")).to_have_text("1 pick")

    search.fill("privacy-focused")
    expect(page.locator(".pick:visible")).to_have_count(1)
    expect(page.locator(".pick:visible h2, .pick:visible h4")).to_contain_text(
        "Actual Budget"
    )


def test_search_filters_and_sort_combine(page: Page):
    page.get_by_label("Search picks").fill("ping")
    page.get_by_label("Show").select_option(label="LINUX Unplugged")
    page.get_by_label("License").select_option(label="MIT")

    visible_cards = page.locator(".pick:visible")
    expect(visible_cards).to_have_count(1)
    expect(visible_cards.first.locator("h2, h4")).to_contain_text("nping")

    page.get_by_label("Sort picks").select_option("title-desc")
    expect(visible_cards).to_have_count(1)


def test_no_results_and_reset(page: Page):
    page.get_by_label("Search picks").fill("no pick can match this phrase")

    expect(page.locator(".pick:visible")).to_have_count(0)
    expect(page.locator("#pick-empty-state")).to_be_visible()
    expect(page.locator("#pick-results-count")).to_have_text("0 picks")

    page.get_by_role("button", name="Reset filters").click()
    expect(page.get_by_label("Search picks")).to_have_value("")
    expect(page.locator("#pick-empty-state")).to_be_hidden()
    expect(page.locator(".pick:visible")).to_have_count(177)
    expect(page.locator("#pick-results-count")).to_have_text("177 picks")


def test_recent_sort_uses_real_episode_dates(page: Page):
    page.get_by_label("Sort picks").select_option("date-desc")

    first_card = page.locator(".pick:visible").first
    expect(first_card).to_have_attribute("data-featured-date", "2026-10-11T16:17:00-07:00")
    expect(first_card.locator("h2, h4")).to_contain_text("RAWmakase")


def test_project_links_are_isolated_from_the_opener(page: Page):
    links = page.locator(".pick h2 a[target='_blank'], .pick h4 a[target='_blank']")
    expect(links).to_have_count(177)

    for index in range(links.count()):
        expect(links.nth(index)).to_have_attribute("rel", "noopener noreferrer")


def test_controls_fit_a_mobile_viewport(page: Page, screenshot_dir: Path):
    page.set_viewport_size({"width": 390, "height": 844})
    page.reload()

    controls = page.locator("#pick-discovery-controls")
    expect(controls).to_be_visible()
    assert controls.bounding_box()["width"] <= 390

    page.screenshot(path=f"{screenshot_dir}/pick-pen-mobile.png", full_page=True)
