import pandas as pd

# TfidfVectorizer converts our text into numbers
from sklearn.feature_extraction.text import TfidfVectorizer

# LogisticRegression is our ML model
# Think of it as a smart decision maker
from sklearn.linear_model import LogisticRegression

# These help us split data and check accuracy
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# pickle saves our trained model to a file
# So we don't have to retrain every time
import pickle

# Load our cleaned dataset
df = pd.read_csv('../dataset/cleaned_reviews.csv')

print("✅ Dataset loaded successfully")
print(f"Total reviews: {len(df)}")

# X = input (the review text)
# y = output (fake=1 or real=0)
# Fill any remaining empty values with empty string
# astype(str) converts everything to text just to be safe
df['cleaned_text'] = df['cleaned_text'].fillna('')
df['cleaned_text'] = df['cleaned_text'].astype(str)
X = df['cleaned_text']
y = df['label_num']

# Split data into training and testing
# 80% of data = model learns from this (training)
# 20% of data = we test how good our model is (testing)
# random_state=42 means we get same split every time we run
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✅ Data split done:")
print(f"Training reviews: {len(X_train)}")
print(f"Testing reviews: {len(X_test)}")

# Convert text to numbers using TF-IDF
# max_features=5000 means we only use top 5000 important words
tfidf = TfidfVectorizer(max_features=5000)

# fit_transform = learn the words AND convert training text to numbers
X_train_tfidf = tfidf.fit_transform(X_train)

# transform = only convert testing text to numbers (don't learn again)
X_test_tfidf = tfidf.transform(X_test)

print("\n✅ Text converted to numbers using TF-IDF")

# Create and train our ML model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

print("\n✅ Model trained successfully!")

# Test our model on the 20% testing data
y_pred = model.predict(X_test_tfidf)

# Check accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n=== Model Accuracy ===")
print(f"Accuracy: {accuracy * 100:.2f}%")

# Detailed report
print("\n=== Detailed Report ===")
print(classification_report(y_test, y_pred, 
      target_names=['Real (OR)', 'Fake (CG)']))

# Save the trained model and tfidf to files
# So we can use them later in our Flask API
pickle.dump(model, open('../backend/model/model.pkl', 'wb'))
pickle.dump(tfidf, open('../backend/model/tfidf.pkl', 'wb'))

print("\n✅ Model saved to backend/model/")