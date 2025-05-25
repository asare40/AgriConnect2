import pandas as pd
import numpy as np
import random

regions = ['Kano', 'Oyo', 'Benue', 'Kaduna', 'Plateau']
crop_types = ['Maize', 'Rice', 'Tomatoes', 'Yam', 'Cassava']
education_levels = ['Primary', 'Secondary', 'Tertiary']
phone_types = ['Basic', 'Feature', 'Smart']
financial_access_levels = ['None', 'Limited', 'Some', 'Full']
genders = ['Male', 'Female', 'Other']

def random_lat_long(region):
    # Simple mapping for demo
    region_map = {
        'Kano': (12.0, 8.5),
        'Oyo': (7.5, 3.9),
        'Benue': (7.7, 8.6),
        'Kaduna': (10.5, 7.4),
        'Plateau': (9.2, 8.9)
    }
    lat, long = region_map[region]
    return lat + random.uniform(-0.5, 0.5), long + random.uniform(-0.5, 0.5)

def generate_farmer_row(i):
    region = random.choice(regions)
    crop = random.choice(crop_types)
    age = random.randint(18, 35)
    education = random.choice(education_levels)
    farm_size = round(random.uniform(0.5, 5.0), 1)
    phone = random.choice(phone_types)
    fin_access = random.choice(financial_access_levels)
    experience = random.randint(0, age - 16)
    extension_access = random.choice(['Yes', 'No'])
    cooperative_member = random.choice(['Yes', 'No'])
    irrigation_access = random.choice(['Yes', 'No'])
    dependents = random.randint(0, 5)
    gender = random.choice(genders)
    lat, long = random_lat_long(region)
    return [
        f"YF{i:03d}", region, crop, age, education, farm_size, phone, fin_access,
        experience, extension_access, cooperative_member, irrigation_access,
        dependents, gender, round(lat, 4), round(long, 4)
    ]

def main(n=100):
    rows = [generate_farmer_row(i) for i in range(1, n+1)]
    columns = [
        'farmer_id','region','crop_type','age','education_level','farm_size','phone_type',
        'financial_access','experience_years','extension_access','cooperative_member',
        'irrigation_access','dependents','gender','latitude','longitude'
    ]
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv("youth_farmers.csv", index=False)
    print(f"Generated youth_farmers.csv with {n} rows.")

if __name__ == "__main__":
    main(200)  # Change to desired number of farmers