import sqlite3
def tablolara_bak():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    print("=" * 60)
    print("VERİTABANI TABLOLARI")
    print("=" * 60)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table = table_name[0]
        print(f"\n[TABLO] {table}")
        print("-" * 60)
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        print("Sutunlar:")
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"  - {col_name} ({col_type})")
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"\nToplam kayit: {count}")
        if count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
            rows = cursor.fetchall()
            print("\nIlk 5 kayit ornegi:")
            for i, row in enumerate(rows, 1):
                print(f"  {i}. {row}")
    print("\n" + "=" * 60)
    print("\n[ICERIKLER TABLOSU ORNEKLERI]:")
    print("-" * 60)
    cursor.execute()
    icerikler = cursor.fetchall()
    for icerik in icerikler:
        print(f"ID: {icerik[0]} | {icerik[1]} ({icerik[2]}) | {icerik[3]} | {icerik[4]} | Puan: {icerik[5]}")
    conn.close()
if __name__ == "__main__":
    tablolara_bak()