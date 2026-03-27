import hashlib
import secrets
import datetime
import re
OUTPUT_FILE = "database_setup.sql"
DB_NAME = "recommendation_system.db"
HEADER = 
def get_schema(conn):
    cursor = conn.cursor()
    schema_sql = []
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    for table_name, create_sql in tables:
        if create_sql:
            clean_sql = re.sub(r'/\*.*?\*/', '', create_sql, flags=re.DOTALL)
            clean_sql = re.sub(r'--.*', '', clean_sql)
            schema_sql.append(f"DROP TABLE IF EXISTS {table_name};")
            schema_sql.append(f"{clean_sql.strip()};")
            schema_sql.append("")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type IN ('index', 'trigger') AND name NOT LIKE 'sqlite_%';")
    others = cursor.fetchall()
    for name, sql in others:
        if sql:
            clean_sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
            clean_sql = re.sub(r'--.*', '', clean_sql)
            schema_sql.append(f"{clean_sql.strip()};")
            schema_sql.append("")
    return "\n".join(schema_sql)
def escape_string(s):
    if s is None:
        return "NULL"
    if isinstance(s, (int, float)):
        return str(s)
    return "'" + str(s).replace("'", "''") + "'"
def get_data_dump(conn):
    cursor = conn.cursor()
    data_sql = []
    data_sql.append("-- SEED DATA: Users")
    cursor.execute("SELECT * FROM kullanicilar LIMIT 20")
    users = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    col_str = ", ".join(columns)
    for row in users:
        vals = [escape_string(x) for x in row]
        val_str = ", ".join(vals)
        data_sql.append(f"INSERT INTO kullanicilar ({col_str}) VALUES ({val_str});")
    data_sql.append("")
    data_sql.append("-- SEED DATA: Content (Films, Books, Series)")
    cursor.execute("SELECT * FROM icerikler ORDER BY imdb_puani DESC LIMIT 100")
    content = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    col_str = ", ".join(columns)
    for row in content:
        vals = [escape_string(x) for x in row]
        val_str = ", ".join(vals)
        data_sql.append(f"INSERT INTO icerikler ({col_str}) VALUES ({val_str});")
    data_sql.append("")
    data_sql.append("-- SEED DATA: Ratings")
    cursor.execute("SELECT * FROM puanlar ORDER BY id DESC LIMIT 200")
    ratings = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    col_str = ", ".join(columns)
    for row in ratings:
        vals = [escape_string(x) for x in row]
        val_str = ", ".join(vals)
        data_sql.append(f"INSERT INTO puanlar ({col_str}) VALUES ({val_str});")
    return "\n".join(data_sql)
def main():
    try:
        conn = sqlite3.connect(DB_NAME)
        schema = get_schema(conn)
        data = get_data_dump(conn)
        final_content = HEADER + "\n" + schema + "\n" + data + "\n\nCOMMIT;\nPRAGMA foreign_keys = ON;\n"
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Generated {OUTPUT_FILE} with Schema + Data.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()
if __name__ == "__main__":
    main()