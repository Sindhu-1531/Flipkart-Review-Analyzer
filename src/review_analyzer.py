# review_analyzer.py

import pandas as pd
from textblob import TextBlob

def analyze_sentiment(text):
    # TextBlob gives polarity between -1.0 (negative) to 1.0 (positive)
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

def main():
    # Load your CSV file
    csv_file = "flipkart_reviews.csv"
    df = pd.read_csv(csv_file)

    # Analyze each review
    df["Polarity"] = df["Review"].apply(analyze_sentiment)
    df["Sentiment"] = df["Polarity"].apply(classify_sentiment)

    # Summary statistics
    positive_count = (df["Sentiment"] == "Positive").sum()
    negative_count = (df["Sentiment"] == "Negative").sum()
    neutral_count = (df["Sentiment"] == "Neutral").sum()

    total_reviews = len(df)

    print(f"\n Total Reviews: {total_reviews}")
    print(f" Positive Reviews: {positive_count} ({positive_count/total_reviews*100:.1f}%)")
    print(f" Negative Reviews: {negative_count} ({negative_count/total_reviews*100:.1f}%)")
    print(f" Neutral Reviews: {neutral_count} ({neutral_count/total_reviews*100:.1f}%)")

    # Simple Good Buy Decision
    if positive_count / total_reviews >= 0.6:
        print("\n Final Verdict: GOOD BUY ")
    elif negative_count / total_reviews >= 0.4:
        print("\n Final Verdict: BAD BUY ")
    else:
        print("\n Final Verdict: NEUTRAL / MIXED")

    # Save updated CSV with sentiment columns
    output_file = "flipkart_reviews_with_sentiment.csv"
    df.to_csv(output_file, index=False)
    print(f"\n Detailed results saved to {output_file}")

if __name__ == "__main__":
    main()
