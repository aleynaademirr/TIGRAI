import os
DB_NAME = "recommendation_system.db"
OUTPUT_FILE = "database_setup.sql"
def dump_schema():
    if not os.path.exists(DB_NAME):
        print(f"Error: {DB_NAME} not found.")
        return
    print(f"Dumping schema from {DB_NAME}...")
    try:
        conn = sqlite3.connect(DB_NAME)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("/* TIGRAI Database Schema Dump */\n")
            f.write("/* Generated automatically */\n\n")
            f.write("PRAGMA foreign_keys=OFF;\n")
            f.write("BEGIN TRANSACTION;\n\n")
            cursor = conn.cursor()
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()
            for table_name, create_sql in tables:
                if create_sql:
                    f.write(f"/* Table: {table_name} */\n")
                    f.write(f"DROP TABLE IF EXISTS {table_name};\n")
                    f.write(f"{create_sql};\n\n")
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type IN ('index', 'trigger') AND name NOT LIKE 'sqlite_%';")
            others = cursor.fetchall()
            for name, sql in others:
                if sql:
                    f.write(f"/* {name} */\n")
                    f.write(f"{sql};\n\n")
            f.write("COMMIT;\n")
        print(f"Schema dumped to {OUTPUT_FILE} successfully.")
    except Exception as e:
        print(f"Error dumping schema: {e}")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    dump_schema()