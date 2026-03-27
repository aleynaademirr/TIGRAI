import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
def repair_data():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    print("=== VERİ ONARIMI BAŞLIYOR ===")
    print("\n1. IMDB Puanları 0-10 skalasına getiriliyor...")
    cursor.execute()
    print(f"   📚 {cursor.rowcount} kitap puanı güncellendi.")
    cursor.execute()
    print(f"   🎬 {cursor.rowcount} film/dizi puanı güncellendi.")
    conn.commit()
    if not OMDB_API_KEY:
        print("\n❌ OMDb API Key bulunamadı! Poster güncellemesi geçiliyor.")
        return
    print(f"\n2. Popüler içeriklerin posterleri OMDb ({OMDB_API_KEY}) ile yenileniyor...")
    cursor.execute()
    items = cursor.fetchall()
    updated_count = 0
    for item in items:
        id, baslik, tur, yil = item
        try:
            url = f"http://www.omdbapi.com/?t={baslik}&apikey={OMDB_API_KEY}"
            if yil:
                url += f"&y={yil}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('Response') == 'True' and data.get('Poster') and data.get('Poster') != 'N/A':
                new_poster = data['Poster']
                new_rating = data.get('imdbRating')
                if new_rating and new_rating != 'N/A':
                    cursor.execute(, (new_poster, float(new_rating), id))
                else:
                     cursor.execute("UPDATE icerikler SET poster_url = ? WHERE id = ?", (new_poster, id))
                print(f"   ✅ Güncellendi: {baslik}")
                updated_count += 1
            else:
                print(f"   ⚠️  Bulunamadı: {baslik}")
        except Exception as e:
            print(f"   ❌ Hata ({baslik}): {e}")
    conn.commit()
    conn.close()
    print(f"\n✨ İşlem Tamamlandı! {updated_count} poster yenilendi.")
if __name__ == "__main__":
    repair_data()