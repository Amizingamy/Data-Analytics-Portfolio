"""Regenerate RESULTS.md: runs every query in queries.sql and writes the SQL plus its output."""
import pandas as pd
import run_sql as r

conn = r.load_database()
out = ["# SQL results\n", "Output of every query in `queries.sql`, run on the simulated Brew Room data (SQLite). Regenerate with `python3 make_results.py`.\n"]
for n, (t, sql) in r.split_queries((r.HERE / "queries.sql").read_text()).items():
    df = pd.read_sql_query(sql, conn)
    out.append(f"## Q{n}: {t}\n\n```sql\n{sql}\n```\n\n```\n{df.to_string(index=False)}\n```\n")
(r.HERE / "RESULTS.md").write_text("\n".join(out))
