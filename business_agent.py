import os
import re
import sqlite3
from groq import Groq

DB_PATH = "business_warehouse.db"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.3-70b-versatile"


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_schema():
    conn = get_connection()
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    schema = {}

    for table in tables:
        table_name = table[0]

        columns = cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        schema[table_name] = [column[1] for column in columns]

    conn.close()

    return schema


def format_schema(schema):
    text = ""

    for table, columns in schema.items():
        text += f"Table: {table}\n"
        text += "Columns: " + ", ".join(columns) + "\n\n"

    return text


def generate_sql(question, schema):
    schema_text = format_schema(schema)

    prompt = f"""
You are an expert SQLite SQL generator for a business analytics system.

Database schema:

{schema_text}

User question:
{question}

Generate ONE valid SQLite SELECT query that answers the user's question.

Rules:

1. Return ONLY SQL. Do not return explanations.
2. Use only tables and columns that exist in the schema.
3. Use double quotes around column names.
4. Use SQLite syntax.
5. Never modify, delete, insert, update, or drop data.
6. For total revenue, use SUM("Sales").
7. For total profit, use SUM("Profit").
8. For complaint questions, use the complaints table.
9. For complaint counts by department, use COUNT(*) grouped by "Department".
10. For loss-making orders, use "Profit" < 0.
11. For loss-making order percentage, calculate the percentage of rows where "Profit" < 0.
12. When finding highest, lowest, most, least, best, or worst values, DO NOT use LIMIT 1 if multiple records could have the same value.
13. Return all records needed to identify ties.
14. Only use LIMIT when the user explicitly asks for a specific number such as top 5 or top 10.
15. If the question asks for a ranking such as highest revenue region, return all regions and their values so ties can be detected.
16. Never assume that a single result means there cannot be a tie.

SQL:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You generate accurate SQLite SELECT queries only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    sql = sql.strip()

    return sql


def validate_sql(sql):
    sql_clean = sql.strip().lower()

    if not (
        sql_clean.startswith("select")
        or sql_clean.startswith("with")
    ):
        raise ValueError("Only SELECT queries are allowed.")

    forbidden = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "attach ",
        "detach ",
        "pragma "
    ]

    for word in forbidden:
        if word in sql_clean:
            raise ValueError("Unsafe SQL detected.")

    return True


def execute_sql(sql):
    validate_sql(sql)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    conn.close()

    return columns, rows


def format_database_result(columns, rows):
    if not rows:
        return "No results found."

    result = []

    for row in rows:
        values = []

        for column, value in zip(columns, row):
            values.append(f"{column}: {value}")

        result.append(" | ".join(values))

    return "\n".join(result)


def generate_answer(question, sql, columns, rows):
    database_result = format_database_result(columns, rows)

    prompt = f"""
You are an AI Business Advisor.

Answer the user's business question using ONLY the database result provided below.

User question:
{question}

SQL used:
{sql}

Database result:
{database_result}

Rules:

1. Give a clear and concise business answer.
2. Do not invent numbers or facts.
3. Use the exact values from the database result.
4. If multiple records share the highest value, mention ALL of them.
5. If multiple records share the lowest value, mention ALL of them.
6. Explicitly say that there is a tie when applicable.
7. Never arbitrarily choose one record when there is a tie.
8. For complaint questions, mention the department, complaint type, store, or category and the count when available.
9. For revenue and profit questions, clearly state the amount.
10. For percentages, clearly state the percentage.
11. Keep the answer to 2-4 sentences.
12. Do not mention SQL, database queries, prompts, or technical implementation unless the user asks.
13. Do not claim that a department or region requires attention unless the data reasonably supports that observation.

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a precise business intelligence advisor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


def print_result(sql, columns, rows, answer):
    print("\nSQL Query:")
    print(sql)

    print("\nDatabase Result:")
    if rows:
        for row in rows:
            values = []

            for column, value in zip(columns, row):
                values.append(f"{column}: {value}")

            print(" | ".join(values))
    else:
        print("No results found.")

    print("\nAI Business Advisor:")
    print(answer)

    print("\n" + "-" * 70)


def process_question(question, schema):
    print("\nGenerating SQL...")

    try:
        sql = generate_sql(question, schema)

        print("\nSQL Query:")
        print(sql)

        columns, rows = execute_sql(sql)

        print("\nDatabase Result:")
        if rows:
            for row in rows:
                values = []

                for column, value in zip(columns, row):
                    values.append(f"{column}: {value}")

                print(" | ".join(values))
        else:
            print("No results found.")

        print("\nGenerating answer...")

        answer = generate_answer(
            question,
            sql,
            columns,
            rows
        )

        print("\nAI Business Advisor:")
        print(answer)

        print("\n" + "-" * 70)

    except Exception as e:
        print("\nError:")
        print(e)
        print("\n" + "-" * 70)


def main():
    print("=" * 70)
    print("AI BUSINESS ADVISOR AGENT")
    print("=" * 70)

    if not os.getenv("GROQ_API_KEY"):
        print("\nGROQ_API_KEY is not set.")
        print("Run this command in the terminal:")
        print('export GROQ_API_KEY="your_api_key_here"')
        return

    if not os.path.exists(DB_PATH):
        print(f"\nDatabase not found: {DB_PATH}")
        return

    schema = get_schema()

    print("\nAgent connected to business_warehouse.db")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            print("\nAgent stopped.")
            break

        if not question:
            continue

        process_question(question, schema)


if __name__ == "__main__":
    main()