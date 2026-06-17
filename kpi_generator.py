import pandas as pd

superstore = pd.read_csv(
    "datasets/Superstore.csv",
    encoding="latin1"
)

complaints = pd.read_csv(
    "datasets/StoreComplaints_Updated.csv"
)
# Sales KPIs

total_revenue = superstore["Sales"].sum()

total_profit = superstore["Profit"].sum()

total_orders = superstore["Order ID"].nunique()

profit_margin = (total_profit / total_revenue) * 100

# Complaint KPIs

total_complaints = complaints.shape[0]

complaints_by_type = (complaints["Complaint Type"] .value_counts())

print("\n===== BUSINESS HEALTH KPIs =====\n")

print(f"Total Revenue      : ${total_revenue:,.2f}")

print(f"Total Profit       : ${total_profit:,.2f}")

print(f"Total Orders       : {total_orders}")

print(f"Profit Margin      : {profit_margin:.2f}%")

print(f"Total Complaints   : {total_complaints}")

print("\n===== COMPLAINT BREAKDOWN =====\n")

for complaint_type, count in complaints_by_type.items():
    print(f"{complaint_type}: {count}")