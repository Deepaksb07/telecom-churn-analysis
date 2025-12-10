import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# STEP 1: Data Loading & Preprocessing (Python)
# ==========================================

# Load the dataset (Make sure 'data.csv' is in the same folder)
df = pd.read_csv('data.csv')

# Preprocessing: Convert 'TotalCharges' to numeric and handle missing values
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(0)

# Create an in-memory SQL database
conn = sqlite3.connect(':memory:')
df.to_sql('churn_data', conn, index=False, if_exists='replace')

print("Data loaded and SQL environment ready.")

# ==========================================
# STEP 2: Feature Engineering & Analysis (SQL)
# ==========================================

# SQL Query 1: Create Tenure Bands & Flag Churn
query_features = """
SELECT 
    *,
    CASE 
        WHEN tenure <= 12 THEN '0-12 Months'
        WHEN tenure > 12 AND tenure <= 24 THEN '12-24 Months'
        WHEN tenure > 24 AND tenure <= 48 THEN '24-48 Months'
        ELSE '> 48 Months' 
    END AS Tenure_Band
FROM churn_data
"""
df_transformed = pd.read_sql(query_features, conn)

# SQL Query 2: Validate the "Month-to-Month" Insight
# Finding: % of churners who are Month-to-Month with < 3 months tenure
query_insight = """
SELECT
    COUNT(*) as Total_Churners,
    SUM(CASE WHEN Contract = 'Month-to-month' AND tenure < 3 THEN 1 ELSE 0 END) as Target_Segment,
    (CAST(SUM(CASE WHEN Contract = 'Month-to-month' AND tenure < 3 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 as Percentage
FROM churn_data
WHERE Churn = 'Yes'
"""
insight_df = pd.read_sql(query_insight, conn)
print("\n--- Insight Verification ---")
print(insight_df)

# SQL Query 3: Aggregate Data for Heatmap
query_heatmap = """
SELECT 
    Contract,
    PaymentMethod,
    CAST(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as Churn_Rate
FROM churn_data
GROUP BY Contract, PaymentMethod
"""
heatmap_df = pd.read_sql(query_heatmap, conn)

# ==========================================
# STEP 3: Visualization (Python)
# ==========================================

# 1. Heatmap: Churn Risk by Contract & Payment Method
heatmap_matrix = heatmap_df.pivot(index='Contract', columns='PaymentMethod', values='Churn_Rate')

plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_matrix, annot=True, fmt=".0%", cmap='Reds', linewidths=.5)
plt.title('Churn Rate Heatmap: Contract vs Payment Method')
plt.tight_layout()
plt.savefig('churn_heatmap.png') # Saves the image
plt.show()

# 2. Histogram: Tenure Distribution
plt.figure(figsize=(10, 6))
sns.histplot(data=df_transformed, x='tenure', hue='Churn', multiple='stack', palette='viridis')
plt.title('Customer Tenure Distribution (Churn vs Retained)')
plt.xlabel('Tenure (Months)')
plt.savefig('tenure_histogram.png') # Saves the image
plt.show()

print("\nAnalysis Complete. Images saved as 'churn_heatmap.png' and 'tenure_histogram.png'.")