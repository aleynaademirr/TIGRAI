import requests
import time
import os
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
from dotenv import load_dotenv
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
OMDB_BASE_URL = "http://www.omdbapi.com/"
def search_series_omdb(title: str, retry_count: int = 2) -> str:
    if not OMDB_API_KEY:
        print("❌ OMDB_API_KEY bulunamadı! .env dosyasına ekleyin.")
        return None
    for attempt in range(retry_count):
        try:
            params = {
                'apikey': OMDB_API_KEY,
                't': title,  
                'type': "series"  
            }
            response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    poster = data.get("Poster")
                    if poster and poster != "N/A":
                        return poster
                return None  
            else:
                print(f"  [ERR] HTTP {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                print(f"  [TIMEOUT] Tekrar deneniyor...")
                time.sleep(1)
            else:
                return None
        except Exception as e:
            print(f"  [ERR] {title}: {e}")
            return None
    return None
def update_series_posters_omdb():
    print("=" * 60)
    print("DİZİ POSTERLERİ GÜNCELLENİYOR (OMDb API)")
    print("=" * 60)
    if not OMDB_API_KEY:
        print("\n❌ OMDb API KEY GEREKLİ!")
        print("\n📝 Nasıl Alınır (ÇOK KOLAY - 2 dakika):")
        print("1. http://www.omdbapi.com/apikey.aspx adresine git")
        print("2. Email adresini gir (kayıt yok!)")
        print("3. Email'ine gelen linke tıkla")
        print("4. API key'i kopyala")
        print("5. .env dosyasına ekle: OMDB_API_KEY=your_key")
        print("\n⏸️  Script durduruluyor...")
        return 0
    print(f"\n✅ OMDb API Key bulundu")
    db = SessionLocal()
    series = db.query(Icerik).filter(
        Icerik.tur == 'Dizi',
        (Icerik.poster_url == None) | 
        (Icerik.poster_url.like('%placehold%')) |
        (Icerik.poster_url == '')
    ).all()
    print(f"📺 Güncellenecek {len(series)} dizi bulundu\n")
    updated_count = 0
    not_found_count = 0
    error_count = 0
    for idx, show in enumerate(series):
        try:
            progress = ((idx + 1) / len(series)) * 100
            print(f"[{progress:.1f}%] {show.baslik[:40]}...", end=" ")
            poster_url = search_series_omdb(show.baslik)
            if poster_url:
                show.poster_url = poster_url
                updated_count += 1
                print("✅")
            else:
                not_found_count += 1
                print("❌")
            if (idx + 1) % 50 == 0:
                db.commit()
                print(f"\n💾 {updated_count} dizi kaydedildi...\n")
            time.sleep(0.1)  
        except Exception as e:
            error_count += 1
            print(f"❌ HATA: {e}")
    db.commit()
    db.close()
    print("\n" + "=" * 60)
    print("✅ GÜNCELLEME TAMAMLANDI!")
    print("=" * 60)
    print(f"   Güncellenen: {updated_count}")
    print(f"   Bulunamayan: {not_found_count}")
    print(f"   Hatalar: {error_count}")
    print(f"   Başarı Oranı: {(updated_count / len(series) * 100):.1f}%")
    return updated_count
if __name__ == "__main__":
    update_series_posters_omdb()