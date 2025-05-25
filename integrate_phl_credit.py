import pandas as pd

# Load credit data and PHL risk outputs
credit_df = pd.read_csv('synthetic_loan_repayment.csv')
phl_risk_df = pd.read_csv('phl_risk_results.csv')  # Output from your PHL model

# Merge on farmer_id (or other unique identifier)
full_df = pd.merge(credit_df, phl_risk_df, on='farmer_id', how='left')

# Example: Use PHL risk as extra feature for credit scoring
from sklearn.ensemble import RandomForestClassifier

X = full_df[['age', 'education', 'farm_size', 'crop_type', 'region', 
             'tech_literacy', 'financial_access', 'prev_loan', 'phl_risk_score']]
y = full_df['repayment_status']

clf = RandomForestClassifier()
clf.fit(X, y)

# Predict credit risk with PHL context for new applicants
# full_df['predicted_credit_risk'] = clf.predict_proba(X)[:, 1]