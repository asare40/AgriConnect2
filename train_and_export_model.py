import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# 1. Load your data
df = pd.read_csv("youth_farmers.csv")
df.columns = df.columns.str.strip()

# 2. Preprocess categorical columns
# Map gender
df['gender_code'] = df['gender'].map({'Male': 0, 'Female': 1, 'Other': 2})

# Map education_level
edu_map = {'Primary': 0, 'Secondary': 1, 'Tertiary': 2}
df['education_level_code'] = df['education_level'].map(edu_map)

# Map phone_type
phone_map = {'Basic phone': 0, 'Feature phone': 1, 'Smartphone': 2}
df['phone_type_code'] = df['phone_type'].map(phone_map)

# Map financial_access
fin_map = {'None': 0, 'Limited': 1, 'Some': 2, 'Full': 3}
df['financial_access_code'] = df['financial_access'].map(fin_map)

# Map extension_access, cooperative_member, irrigation_access
yn_map = {'No': 0, 'Yes': 1}
df['extension_access_code'] = df['extension_access'].map(yn_map)
df['cooperative_member_code'] = df['cooperative_member'].map(yn_map)
df['irrigation_access_code'] = df['irrigation_access'].map(yn_map)

# (Optional) Map region and crop_type if you want to use them
# df['region_code'] = df['region'].astype('category').cat.codes
# df['crop_type_code'] = df['crop_type'].astype('category').cat.codes

# 3. Create a synthetic target: creditworthy (for demo purposes)
# We'll say farmers with tertiary education, smartphone, full financial access, and cooperative membership are creditworthy.
df['creditworthy'] = (
    (df['education_level_code'] == 2) &
    (df['phone_type_code'] == 2) &
    (df['financial_access_code'] == 3) &
    (df['cooperative_member_code'] == 1)
).astype(int)

# 4. Prepare features for the model
feature_cols = [
    'age',
    'education_level_code',
    'farm_size',
    'phone_type_code',
    'financial_access_code',
    'experience_years',
    'extension_access_code',
    'cooperative_member_code',
    'irrigation_access_code',
    'dependents',
    'gender_code'
]

X = df[feature_cols]
y = df['creditworthy']

# 5. Split data for training/testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train the model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Optional: Print test accuracy
acc = clf.score(X_test, y_test)
print(f"Test accuracy: {acc:.2f}")

# 7. Export the trained model
joblib.dump(clf, "your_model.joblib")
print("Model exported as your_model.joblib")