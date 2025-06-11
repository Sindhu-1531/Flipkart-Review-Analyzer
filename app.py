# app.py

import streamlit as st
import pandas as pd
from textblob import TextBlob
from playwright.sync_api import sync_playwright
import time
import csv

# Reusable scraping function
def scrape_flipkart_reviews(url, num_pages=2):
    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        for _ in range(num_pages):
            page.wait_for_timeout(2000)

            review_elements = page.query_selector_all("div._27M-vq") or page.query_selector_all("div._16PBlm") or page.query_selector_all("div.col.EPCmJX.Ma1fCG")

            if not review_elements:
                st.error("Could not find review elements on this page.")
                break

            for elem in review_elements:
                try:
                    rating_elem = elem.query_selector("div._3LWZlK")
                    rating = rating_elem.inner_text().strip() if rating_elem else "No rating"

                    title_elem = elem.query_selector("p._2-N8zT")
                    title = title_elem.inner_text().strip() if title_elem else "No title"

                    review_elem = elem.query_selector("div.t-ZTKy div")
                    review = review_elem.inner_text().strip() if review_elem else "No review"

                    buyer_elem = elem.query_selector("p._2sc7ZR._2V5EHH")
                    buyer = buyer_elem.inner_text().strip() if buyer_elem else "No buyer info"

                    reviews.append({
                        "Rating": rating,
                        "Title": title,
                        "Review": review,
                        "Buyer Info": buyer
                    })

                except Exception as e:
                    print(f"Skipping a review block due to error: {e}")
                    continue

            # Try clicking the next page button
            try:
                next_button = page.query_selector("a._1LKTO3")  # Flipkart next button class
                if next_button and "disabled" not in next_button.get_attribute("class"):
                    next_button.click()
                    page.wait_for_timeout(3000)
                else:
                    break
            except Exception as e:
                print(f"Next page navigation failed: {e}")
                break

        browser.close()

    # Save to CSV
    csv_file = "flipkart_reviews.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Rating", "Title", "Review", "Buyer Info"])
        writer.writeheader()
        writer.writerows(reviews)

    return csv_file

# Sentiment analysis functions
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return polarity

def classify_sentiment(polarity):
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"

# Streamlit App
st.title("🛍️ Flipkart Review Analyzer")
st.write("Enter a Flipkart product **Review Page URL** to analyze its reviews and check if it is a **Good Buy or Bad Buy**!")

url = st.text_input("Paste Flipkart Product Review URL:")

if st.button("Analyze"):
    if not url:
        st.warning("Please enter a valid Flipkart Review URL.")
    else:
        with st.spinner("Scraping reviews... Please wait ⏳"):
            csv_file = scrape_flipkart_reviews(url, num_pages=2)

        df = pd.read_csv(csv_file)

        st.success(f"✅ Scraped {len(df)} reviews.")

        # Run sentiment analysis
        df["Polarity"] = df["Review"].apply(analyze_sentiment)
        df["Sentiment"] = df["Polarity"].apply(classify_sentiment)

        # Summary stats
        positive_count = (df["Sentiment"] == "Positive").sum()
        negative_count = (df["Sentiment"] == "Negative").sum()
        neutral_count = (df["Sentiment"] == "Neutral").sum()
        total_reviews = len(df)

        st.write(f"✅ Total Reviews: {total_reviews}")
        st.write(f"✅ Positive Reviews: {positive_count} ({positive_count/total_reviews*100:.1f}%)")
        st.write(f"❌ Negative Reviews: {negative_count} ({negative_count/total_reviews*100:.1f}%)")
        st.write(f"😐 Neutral Reviews: {neutral_count} ({neutral_count/total_reviews*100:.1f}%)")

        # Final Verdict
        if positive_count / total_reviews >= 0.6:
            st.success("🎉 Final Verdict: GOOD BUY ✅")
        elif negative_count / total_reviews >= 0.4:
            st.error("⚠️ Final Verdict: BAD BUY ❌")
        else:
            st.info("🤔 Final Verdict: NEUTRAL / MIXED")

        # Show full dataframe
        with st.expander("See All Reviews"):
            st.dataframe(df[["Rating", "Title", "Review", "Buyer Info", "Sentiment"]])

        # Save updated CSV
        df.to_csv("flipkart_reviews_with_sentiment.csv", index=False)
        st.info("📄 Detailed results saved to `flipkart_reviews_with_sentiment.csv`.")

