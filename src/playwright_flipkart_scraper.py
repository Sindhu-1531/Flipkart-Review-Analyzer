# playwright_flipkart_scraper.py

from playwright.sync_api import sync_playwright
import csv
import time

def scrape_flipkart_reviews(url, max_pages=5):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        # Wait for reviews block to appear
        page.wait_for_selector("div.col.EPCmJX.Ma1fCG")

        all_reviews = []
        current_page = 1

        while current_page <= max_pages:
            print(f"\n📄 Scraping Page {current_page} ...")

            review_blocks = page.query_selector_all("div.col.EPCmJX.Ma1fCG")

            for block in review_blocks:
                try:
                    # Extract rating
                    rating_element = block.query_selector("div._3LWZlK._1BLPMq")
                    rating = rating_element.inner_text().strip() if rating_element else "No rating"

                    # Extract title (ex: Fabulous!)
                    title_element = block.query_selector("p._2-N8zT")
                    title = title_element.inner_text().strip() if title_element else "No title"

                    # Extract review text
                    review_text_element = block.query_selector("div.ZmyHeo > div")
                    review_text = review_text_element.inner_text().strip() if review_text_element else "No review text"

                    # Extract buyer name & date
                    buyer_element = block.query_selector("p._2NsDsF")
                    buyer_info = buyer_element.inner_text().strip() if buyer_element else "No buyer info"

                    all_reviews.append({
                        "Rating": rating,
                        "Title": title,
                        "Review": review_text,
                        "Buyer Info": buyer_info
                    })

                except Exception as e:
                    print(f"Error extracting a review: {e}")

            # Try to click the Next button
            try:
                next_button = page.query_selector("a._1LKTO3")  # Class for Next button
                if next_button and "disabled" not in next_button.get_attribute("class"):
                    next_button.click()
                    time.sleep(2)  # Wait for next page to load
                    page.wait_for_selector("div.col.EPCmJX.Ma1fCG")
                    current_page += 1
                else:
                    print("No more pages to scrape.")
                    break
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break

        browser.close()
        return all_reviews

def save_reviews_to_csv(reviews, filename="flipkart_reviews.csv"):
    keys = reviews[0].keys() if reviews else []
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(reviews)
    print(f"\n✅ Reviews saved to {filename}")

if __name__ == "__main__":
    url = input("Enter Flipkart product review page URL: ")
    try:
        reviews = scrape_flipkart_reviews(url, max_pages=5)  # You can change max_pages if needed
        print(f"\n✅ Total reviews extracted: {len(reviews)}")

        for i, review in enumerate(reviews, start=1):
            print(f"\n--- Review {i} ---")
            print(f"Rating: {review['Rating']}")
            print(f"Title: {review['Title']}")
            print(f"Review: {review['Review']}")
            print(f"Buyer Info: {review['Buyer Info']}")

        save_reviews_to_csv(reviews)

    except Exception as e:
        print(f"\n❌ Error while scraping: {e}")
