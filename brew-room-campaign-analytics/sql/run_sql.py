"""
Load the Brew Room CSVs into SQLite and run every query in queries.sql.

Usage:
    python3 run_sql.py              # run all queries and print the results
    python3 run_sql.py 3            # run only Q3
    python3 run_sql.py --save-db    # also write brew_room.db (open it in DB Browser for SQLite)

Works the same in Google Colab: upload the data folder and this folder, then run it.
"""

import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data"

TABLES = {
    "daily_sales": "daily_sales.csv",
    "loyalty_members": "loyalty_members.csv",
    "instagram_engagement": "instagram_engagement.csv",
}


def load_database(path=":memory:"):
    conn = sqlite3.connect(path)
    for table, filename in TABLES.items():
        pd.read_csv(DATA / filename).to_sql(table, conn, if_exists="replace", index=False)
    return conn


def split_queries(text):
    """Split queries.sql into {number: (title, sql)} using the '-- Q<n>:' headers."""
    parts = re.split(r"^-- Q(\d+): (.*)$", text, flags=re.MULTILINE)
    queries = {}
    for i in range(1, len(parts), 3):
        number, title, body = int(parts[i]), parts[i + 1], parts[i + 2]
        sql = "\n".join(line for line in body.splitlines() if not line.startswith("-- ")).strip()
        queries[number] = (title, sql)
    return queries


def main():
    args = sys.argv[1:]
    save_db = "--save-db" in args
    wanted = {int(a) for a in args if a.isdigit()}

    conn = load_database(str(HERE / "brew_room.db") if save_db else ":memory:")
    queries = split_queries((HERE / "queries.sql").read_text())

    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 20)
    for number, (title, sql) in queries.items():
        if wanted and number not in wanted:
            continue
        print(f"\nQ{number}: {title}")
        print(pd.read_sql_query(sql, conn).to_string(index=False))


if __name__ == "__main__":
    main()
