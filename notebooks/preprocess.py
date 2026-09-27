import pandas as pd

# re is a library for finding and replacing text patterns
import re

# Load our dataset
df = pd.read_csv('../dataset/cleaned_reviews.csv')
df = df.dropna(subset=['cleaned_text'])

# Function to clean a single review
# Think of it as a text washing machine
def clean_text(text):
    # Convert everything to lowercase
    # So "FAKE" and "fake" are treated the same
    text = text.lower()
    
    # Remove punctuation and special characters
    # Only keep letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra spaces
    text = text.strip()
    
    return text

# dropna removes all rows where text_ column is empty
df = df.dropna(subset=['text_'])

# Apply our cleaning function to every review in text_ column
df['cleaned_text'] = df['text_'].apply(clean_text)

# Convert labels to numbers
# ML models understand numbers not words
# CG (fake) = 1, OR (real) = 0
df['label_num'] = df['label'].apply(lambda x: 1 if x == 'CG' else 0)

# Show sample of cleaned data
print("=== Original vs Cleaned Text ===")
print("\nOriginal:", df['text_'][0])
print("\nCleaned:", df['cleaned_text'][0])

print("\n=== Label Conversion ===")
print(df[['label', 'label_num']].head())

# Save cleaned data to dataset folder
df.to_csv('../dataset/cleaned_reviews.csv', index=False)
print("\n✅ Cleaned data saved to dataset/cleaned_reviews.csv")