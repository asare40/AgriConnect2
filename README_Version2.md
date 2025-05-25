# Youth Farmer Credit Scoring and Dashboard

## Overview

This project predicts the creditworthiness of youth farmers using agricultural, financial, and technology adoption data, and provides data-driven advice to improve access to affordable finance.

## Features

- **Live Analysis:** Enter farmer data for instant credit scoring and advice.
- **Dashboard:** View, filter, and analyze all farmer scores and advice.
- **Batch Upload:** Upload new farmer data in CSV format.
- **Visualizations:** Score distributions, feature importance, and model metrics.
- **Documentation:** Data dictionary, user guide, and contact info.

## Files & Data

Place all these CSV files in a `data` folder or the root directory:

| Filename                     | Description                                           |
|------------------------------|------------------------------------------------------|
| youth_farmers.csv            | Farmer demographics and farm/tech/finance info       |
| crop_production.csv          | Crop yield/production data by region and crop        |
| post_harvest_losses_cleaned.csv | Post-harvest loss rates by crop and region        |
| loan_repayement.csv          | Loan history and repayment status for each farmer    |

## How to Run

1. Install requirements:
    ```bash
    pip install streamlit pandas scikit-learn matplotlib
    ```
2. Place all required CSV files in the same folder as `app.py`.
3. Start the dashboard:
    ```bash
    streamlit run app.py
    ```
4. Open the link provided by Streamlit in your browser.

## Data Dictionary

| Field             | Description                                 |
|-------------------|---------------------------------------------|
| age               | Farmer's age                                |
| education_level   | 0=Primary, 1=Secondary, 2=Tertiary          |
| farm_size         | Hectares farmed                             |
| yield             | Average crop yield                          |
| loss_rate         | Post-harvest loss percent                   |
| tech_literacy     | 0=Basic, 1=Feature, 2=Smartphone            |
| financial_access  | 0=None, 1=Limited, 2=Some, 3=Full           |
| prev_loan         | 0=No, 1=Yes                                 |

## How it helps

- **For Farmers:** Understand and improve your credit score; get actionable steps for better finance access.
- **For Lenders/NGOs:** Quickly assess risk and target advice/interventions at scale.

## Contact

For support or questions, contact the project maintainer or open an issue.