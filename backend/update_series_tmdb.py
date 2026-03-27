import requests
import time
import os
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
from dotenv import load_dotenv
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
def search_tv_show(title: str, retry_count: int = 3) -> str:
    if not TMDB_API_KEY:
        print("❌ TMDB_API_KEY bulunamadı! .env dosyasına ekleyin.")
        return None
    for attempt in range(retry_count):
        try:
            url = f"{TMDB_BASE_URL}/search/tv"
            params = {
                : TMDB_API_KEY,
                : title,
                : "tr-TR"  
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    first_result = data["results"][0]
                    poster_path = first_result.get("poster_path")
                    if poster_path:
                        return f"{TMDB_IMAGE_BASE}{poster_path}"
                return None  
            elif response.status_code == 429:  
                wait_time = 2 ** attempt  
                print(f"  [RATE LIMIT] {wait_time}s bekleniyor...")
                time.sleep(wait_time)
                continue
            else:
                print(f"  [ERR] HTTP {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                print(f"  [TIMEOUT] Tekrar deneniyor ({attempt + 1}/{retry_count})...")
                time.sleep(1)
            else:
                return None
        except Exception as e:
            print(f"  [ERR] {title}: {e}")
            return None
    return None
def update_series_posters():
    print("=" * 60)
    print("DİZİ POSTERLERİ GÜNCELLENİYOR (TMDB API)")
    print("=" * 60)
    if not TMDB_API_KEY:
        print("\n❌ TMDB API KEY GEREKLİ!")
        print("\n📝 Nasıl Alınır:")
        print("1. https://www.themoviedb.org/ adresine git")
        print("2. Ücretsiz hesap aç (5 dakika)")
        print("3. Settings > API > Request API Key")
        print("4. .env dosyasına ekle: TMDB_API_KEY=your_key_here")
        print("\n⏸️  Script durduruluyor...")
        return 0
    print(f"\n✅ TMDB API Key bulundu")
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
            poster_url = search_tv_show(show.baslik)
            if poster_url:
                show.poster_url = poster_url
                updated_count += 1
                print("✅")
            else:
                not_found_count += 1
                print("❌ Bulunamadı")
            if (idx + 1) % 50 == 0:
                db.commit()
                print(f"\n💾 {updated_count} dizi kaydedildi...\n")
            if (idx + 1) % 10 == 0:
                time.sleep(0.3)
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
    update_series_posters()