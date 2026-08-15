import sqlite3
import pandas as pd

superstore = pd.read_csv(
    "datasets/Superstore.csv",
    encoding="latin1"
)

complaints = pd.read_csv(
    "datasets/StoreComplaints_Updated.csv"
)

complaints_ai = pd.read_csv(
    "datasets/StoreComplaints_AI_Analyzed.csv"
)

connection = sqlite3.connect("business_warehouse.db")

superstore.to_sql(
    "superstore",
    connection,
    if_exists="replace",
    index=False
)

complaints.to_sql(
    "complaints",
    connection,
    if_exists="replace",
    index=False
)

complaints_ai.to_sql(
    "complaints_ai",
    connection,
    if_exists="replace",
    index=False
)

print("SQL warehouse created successfully.")

print("\nTables created:")
print("- superstore")
print("- complaints")
print("- complaints_ai")

cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM superstore")
print("\nSuperstore rows:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM complaints")
print("Complaint rows:", cursor.fetchone()[0])

cursor.execute("SELECT COUNT(*) FROM complaints_ai")
print("AI complaint rows:", cursor.fetchone()[0])

connection.close()

print("\nSQL warehouse ready: business_warehouse.db")