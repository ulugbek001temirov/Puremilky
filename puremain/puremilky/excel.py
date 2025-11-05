# import pandas as pd
# import sqlite3

# conn = sqlite3.connect("bot.db")

# tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]

# with pd.ExcelWriter("output.xlsx") as writer:
#     for t in tables:
#         try:
#             df = pd.read_sql(f"SELECT * FROM {t}", conn)
#             if not df.empty:
#                 df.to_excel(writer, sheet_name=t, index=False)
#                 print(f"✅ Exported table: {t}")
#             else:
#                 print(f"⚠️ Table '{t}' is empty, skipped.")
#         except Exception as e:
#             print(f"❌ Error reading table '{t}': {e}")

# conn.close()
import pandas as pd
import sqlite3

conn = sqlite3.connect("bot.db")
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]

with pd.ExcelWriter("output.xlsx") as writer:
    for t in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {t}", conn)
            if not df.empty:
                df.to_excel(writer, sheet_name=t, index=False)
                print(f"Exported table: {t}")
            else:
                print(f"Table '{t}' is empty, skipped.")
        except Exception as e:
            print(f"Error reading table '{t}': {e}")

conn.close()
