from playwright.sync_api import sync_playwright
import random

BASE_URL = "http://localhost:5001"

def test_full_user_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Add book
        page.goto(f"{BASE_URL}/add_book")

        unique_isbn = str(random.randint(10**12, 10**13 - 1))

        page.fill("input[name='title']", "Test Book")
        page.fill("input[name='author']", "Test Author")
        page.fill("input[name='isbn']", unique_isbn)
        page.fill("input[name='total_copies']", "5")

        page.click("button[type='submit']")

        # The add_book POST redirects to catalog - success 
        page.wait_for_timeout(500)
        assert "catalog" in page.url

        # 2. Confirm book appears in catalog
        assert page.locator("text=Test Book").first.is_visible()

        # 3. Borrow book for patron

        # Find the row containing our book
        row = page.locator("tr", has_text="Test Book").first

        # Inside that row: the patron_id field
        patron_input = row.locator("input[name='patron_id']")
        patron_input.fill("123456")

        # Click the Borrow button inside the same row
        borrow_button = row.locator("button", has_text="Borrow")
        borrow_button.click()

        page.wait_for_timeout(500)

        # 4. Validate borrow success
        assert (
            page.locator("text=Successfully").count() > 0 or
            page.locator("text=success").count() > 0 or
            page.locator("text=Due").count() > 0
        )

        browser.close()