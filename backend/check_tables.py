conn = sqlite3.connect('recommendation_system.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("=== TABLOLAR ===")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    print(f"    Sütunlar: {', '.join([col[1] for col in columns])}")
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"    Kayıt sayısı: {count}")
    except:
        print(f"    Kayıt sayısı: (hata)")
print("\n=== ÖRNEK VERİLER ===")
cursor.execute("SELECT tur, COUNT(*) FROM icerikler GROUP BY tur;")
icerik_stats = cursor.fetchall()
print("İçerik türleri:")
for tur, count in icerik_stats:
    print(f"  {tur}: {count}")
conn.close()