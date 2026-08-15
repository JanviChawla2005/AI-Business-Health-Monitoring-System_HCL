import ollama
import io
from contextlib import redirect_stdout

with redirect_stdout(io.StringIO()):
    from kpi_generator import (
        total_revenue,
        total_profit,
        total_orders,
        profit_margin
    )

    import business_analysis as analysis
    
business_data = f"""
BUSINESS HEALTH KPIs

Total Revenue: ${total_revenue:,.2f}
Total Profit: ${total_profit:,.2f}
Total Orders: {total_orders}
Profit Margin: {profit_margin:.2f}%

CUSTOMER KPIs

Unique Customers: {analysis.unique_customers}
Average Order Value: ${analysis.average_order_value:,.2f}
Revenue Per Customer: ${analysis.revenue_per_customer:,.2f}
Average Profit Per Order: ${analysis.average_profit_per_order:,.2f}

PRODUCT KPIs

Unique Products: {analysis.unique_products}
Best Selling Product: {analysis.best_selling_product}
Most Profitable Product: {analysis.most_profitable_product}
Average Revenue Per Product: ${analysis.average_revenue_per_product:,.2f}

PROFITABILITY AND RISK KPIs

Loss-Making Orders: {analysis.loss_making_orders}
Loss-Making Order Percentage: {analysis.loss_order_percentage:.2f}%
Highest Discount: {analysis.highest_discount * 100:.2f}%
Average Discount: {analysis.average_discount * 100:.2f}%

REGIONAL PERFORMANCE

Revenue by Region:
{analysis.revenue_by_region.to_string()}

Profit by Region:
{analysis.profit_by_region.to_string()}

SEGMENT PERFORMANCE

Revenue by Segment:
{analysis.revenue_by_segment.to_string()}

Profit by Segment:
{analysis.profit_by_segment.to_string()}

CATEGORY PERFORMANCE

Sales by Category:
{analysis.sales_by_category.to_string()}

Profit by Category:
{analysis.profit_by_category.to_string()}

SUB-CATEGORY PERFORMANCE

Sales by Sub-Category:
{analysis.sales_by_subcategory.to_string()}

Profit by Sub-Category:
{analysis.profit_by_subcategory.to_string()}

TOP 10 PRODUCTS BY SALES

{analysis.top_products.to_string()}

TOP 10 LOSS-MAKING PRODUCTS

{analysis.worst_products.to_string()}

LOGISTICS

Average Shipping Time: {analysis.average_shipping_time:.2f} days

Orders by Ship Mode:
{analysis.orders_by_ship_mode.to_string()}

Revenue by Ship Mode:
{analysis.revenue_by_ship_mode.to_string()}

Profit by Ship Mode:
{analysis.profit_by_ship_mode.to_string()}

BUSINESS TIME PERIOD

First Order Date: {analysis.first_order_date.date()}
Latest Order Date: {analysis.latest_order_date.date()}
Business Duration: {analysis.business_duration} days

MONTHLY REVENUE

{analysis.monthly_revenue.to_string()}

MONTHLY PROFIT

{analysis.monthly_profit.to_string()}

MONTHLY ORDERS

{analysis.monthly_orders.to_string()}
"""

prompt = f"""
You are an AI Business Health Advisor.

Analyze the verified business data below and create a professional
management-level Business Health Report.

{business_data}

STRICT RULES:

1. Use ONLY the data provided above.
2. Do not invent KPIs, statistics, benchmarks, trends, causes, or facts.
3. Do not include complaint KPIs or customer experience analysis.
4. Do not call total revenue "revenue growth".
5. Revenue growth has NOT been calculated, so do not discuss revenue growth.
6. Do not claim revenue increased or decreased unless the monthly data
   directly supports the statement.
7. Do not describe a KPI as high, low, strong, weak, significant, good,
   or poor unless the supplied data clearly supports the comparison.
8. Do not describe the average discount as high or low.
9. Report the average discount as a percentage.
10. Loss-Making Orders and Loss-Making Products are completely different.
11. Loss-Making Orders refers to the number of orders where total order
    profit is negative.
12. The Top 10 Loss-Making Products refers to the products listed in the
    supplied product analysis.
13. Never call Loss-Making Orders products.
14. Do not invent causes for poor performance.
15. Recommendations must be directly connected to the supplied data.
16. Do not use external business knowledge.
17. Use actual numbers when discussing important findings.
18. Do not create KPIs that were not supplied.
19. Do not mention a specific number of years unless directly calculated
    from the supplied dates.
20. Refer to the period as "the available data period" when necessary.
21. Do not repeat the same finding in multiple sections.
22. Keep the report concise and suitable for management.
23. Do not use Markdown symbols such as ** or ##.

Determine the overall business health using the supplied profitability
and risk KPIs.

Choose exactly ONE:

Healthy
Moderate
At Risk

Use the following structure EXACTLY:

AI BUSINESS HEALTH REPORT

BUSINESS HEALTH:
[Healthy / Moderate / At Risk]

EXECUTIVE SUMMARY:
Write one concise paragraph using the most important verified KPIs.

KEY STRENGTHS:
1. Use a measurable positive finding.
2. Use a second measurable positive finding.
3. Use a third measurable positive finding.

KEY CONCERNS:
1. Discuss the loss-making order percentage.
2. Discuss the discount/profitability situation.
3. Discuss another measurable concern from the supplied data.

BUSINESS RISKS:
1. Identify a risk directly related to loss-making orders.
2. Identify a risk directly related to profitability or discounts.
3. Identify one additional risk directly supported by the data.

RECOMMENDATIONS:
1. Give an action addressing loss-making orders.
2. Give an action addressing profitability or discounts.
3. Give an action addressing regional or product performance.
4. Give one additional practical action based directly on the data.

MANAGEMENT PRIORITY:
Identify ONE issue management should address first.
Support the priority with the relevant KPI and explain why it deserves
attention.

Do not add any sections.
Do not invent any information.
"""

print("\n" + "=" * 60)
print("STARTING AI BUSINESS HEALTH ANALYSIS")
print("=" * 60)

print("\nSending verified business data to Llama 3.1 8B...\n")

response = ollama.chat(
    model="llama3.1:8b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    options={
        "temperature": 0.1
    }
)

report = response["message"]["content"].strip()

report = report.replace("**", "")
report = report.replace("##", "")

print("\n" + "=" * 60)
print("AI BUSINESS HEALTH REPORT")
print("=" * 60)

print(report)

output_file = "AI_Business_Health_Report.txt"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(report)

print("\n" + "=" * 60)
print("REPORT SAVED")
print("=" * 60)
print(output_file)