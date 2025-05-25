import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import matplotlib.pyplot as plt

def load_data():
    farmers = pd.read_csv('youth_farmers.csv')
    crops = pd.read_csv('crop_production.csv')
    losses = pd.read_csv('post_harvest_losses_cleaned.csv')
    loan_repay = pd.read_csv('loan_repayement.csv')
    return farmers, crops, losses, loan_repay

def preprocess_data(farmers, crops, losses, loan_repay):
    crop_yield = crops.groupby(['region', 'crop_type'])['yield'].mean().reset_index()
    loss_rate = losses.groupby(['region', 'crop_type'])['loss_rate'].mean().reset_index()
    df = farmers.merge(crop_yield, on=['region', 'crop_type'], how='left')
    df = df.merge(loss_rate, on=['region', 'crop_type'], how='left')
    df = df.merge(loan_repay[['farmer_id', 'prev_loan', 'repayment_status']], on='farmer_id', how='left')
    df['yield'] = df['yield'].fillna(df['yield'].mean())
    df['loss_rate'] = df['loss_rate'].fillna(df['loss_rate'].mean())
    df['education_level'] = df['education_level'].map({'Primary':0, 'Secondary':1, 'Tertiary':2})
    df['tech_literacy'] = df['phone_type'].map({'Basic':0, 'Feature':1, 'Smart':2})
    df['financial_access'] = df['financial_access'].map({'None':0, 'Limited':1, 'Some':2, 'Full':3})
    df['extension_access'] = df['extension_access'].map({'No':0, 'Yes':1})
    df['cooperative_member'] = df['cooperative_member'].map({'No':0, 'Yes':1})
    df['irrigation_access'] = df['irrigation_access'].map({'No':0, 'Yes':1})
    df['gender'] = df['gender'].map({'Male':0, 'Female':1, 'Other':2})
    df = df.fillna(0)
    return df, crop_yield, loss_rate

def train_model(df):
    features = [
        'age', 'education_level', 'farm_size', 'yield', 'loss_rate', 'tech_literacy', 'financial_access',
        'prev_loan', 'experience_years', 'extension_access', 'cooperative_member', 'irrigation_access',
        'dependents', 'gender'
    ]
    X = df[features]
    y = df['repayment_status']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
    importances = pd.Series(model.feature_importances_, index=features)
    return model, features, report, roc_auc, importances

def get_advice(row, crop_yield, loss_rate):
    advice = []
    if row['credit_score'] < 60:
        if row['yield'] < crop_yield['yield'].mean():
            advice.append("Increase your crop yield (e.g., use improved seeds or practices).")
        if row['loss_rate'] > loss_rate['loss_rate'].mean():
            advice.append("Reduce post-harvest losses (improve storage, transport).")
        if row['financial_access'] < 2:
            advice.append("Adopt mobile money or join a cooperative for better financial access.")
        if row['tech_literacy'] < 2:
            advice.append("Use a smartphone for better access to markets and information.")
        if row['experience_years'] < 3:
            advice.append("Seek mentorship or training to gain more experience.")
        if row['extension_access'] == 0:
            advice.append("Access extension services for up-to-date farming advice.")
        if row['cooperative_member'] == 0:
            advice.append("Join a farmers' cooperative for support and loans.")
        if row['irrigation_access'] == 0:
            advice.append("Consider irrigation solutions to boost yields.")
    return " ".join(advice) if advice else "Keep up the good work!"

def main():
    farmers, crops, losses, loan_repay = load_data()
    df, crop_yield, loss_rate = preprocess_data(farmers, crops, losses, loan_repay)
    model, features, report, roc_auc, importances = train_model(df)
    print("Classification Report:\n", report)
    print("ROC AUC Score:", roc_auc)

    # Feature importance plot
    importances = importances.sort_values(ascending=True)
    plt.figure(figsize=(8,5))
    importances.plot(kind='barh')
    plt.title('Feature Importance in Creditworthiness')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    plt.show()

    # Generate credit scores
    df['credit_score'] = (model.predict_proba(df[features])[:,1] * 100).round(1)
    df['improvement_advice'] = df.apply(lambda row: get_advice(row, crop_yield, loss_rate), axis=1)

    # Export scorecard
    df[['farmer_id', 'region', 'crop_type', 'credit_score', 'improvement_advice']].to_csv('farmer_credit_scores.csv', index=False)
    print("Credit scores with advice saved to farmer_credit_scores.csv")
    print(df[['farmer_id', 'region', 'crop_type', 'credit_score', 'improvement_advice']].head(10))

if __name__ == "__main__":
    main()