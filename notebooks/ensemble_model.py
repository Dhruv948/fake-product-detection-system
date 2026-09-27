import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# VotingClassifier combines multiple models into one
from sklearn.ensemble import VotingClassifier

# CalibratedClassifierCV makes LinearSVC work with VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
import pickle

# Load cleaned dataset
df = pd.read_csv('../dataset/cleaned_reviews.csv')
df['cleaned_text'] = df['cleaned_text'].fillna('')
df['cleaned_text'] = df['cleaned_text'].astype(str)

print("✅ Dataset loaded")

# X = review text, y = fake or real
X = df['cleaned_text']
y = df['label_num']

# Split data 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Convert text to numbers using TF-IDF
# ngram_range=(1,2) means we look at single words AND pairs of words
# Example: "not good" is more meaningful than just "good"
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

print("✅ TF-IDF conversion done")

# Create our 3 individual models
# Model 1: Logistic Regression
lr = LogisticRegression(max_iter=1000)

# Model 2: Naive Bayes - works great with text
nb = MultinomialNB()

# Model 3: Linear SVC - powerful text classifier
# CalibratedClassifierCV wraps it so it works in VotingClassifier
svc = CalibratedClassifierCV(LinearSVC(max_iter=1000))

# Combine all 3 into one Ensemble model
# voting='soft' means they share confidence scores not just yes/no votes
ensemble = VotingClassifier(
    estimators=[
        ('lr', lr),
        ('nb', nb),
        ('svc', svc)
    ],
    voting='soft'
)

print("\n⏳ Training ensemble model... (this may take 2-3 minutes)")

# Train the ensemble model
ensemble.fit(X_train_tfidf, y_train)

print("✅ Ensemble model trained!")

# Test accuracy
y_pred = ensemble.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n=== Ensemble Model Accuracy ===")
print(f"Accuracy: {accuracy * 100:.2f}%")

print("\n=== Detailed Report ===")
print(classification_report(y_test, y_pred,
      target_names=['Real (OR)', 'Fake (CG)']))

# Save ensemble model and tfidf
# We overwrite the old model with our better one
pickle.dump(ensemble, open('../backend/model/model.pkl', 'wb'))
pickle.dump(tfidf, open('../backend/model/tfidf.pkl', 'wb'))

print("\n✅ Ensemble model saved to backend/model/")