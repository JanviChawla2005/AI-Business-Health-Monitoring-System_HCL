import pandas as pd

superstore = pd.read_csv(
    "datasets/Superstore.csv",
    encoding="latin1"
)

complaints = pd.read_csv(
    "datasets/StoreComplaints_Updated.csv"
)

# Convert date columns

superstore["Order Date"] = pd.to_datetime(
    superstore["Order Date"]
)

superstore["Ship Date"] = pd.to_datetime(
    superstore["Ship Date"]
)

complaints["Date of Complaint"] = pd.to_datetime(
    complaints["Date of Complaint"]
)

print(superstore.dtypes)
print()
print(complaints.dtypes)

print("\nSUPERSTORE SAMPLE")
print(superstore.head())

print("\nCOMPLAINTS SAMPLE")
print(complaints.head())