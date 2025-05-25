import pandas as pd
import numpy as np

np.random.seed(42)

N = 200  # Number of farmers

# Possible values
crops = ['Tomatoes', 'Yam', 'Rice', 'Maize', 'Cassava']
regions = ['Kano', 'Oyo', 'Benue', 'Kaduna', 'Plateau']
edu_levels = ['Primary', 'Secondary', 'Tertiary']
tech_lit = ['Low', 'Medium', 'High']
fin_access = ['None', 'Some', 'Limited', 'Full']

# Generate farmers
farmer_ids = [f'YF{1000+i}' for i in range(N)]
ages = np.random.randint(20, 35, size=N)
education = np.random.choice(edu_levels, size=N, p=[0.3,0.5,0.2])
farm_size = np.round(np.random.uniform(0.5, 5.0, size=N), 2)
crop_type = np.random.choice(crops, size=N)
region = np.random.choice(regions, size=N)
tech_literacy = np.random.choice(tech_lit, size=N, p=[0.2,0.5,0.3])
financial_access = np.random.choice(fin_access, size=N, p=[0.2,0.3,0.3,0.2])
prev_loan = np.random.binomial(1, 0.4, size=N)
repayment_status = np.random.binomial(1, 0.7 - 0.2*prev_loan, size=N)  # those with previous loans slightly lower repayment

# Build credit dataframe
credit_df = pd.DataFrame({
    "farmer_id": farmer_ids,
    "age": ages,
    "education": education,
    "farm_size": farm_size,
    "crop_type": crop_type,
    "region": region,
    "tech_literacy": tech_literacy,
    "financial_access": financial_access,
    "prev_loan": prev_loan,
    "repayment_status": repayment_status
})

credit_df.to_csv("synthetic_loan_repayment_large.csv", index=False)

# Synthesize PHL risk results
phl_risk_score = np.clip(np.random.beta(2, 3, N) + (crop_type == "Tomatoes")*0.25 + (region == "Kano")*0.10, 0, 1)
avg_annual_phl_loss = np.round(phl_risk_score * np.random.uniform(0.07, 0.25, N), 3)
interventions_adopted = np.random.randint(0, 4, N)

phl_df = pd.DataFrame({
    "farmer_id": farmer_ids,
    "phl_risk_score": np.round(phl_risk_score, 2),
    "avg_annual_phl_loss": avg_annual_phl_loss,
    "interventions_adopted": interventions_adopted
})

phl_df.to_csv("phl_risk_results_large.csv", index=False)

print("Synthetic datasets generated: synthetic_loan_repayment_large.csv and phl_risk_results_large.csv")