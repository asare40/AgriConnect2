import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# Load datasets
credit_df = pd.read_csv('synthetic_loan_repayment_large.csv')
phl_df = pd.read_csv('phl_risk_results_large.csv')  # Output from your PHL model

# Merge on farmer_id
df = pd.merge(credit_df, phl_df, on='farmer_id', how='left')

# Fill missing PHL values (if any) with safe defaults
df['phl_risk_score'] = df['phl_risk_score'].fillna(df['phl_risk_score'].mean())
df['avg_annual_phl_loss'] = df['avg_annual_phl_loss'].fillna(0)
df['interventions_adopted'] = df['interventions_adopted'].fillna(0)

# Encode categorical variables
df['education'] = df['education'].astype('category').cat.codes
df['crop_type'] = df['crop_type'].astype('category').cat.codes
df['region'] = df['region'].astype('category').cat.codes
df['financial_access'] = df['financial_access'].astype('category').cat.codes
df['tech_literacy'] = df['tech_literacy'].astype('category').cat.codes

# Features and label
features = [
    'age', 'education', 'farm_size', 'crop_type', 'region', 'tech_literacy',
    'financial_access', 'prev_loan', 'phl_risk_score', 'avg_annual_phl_loss', 'interventions_adopted'
]
X = df[features]
y = df['repayment_status']

# Use stratified split to preserve class balance in train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Check class balance in train/test
print("Unique values in y_train:", np.unique(y_train, return_counts=True))
print("Unique values in y_test:", np.unique(y_test, return_counts=True))

# Train credit model (Random Forest)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
probs = model.predict_proba(X_test)
if probs.shape[1] == 2:
    y_proba = probs[:, 1]
else:
    # Only one class present in y_test; fallback to zeros or ones
    y_proba = np.zeros(len(y_test)) if model.classes_[0] == 1 else np.ones(len(y_test))
y_pred = model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("ROC AUC Score:", roc_auc_score(y_test, y_proba))

# Feature importance
importances = model.feature_importances_
print("\nFeature importances:")
for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
    print(f"{feat}: {imp:.3f}")

# Example: Predict for a new applicant
example = X_test.iloc[0]
print("\nSample prediction (repayment probability):", model.predict_proba([example])[0, 1] if probs.shape[1] == 2 else model.predict_proba([example])[0, 0])

# (Optional) Save results for dashboard integration
# --- FULL OUTPUT for analytics ---
# You may add more columns here (e.g., crop_type, financial_access) if desired!
output_cols = [
    'farmer_id', 'region', 'crop_type', 'age', 'education', 'farm_size', 'tech_literacy',
    'financial_access', 'prev_loan', 'predicted_credit_score', 'phl_risk_score',
    'avg_annual_phl_loss', 'interventions_adopted'
]
df['predicted_credit_score'] = model.predict_proba(X)[:, 1] if model.n_classes_ == 2 else model.predict_proba(X)[:, 0]
df[output_cols].to_csv('integrated_results.csv', index=False)
print("\nSaved integrated_results.csv with all needed analytics fields.")