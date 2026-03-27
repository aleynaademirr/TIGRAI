import requests
import time
def check_data_quality():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    print("=== POPÜLER İÇERİK KONTROLÜ ===")
    popular_tests = [
        , "The Dark Knight", "Interstellar", "Breaking Bad", 
        , "Friends", "The Matrix"
    ]
    print("\n--- Puan Kontrolü ---")
    for title in popular_tests:
        cursor.execute("SELECT baslik, tur, imdb_puani, poster_url FROM icerikler WHERE baslik LIKE ?", (f"%{title}%",))
        results = cursor.fetchall()
        for row in results:
            print(f"Baslik: {row[0]}")
            print(f"Tur: {row[1]}")
            print(f"Puan: {row[2]} (Beklenen: ~8.0-9.5)")
            print(f"Poster: {row[3][:50]}...")
            print("-" * 30)
    print("\n=== POSTER URL ERİŞİM TESTİ (Rastgele 5) ===")
    cursor.execute("SELECT baslik, poster_url FROM icerikler WHERE poster_url IS NOT NULL AND poster_url != '' ORDER BY RANDOM() LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        baslik, url = row
        print(f"\nKontrol ediliyor: {baslik}")
        print(f"URL: {url}")
        try:
            response = requests.head(url, timeout=3)
            print(f"Durum Kodu: {response.status_code}")
            if response.status_code == 200:
                print("✅ Erişilebilir")
            else:
                print("❌ Erişilemez")
        except Exception as e:
            print(f"❌ Hata: {e}")
    conn.close()
if __name__ == "__main__":
    check_data_quality()