import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# --- STEP 1: LOAD DATA ---
# (Using the method that worked for you)
try:
    df = pd.read_csv('data.csv') 
except FileNotFoundError:
    # Fallback to the long name if data.csv doesn't exist
    df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Clean TotalCharges
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

# Connect to SQL
conn = sqlite3.connect(':memory:')
df.to_sql('churn_data', conn, index=False, if_exists='replace')

# --- STEP 2: COMPLEX SQL FEATURE ENGINEERING ---
# Goal: Count how many "extra services" a customer has and calculate Average Revenue per User (ARPU)
query_advanced = """
SELECT 
    *,
    (CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN OnlineBackup = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN DeviceProtection = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN StreamingTV = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN StreamingMovies = 'Yes' THEN 1 ELSE 0 END) as Num_Services,
     
    CASE 
        WHEN tenure > 0 THEN TotalCharges / tenure 
        ELSE 0 
    END as Avg_Monthly_Spend_Calculated
FROM churn_data
"""
df_augmented = pd.read_sql(query_advanced, conn)

# --- STEP 3: VISUALIZATIONS (Adding 3 New Charts) ---

# Set the style
sns.set_style("whitegrid")

# Chart 3: Churn Rate by Internet Service Type
# This often reveals that "Fiber Optic" users churn more (high competition?)
plt.figure(figsize=(8, 5))
sns.countplot(data=df_augmented, x='InternetService', hue='Churn', palette='Set1')
plt.title('Churn Count by Internet Service Type')
plt.ylabel('Number of Customers')
plt.savefig('internet_service_churn.png')
plt.show()

# Chart 4: Monthly Charges Box Plot
# Do churners pay more on average?
plt.figure(figsize=(8, 5))
sns.boxplot(data=df_augmented, x='Churn', y='MonthlyCharges', palette='Pastel1')
plt.title('Distribution of Monthly Charges: Churn vs Retained')
plt.savefig('monthly_charges_boxplot.png')
plt.show()

# Chart 5: Does having more services reduce churn? (The "Sticky" Factor)
plt.figure(figsize=(8, 5))
sns.countplot(data=df_augmented, x='Num_Services', hue='Churn', palette='viridis')
plt.title('Churn by Number of Add-on Services')
plt.xlabel('Number of Services (0 to 6)')
plt.ylabel('Count')
plt.legend(title='Churn')
plt.savefig('num_services_churn.png')
plt.show()

print("Phase 2 Complete. Images saved: internet_service_churn.png, monthly_charges_boxplot.png, num_services_churn.png")