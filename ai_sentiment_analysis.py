import pandas as pd
import ollama
import json
import re
import os
import time

# Load dataset

input_file = "datasets/StoreComplaints_Updated.csv"
output_file = "datasets/StoreComplaints_AI_Analyzed.csv"
checkpoint_file = "datasets/AI_Analysis_Checkpoint.csv"

df = pd.read_csv(input_file)

print("Complaint dataset loaded successfully.")
print("Total complaints:", len(df))

required_columns = [
    "Complaint Type",
    "Product Details",
    "Brief Complaint"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column '{column}' was not found."
        )

# Create unique complaint situations

unique_cases = (
    df[
        [
            "Complaint Type",
            "Product Details",
            "Brief Complaint"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
)

print(
    "Unique complaint situations:",
    len(unique_cases)
)

print(
    "AI analysis will be performed only once for each unique situation."
)

# Analyze one complaint situation

def analyze_complaint(
    complaint_type,
    product_details,
    complaint
):

    prompt = f"""
You are an AI-powered customer complaint analysis system.

Analyze the following customer complaint using ALL the information provided.

Complaint Type:
{complaint_type}

Product Details:
{product_details}

Customer Complaint:
"{complaint}"

Determine the following:

1. Sentiment
2. Sentiment score
3. Priority level
4. Whether escalation is required
5. Escalation queue
6. Brief reason

Return ONLY valid JSON with exactly these fields:

sentiment
sentiment_score
priority_level
escalated
escalation_queue
brief_reason

Sentiment:

Choose exactly one:

Positive
Neutral
Negative

Judge the sentiment from the customer's actual wording.

Sentiment score:

Return a number between -0.99 and 0.99.

The score represents the emotional intensity of the complaint.

Use:
- very severe dissatisfaction -> strongly negative
- serious dissatisfaction -> clearly negative
- moderate inconvenience -> moderately negative
- minor inconvenience -> mildly negative
- neutral wording -> near zero
- positive satisfaction -> positive

Do NOT use exactly -1 or 1.

Do NOT automatically use the same score for every complaint.

Different complaints should receive different scores when their emotional intensity differs.

Priority:

Choose exactly one:

High
Medium
Low

High priority should be used for:
- safety concerns
- serious staff misconduct
- severe service failure
- urgent unresolved problems
- repeated failure to resolve an issue
- major customer impact

Medium priority should be used for:
- meaningful product problems
- significant delays
- poor service
- problems requiring attention but not urgent intervention

Low priority should be used for:
- minor inconvenience
- small delays
- minor packaging issues
- issues where the customer can still use the product
- situations that can normally be resolved through routine support

Escalation:

Choose exactly:

Yes
No

Use Yes only when management or a specialized team should intervene.

Use No when normal customer service handling is sufficient.

Escalation queue:

Choose exactly one:

Customer Service
Logistics
Product Team
Manager/Supervisor
None

Use:

Staff misconduct -> Manager/Supervisor

Delivery problems -> Logistics

Product quality or defective products -> Product Team

General customer service problems -> Customer Service

If escalation is No, the queue MUST be None.

Brief reason:

Write one short professional sentence explaining the decision.

Do not invent information.

Return ONLY JSON.
"""


    try:

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0.4
            }
        )

        text = response["message"]["content"].strip()

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "No valid JSON found in response."
            )

        result = json.loads(
            match.group()
        )


        # Validate sentiment

        sentiment = str(
            result.get(
                "sentiment",
                "Negative"
            )
        ).strip().title()

        if sentiment not in [
            "Positive",
            "Neutral",
            "Negative"
        ]:
            sentiment = "Negative"


        # Validate score

        try:

            score = float(
                result.get(
                    "sentiment_score",
                    -0.5
                )
            )

        except:

            score = -0.5


        if score <= -1:
            score = -0.99

        if score >= 1:
            score = 0.99

        score = round(
            score,
            2
        )


        # Validate priority

        priority = str(
            result.get(
                "priority_level",
                "Medium"
            )
        ).strip().title()

        if priority not in [
            "High",
            "Medium",
            "Low"
        ]:

            priority = "Medium"


        # Validate escalation

        escalated = str(
            result.get(
                "escalated",
                "No"
            )
        ).strip().title()

        if escalated not in [
            "Yes",
            "No"
        ]:

            escalated = "No"


        # Validate escalation queue

        queue = str(
            result.get(
                "escalation_queue",
                "None"
            )
        ).strip()

        allowed_queues = [
            "Customer Service",
            "Logistics",
            "Product Team",
            "Manager/Supervisor",
            "None"
        ]

        if queue not in allowed_queues:
            queue = "None"

        if escalated == "No":
            queue = "None"


        # Validate reason

        reason = str(
            result.get(
                "brief_reason",
                "Complaint analyzed based on severity and customer impact."
            )
        ).strip()


        return {
            "AI Sentiment": sentiment,
            "AI Sentiment Score": score,
            "AI Priority Level": priority,
            "AI Escalated": escalated,
            "AI Escalation Queue": queue,
            "AI Brief Reason": reason
        }


    except Exception as e:

        print(
            "Error:",
            e
        )

        return {
            "AI Sentiment": "Negative",
            "AI Sentiment Score": -0.50,
            "AI Priority Level": "Medium",
            "AI Escalated": "No",
            "AI Escalation Queue": "None",
            "AI Brief Reason": "Complaint requires review based on the reported issue."
        }

# Load previous checkpoint if available

if os.path.exists(
    checkpoint_file
):

    checkpoint = pd.read_csv(
        checkpoint_file
    )

    print(
        "\nPrevious checkpoint found."
    )

    print(
        "Completed cases:",
        len(checkpoint),
        "/",
        len(unique_cases)
    )

else:

    checkpoint = pd.DataFrame()

    print(
        "\nNo previous checkpoint found."
    )


# Start analysis

results = []

start_index = len(
    checkpoint
)

if start_index > 0:

    results = checkpoint[
        [
            "AI Sentiment",
            "AI Sentiment Score",
            "AI Priority Level",
            "AI Escalated",
            "AI Escalation Queue",
            "AI Brief Reason"
        ]
    ].to_dict(
        "records"
    )

print()
print("=" * 60)
print("STARTING AI ANALYSIS")
print("=" * 60)

print(
    f"Cases to analyze: {len(unique_cases) - start_index}"
)

print()

# Analyze unique cases

for index in range(
    start_index,
    len(unique_cases)
):

    row = unique_cases.iloc[index]

    print(
        f"Analyzing case {index + 1}/{len(unique_cases)}..."
    )

    result = analyze_complaint(
        row["Complaint Type"],
        row["Product Details"],
        row["Brief Complaint"]
    )

    results.append(
        result
    )


    # Save checkpoint after every case

    checkpoint_data = unique_cases.iloc[
        :len(results)
    ].copy()

    result_df = pd.DataFrame(
        results
    )

    checkpoint_data = pd.concat(
        [
            checkpoint_data.reset_index(drop=True),
            result_df.reset_index(drop=True)
        ],
        axis=1
    )

    checkpoint_data.to_csv(
        checkpoint_file,
        index=False
    )

    print(
        f"Checkpoint saved: {len(results)}/{len(unique_cases)}"
    )

    print()

# Create AI result dataframe

ai_results = pd.DataFrame(
    results
)

# Merge AI results back into all 300 rows

df = df.merge(
    unique_cases,
    on=[
        "Complaint Type",
        "Product Details",
        "Brief Complaint"
    ],
    how="left",
    suffixes=(
        "",
        "_duplicate"
    )
)

# Remove duplicate columns

duplicate_columns = [
    column
    for column in df.columns
    if column.endswith(
        "_duplicate"
    )
]

if duplicate_columns:

    df = df.drop(
        columns=duplicate_columns
    )

# Add AI results

df[
    "AI Sentiment"
] = df.merge(
    unique_cases.assign(
        **{
            "AI Sentiment":
            ai_results["AI Sentiment"],
            "AI Sentiment Score":
            ai_results["AI Sentiment Score"],
            "AI Priority Level":
            ai_results["AI Priority Level"],
            "AI Escalated":
            ai_results["AI Escalated"],
            "AI Escalation Queue":
            ai_results["AI Escalation Queue"],
            "AI Brief Reason":
            ai_results["AI Brief Reason"]
        }
    ),
    on=[
        "Complaint Type",
        "Product Details",
        "Brief Complaint"
    ],
    how="left"
)[
    "AI Sentiment"
]

# Easier and safer mapping

case_keys = (
    unique_cases[
        [
            "Complaint Type",
            "Product Details",
            "Brief Complaint"
        ]
    ]
    .astype(str)
    .agg(
        "||".join,
        axis=1
    )
)

ai_results["Case Key"] = case_keys.values

df["Case Key"] = (
    df[
        [
            "Complaint Type",
            "Product Details",
            "Brief Complaint"
        ]
    ]
    .astype(str)
    .agg(
        "||".join,
        axis=1
    )
)

ai_lookup = ai_results.set_index(
    "Case Key"
)


df[
    "AI Sentiment"
] = df["Case Key"].map(
    ai_lookup["AI Sentiment"]
)

df[
    "AI Sentiment Score"
] = df["Case Key"].map(
    ai_lookup["AI Sentiment Score"]
)

df[
    "AI Priority Level"
] = df["Case Key"].map(
    ai_lookup["AI Priority Level"]
)

df[
    "AI Escalated"
] = df["Case Key"].map(
    ai_lookup["AI Escalated"]
)

df[
    "AI Escalation Queue"
] = df["Case Key"].map(
    ai_lookup["AI Escalation Queue"]
)

df[
    "AI Brief Reason"
] = df["Case Key"].map(
    ai_lookup["AI Brief Reason"]
)


# Remove temporary key

df = df.drop(
    columns=[
        "Case Key"
    ]
)

# Sort by priority

priority_order = {
    "High": 1,
    "Medium": 2,
    "Low": 3
}

df[
    "Priority Order"
] = df[
    "AI Priority Level"
].map(
    priority_order
)

df = df.sort_values(
    by=[
        "Priority Order",
        "AI Sentiment Score"
    ],
    ascending=[
        True,
        True
    ]
)

df = df.drop(
    columns=[
        "Priority Order"
    ]
)

df = df.reset_index(
    drop=True
)

# Save final dataset

df.to_csv(
    output_file,
    index=False
)

# Final report

print()
print("=" * 60)
print("AI ANALYSIS COMPLETED")
print("=" * 60)

print(
    "\nTotal complaints:",
    len(df)
)

print(
    "Unique cases analyzed by AI:",
    len(unique_cases)
)

print(
    "\nPriority distribution:"
)

print(
    df[
        "AI Priority Level"
    ].value_counts()
)

print(
    "\nSentiment distribution:"
)

print(
    df[
        "AI Sentiment"
    ].value_counts()
)

print(
    "\nEscalation distribution:"
)

print(
    df[
        "AI Escalated"
    ].value_counts()
)

print(
    "\nEscalation queue distribution:"
)

print(
    df[
        "AI Escalation Queue"
    ].value_counts()
)

print(
    "\nAverage sentiment score:",
    round(
        df[
            "AI Sentiment Score"
        ].mean(),
        2
    )
)

print(
    "Minimum sentiment score:",
    df[
        "AI Sentiment Score"
    ].min()
)

print(
    "Maximum sentiment score:",
    df[
        "AI Sentiment Score"
    ].max()
)

print(
    "\nFinal dataset saved to:"
)

print(
    output_file
)

print()
print("=" * 60)
print("DONE")
print("=" * 60)