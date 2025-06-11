from playwright.sync_api import sync_playwright
import time

def scrape_flipkart_reviews(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        try:
            # Scroll to bottom slowly to trigger reviews loading
            for i in range(5):
                page.mouse.wheel(0, 1000)
                time.sleep(1)  # Wait a bit for content to load

            # Now wait for review blocks to appear
            page.wait_for_selector('div._27M-vq', timeout=10000)

            reviews = page.locator('div._27M-vq')
            count = reviews.count()

            if count == 0:
                print("⚠️ No reviews found.")
                return

            print(f"\n✅ Found {count} reviews:\n")

            for i in range(min(5, count)):
                rating = reviews.nth(i).locator('div._3LWZlK').text_content()
                body = reviews.nth(i).locator('div.t-ZTKy div div').text_content()
                print(f"Review {i+1}")
                print("Rating:", rating.strip())
                print("Text:", body.strip())
                print("-" * 60)

        except Exception as e:
            print("❌ Error:", e)

        finally:
            browser.close()

if __name__ == "__main__":
    url = input("Enter Flipkart product review page URL: ")
    scrape_flipkart_reviews(url)

