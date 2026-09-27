# pandas is a library that helps us read and work with data files like CSV
import pandas as pd

# Load the CSV file into a "DataFrame" 
# DataFrame = think of it like an Excel sheet in Python
df = pd.read_csv('../dataset/reviews.csv')

# Show the first 5 rows so we can see what our data looks like
print("=== First 5 rows of data ===")
print(df.head())

# Show how many rows and columns we have
print("\n=== Dataset Size ===")
print(f"Total reviews: {df.shape[0]}")
print(f"Total columns: {df.shape[1]}")

# Show column names
print("\n=== Column Names ===")
print(df.columns.tolist())

# Count how many fake (CG) vs real (OR) reviews we have
print("\n=== Fake vs Real Reviews ===")
print(df['label'].value_counts())