import sqlite3
import time
import os
DB_PATH = "recommendation_system.db"
def run_benchmark():
    if not os.path.exists(DB_PATH):
        print(f"Hata: {DB_PATH} bulunamadı!")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"🔥 GERÇEK PERFORMANS TESTİ: {DB_PATH}")
    print("-" * 60)
    print(f"{'SENARYO':<30} | {'SÜRE (ms)':<10} | {'SATIR':<10}")
    print("-" * 60)
    start = time.time()
    cursor.execute("SELECT * FROM icerikler WHERE baslik LIKE '%Star Wars%'")
    rows = cursor.fetchall()
    end = time.time()
    search_time = (end - start) * 1000
    print(f"{'🔍 İçerik Arama (Star Wars)':<30} | {search_time:<10.2f} | {len(rows):<10}")
    start = time.time()
    cursor.execute()
    rows = cursor.fetchall()
    end = time.time()
    history_time = (end - start) * 1000
    print(f"{'👤 Kullanıcı Geçmişi (ID=1)':<30} | {history_time:<10.2f} | {len(rows):<10}")
    start = time.time()
    cursor.execute()
    rows = cursor.fetchall()
    end = time.time()
    stats_time = (end - start) * 1000
    print(f"{'📊 Kategori İstatistiği':<30} | {stats_time:<10.2f} | {len(rows):<10}")
    start = time.time()
    cursor.execute()
    rows = cursor.fetchall()
    end = time.time()
    trend_time = (end - start) * 1000
    print(f"{'📈 Trend Analizi (Complex)':<30} | {trend_time:<10.2f} | {len(rows):<10}")
    conn.close()
    print("-" * 60)
if __name__ == "__main__":
    run_benchmark()