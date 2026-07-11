from data_preprocessing import superstore, complaints

revenue_by_region = superstore.groupby("Region")["Sales"].sum()

print("\n===== REVENUE BY REGION =====")
print(revenue_by_region.to_string())

profit_by_region = superstore.groupby("Region")["Profit"].sum()

print("\n===== PROFIT BY REGION =====")
print(profit_by_region.to_string())

revenue_by_segment = (superstore.groupby("Segment")["Sales"] .sum())

print("\n===== REVENUE BY SEGMENT =====")
print(revenue_by_segment.to_string())

profit_by_segment = (superstore.groupby("Segment")["Profit"].sum())

print("\n===== PROFIT BY SEGMENT =====")
print(profit_by_segment.to_string())

sales_by_category = superstore.groupby("Category")["Sales"].sum()

print("\n===== SALES BY CATEGORY =====")
print(sales_by_category.to_string())

profit_by_category = superstore.groupby("Category")["Profit"].sum()

print("\n===== PROFIT BY CATEGORY =====")
print(profit_by_category.to_string())

sales_by_subcategory = (
    superstore.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== SALES BY SUB-CATEGORY =====")
print(sales_by_subcategory.to_string())

profit_by_subcategory = (
    superstore.groupby("Sub-Category")["Profit"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== PROFIT BY SUB-CATEGORY =====")
print(profit_by_subcategory.to_string())


top_products = (
    superstore.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== TOP 10 PRODUCTS BY SALES =====")
print(top_products.to_string())

worst_products = (
    superstore.groupby("Product Name")["Profit"]
    .sum()
    .sort_values()
    .head(10)
)

print("\n===== TOP 10 LOSS MAKING PRODUCTS =====")
print(worst_products.to_string())

complaints_by_department = complaints["Department"].value_counts()

print("\n===== COMPLAINTS BY DEPARTMENT =====")
print(complaints_by_department.to_string())

complaints_by_store = complaints["Store Location"].value_counts()

print("\n===== COMPLAINTS BY STORE LOCATION =====")
print(complaints_by_store.to_string())

complaints_by_type = complaints["Complaint Type"].value_counts()

print("\n===== COMPLAINTS BY TYPE =====")
print(complaints_by_type.to_string())

most_common_complaint = complaints["Complaint Type"].mode()[0]

print("\nMost Common Complaint Type:", most_common_complaint)

unique_customers = superstore["Customer ID"].nunique()

average_order_value = (
    superstore["Sales"].sum()
    / superstore["Order ID"].nunique()
)

revenue_per_customer = (
    superstore["Sales"].sum()
    / unique_customers
)

average_profit_per_order = (
    superstore["Profit"].sum()
    / superstore["Order ID"].nunique()
)

print("\n===== CUSTOMER KPIs =====")
print(f"Unique Customers: {unique_customers}")
print(f"Average Order Value: ${average_order_value:.2f}")
print(f"Revenue Per Customer: ${revenue_per_customer:.2f}")
print(f"Average Profit Per Order: ${average_profit_per_order:.2f}")


unique_products = superstore["Product ID"].nunique()

best_selling_product = (
    superstore.groupby("Product Name")["Sales"]
    .sum()
    .idxmax()
)

most_profitable_product = (
    superstore.groupby("Product Name")["Profit"]
    .sum()
    .idxmax()
)

average_revenue_per_product = (
    superstore["Sales"].sum()
    / unique_products
)

print("\n===== PRODUCT KPIs =====")
print(f"Unique Products: {unique_products}")
print(f"Best Selling Product: {best_selling_product}")
print(f"Most Profitable Product: {most_profitable_product}")
print(f"Average Revenue Per Product: ${average_revenue_per_product:.2f}")

loss_making_orders = (
    superstore["Profit"] < 0
).sum()

loss_order_percentage = (
    loss_making_orders
    / len(superstore)
) * 100

highest_discount = (superstore["Discount"].max())

average_discount = (superstore["Discount"].mean())

print("\n===== RISK ALERT KPIs =====")
print(f"Loss Making Orders: {loss_making_orders}")
print(f"Loss Order Percentage: {loss_order_percentage:.2f}%")
print(f"Highest Discount Offered: {highest_discount:.2f}")
print(f"Average Discount Offered: {average_discount:.2f}")


first_order_date = (superstore["Order Date"].min())

latest_order_date = (superstore["Order Date"].max())

business_duration = (latest_order_date - first_order_date).days

print("\n===== FORECASTING KPIs =====")
print(f"First Order Date: {first_order_date.date()}")
print(f"Latest Order Date: {latest_order_date.date()}")
print(f"Business Duration: {business_duration} days")

monthly_revenue = (
    superstore.groupby(
        superstore["Order Date"].dt.to_period("M")
    )["Sales"]
    .sum()
)

print("\n===== MONTHLY REVENUE =====")
print(monthly_revenue.to_string())

monthly_profit = (
    superstore.groupby(
        superstore["Order Date"].dt.to_period("M")
    )["Profit"]
    .sum()
)

print("\n===== MONTHLY PROFIT =====")
print(monthly_profit.to_string())

monthly_orders = (
    superstore.groupby(
        superstore["Order Date"].dt.to_period("M")
    )["Order ID"]
    .nunique()
)

print("\n===== MONTHLY ORDERS =====")
print(monthly_orders.to_string())

average_discount_by_category = (superstore.groupby("Category")["Discount"].mean())

average_discount_by_subcategory = (
    superstore.groupby("Sub-Category")["Discount"]
    .mean()
    .sort_values(ascending=False)
)

average_shipping_time = (
    (superstore["Ship Date"] - superstore["Order Date"])
    .dt.days
    .mean()
)

shipping_time_distribution = (
    (superstore["Ship Date"] - superstore["Order Date"])
    .dt.days
    .value_counts()
    .sort_index()
)

orders_by_ship_mode = (superstore["Ship Mode"].value_counts())

revenue_by_ship_mode = (superstore.groupby("Ship Mode")["Sales"].sum())

profit_by_ship_mode = (superstore.groupby("Ship Mode")["Profit"].sum())

print("\n===== LOGISTICS AND DISCOUNT KPIs =====")

print("\nAverage Discount by Category")
print(average_discount_by_category.to_string())

print("\nAverage Discount by Sub-Category")
print(average_discount_by_subcategory.to_string())

print(f"\nAverage Shipping Time: {average_shipping_time:.2f} days")

print("\nShipping Time Distribution")
print(shipping_time_distribution.to_string())

print("\nOrders by Ship Mode")
print(orders_by_ship_mode.to_string())

print("\nRevenue by Ship Mode")
print(revenue_by_ship_mode.to_string())

print("\nProfit by Ship Mode")
print(profit_by_ship_mode.to_string())
