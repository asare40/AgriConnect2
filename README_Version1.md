# Youth Farmer Credit Scoring and Analysis Platform

## Overview

This project predicts the creditworthiness of youth farmers using real agricultural, financial, and tech adoption data, and provides actionable advice to help them access affordable finance.

## Features

- **Live Analysis:** Upload or enter data and instantly get credit scores and advice.
- **Dashboard:** View all farmers, filter by region/crop, visualize trends and risk.
- **Documentation:** Learn how the model works, data sources, and how to use the tool.

## How It Works

1. **Upload Data:** Add farmer or batch data in CSV format.
2. **Predict:** The model estimates credit score and repayment probability.
3. **Advise:** Get tailored recommendations to boost eligibility and success.
4. **Visualize:** Explore distributions, trends, and feature importance.

## Data Dictionary

| Field             | Description                                 |
|-------------------|---------------------------------------------|
| age               | Farmer's age                                |
| education_level   | 0=Primary, 1=Secondary, 2=Tertiary          |
| farm_size         | Hectares farmed                             |
| yield             | Average crop yield                          |
| loss_rate         | Post-harvest loss percent                   |
| tech_literacy     | 0=Basic, 1=Feature phone, 2=Smartphone      |
| financial_access  | 0=None, 1=Limited, 2=Some, 3=Full           |
| prev_loan         | 0=No, 1=Yes                                 |

## Requirements

- Python 3.x
- pandas, scikit-learn, streamlit, matplotlib

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Contact

For support, contact [Your Name] or open an issue.