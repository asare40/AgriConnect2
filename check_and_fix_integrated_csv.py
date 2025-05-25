import os
import pandas as pd

REQUIRED_COLS = ['region', 'phl_risk_score', 'predicted_credit_score', 'interventions_adopted']
FILENAME = "integrated_results.csv"

def check_and_fix_csv():
    # Step 1: Check for file existence
    if not os.path.isfile(FILENAME):
        print(f"ERROR: {FILENAME} not found in this folder.")
        print("If you have 'phl_credit_pipeline.py', run it to generate the file.")
        return

    df = pd.read_csv(FILENAME)
    print(f"Loaded {FILENAME} - shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    if not missing:
        print("✅ All required columns are present! No fix needed.")
        print(df.head())
        return

    print(f"Missing columns: {missing}")

    # Step 2: Try to reconstruct from sources if available
    sources = {
        "credit": "synthetic_loan_repayment_large.csv",
        "phl": "phl_risk_results_large.csv"
    }
    if not (os.path.isfile(sources["credit"]) and os.path.isfile(sources["phl"])):
        print("Could not find one or both of the source CSVs to auto-fix. Please re-run your pipeline or add the columns manually.")
        return

    credit = pd.read_csv(sources["credit"])
    phl = pd.read_csv(sources["phl"])

    # Merge on farmer_id (assumed key)
    merged = pd.merge(credit, phl, on='farmer_id', how='left')

    # Fill missing PHL columns
    if 'phl_risk_score' in missing:
        merged['phl_risk_score'] = merged.get('phl_risk_score', pd.Series([0]*len(merged)))
    if 'interventions_adopted' in missing:
        merged['interventions_adopted'] = merged.get('interventions_adopted', pd.Series([0]*len(merged)))
    if 'predicted_credit_score' in missing:
        # If you have a model, you should re-run your pipeline to get this. Here, we fill with 0.5 as placeholder.
        merged['predicted_credit_score'] = merged.get('predicted_credit_score', pd.Series([0.5]*len(merged)))
    if 'region' in missing:
        merged['region'] = merged.get('region', pd.Series(['Unknown']*len(merged)))

    # Save fixed file
    merged.to_csv(FILENAME, index=False)
    print(f"✅ Fixed {FILENAME} with columns: {merged.columns.tolist()}")
    print(merged[REQUIRED_COLS + ['farmer_id']].head())

if __name__ == "__main__":
    check_and_fix_csv()