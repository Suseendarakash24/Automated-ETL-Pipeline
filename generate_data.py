import pandas as pd
import numpy as np
import random

# 1. Load the original dataset
df = pd.read_csv('india_job_market_2024_2026.csv')

# 2. DUPLICATES: Triple the dataset size with exact and near duplicates
df_dup1 = df.copy()
df_dup2 = df.copy()
df_dup2['Job_ID'] = df_dup2['Job_ID'] + '_DUP'  # Near duplicate with altered ID
df = pd.concat([df, df_dup1, df_dup2], ignore_index=True)

# Shuffle the dataframe to mix duplicates randomly
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. MISSING VALUES: Introduce NaNs and empty strings (~15% of target columns)
cols_to_corrupt = ['City', 'Skills_Required', 'Salary_LPA', 'Company_Rating', 'Education_Required']
for col in cols_to_corrupt:
    mask_nan = np.random.rand(len(df)) < 0.15
    df.loc[mask_nan, col] = np.nan
    mask_empty = np.random.rand(len(df)) < 0.05
    df.loc[mask_empty, col] = ''

# 4. FORMATTING ERRORS
# Salary_LPA: Mix formats, add text, commas, or negative signs
def corrupt_salary(x):
    if pd.isna(x): return x
    x = float(x)
    choices = [f"{x} LPA", f"{x:.1f}", f"{int(x)}", f"{str(x).replace('.', ',')}", f"-{x}", f"~{x}"]
    return random.choice(choices) if random.random() < 0.25 else x
df['Salary_LPA'] = df['Salary_LPA'].apply(corrupt_salary)

# Date_Posted: Mix formats and add invalid dates
def corrupt_date(x):
    if pd.isna(x): return x
    choices = [
        x, 
        x.replace('-', '/'), 
        f"{x.split('-')[2]}/{x.split('-')[1]}/{x.split('-')[0]}", # DD/MM/YYYY
        "TBD", "Pending", "2025-13-45" # Invalid dates
    ]
    return random.choice(choices) if random.random() < 0.20 else x
df['Date_Posted'] = df['Date_Posted'].apply(corrupt_date)

# Location_Tier: Inconsistent casing and abbreviations
def corrupt_tier(x):
    if pd.isna(x): return x
    choices = [x, x.lower(), x.replace(' ', '-'), 'Tier One', 'T1', 'Unknown', 'NA']
    return random.choice(choices) if random.random() < 0.20 else x
df['Location_Tier'] = df['Location_Tier'].apply(corrupt_tier)

# Company_Rating: Out of bounds (e.g., > 5.0) and text
def corrupt_rating(x):
    if pd.isna(x): return x
    choices = [x, 5.5, 6.0, 0.0, -1.2, 'N/A', 'Five', '4.5/5']
    return random.choice(choices) if random.random() < 0.15 else x
df['Company_Rating'] = df['Company_Rating'].apply(corrupt_rating)

# Openings/Applicants: Floats, negatives, or text
for col in ['Openings', 'Applicants']:
    def corrupt_count(x):
        if pd.isna(x): return x
        choices = [x, int(x), float(x), -int(x), f"{x}+"]
        return random.choice(choices) if random.random() < 0.15 else x
    df[col] = df[col].apply(corrupt_count)

# 5. LOGICAL ERRORS
# Swap Work_Mode and City for 5% of rows (e.g., City="Remote", Work_Mode="Mumbai")
swap_mask = np.random.rand(len(df)) < 0.05
df.loc[swap_mask, ['City', 'Work_Mode']] = df.loc[swap_mask, ['Work_Mode', 'City']].values

# Internships with "Lead (10+ yrs)" experience
intern_mask = (df['Job_Type'] == 'Internship') & (np.random.rand(len(df)) < 0.1)
df.loc[intern_mask, 'Experience_Level'] = 'Lead (10+ yrs)'

# Freshers requiring a PhD
fresher_mask = (df['Experience_Level'] == 'Fresher (0-1 yr)') & (np.random.rand(len(df)) < 0.1)
df.loc[fresher_mask, 'Education_Required'] = 'PhD'

# 6. Save the corrupted dataset
df.to_csv('india_job_market_corrupted.csv', index=False)
print("✅ Successfully generated 'india_job_market_corrupted.csv' with heavy errors and duplicates!")