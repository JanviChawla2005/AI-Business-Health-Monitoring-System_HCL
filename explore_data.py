import pandas as pd

superstore = pd.read_csv("datasets/Superstore.csv", encoding="latin1")
complaints = pd.read_csv("datasets/StoreComplaints_Updated.csv")

print("SUPERSTORE")
print(superstore.info())

print("\nCOMPLAINTS")
print(complaints.info())

print("\nMissing Values - Superstore")
print(superstore.isnull().sum())

print("\nMissing Values - Complaints")
print(complaints.isnull().sum())