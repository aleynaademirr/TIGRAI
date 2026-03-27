import requests
import time
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
TVMAZE_BASE_URL = "http://api.tvmaze.com"
def search_series_tvmaze(title: str, retry_count: int = 3) -> str:
    for attempt in range(retry_count):
        try:
            url = f"{TVMAZE_BASE_URL}/search/shows"
            params = {"q": title}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    show_data = results[0].get("show", {})
                    image_data = show_data.get("image", {})
                    poster_url = None
                    if image_data:
                        poster_url = image_data.get("original") or image_data.get("medium")
                    if poster_url:
                        return poster_url
                return None  
            elif response.status_code == 429:  
                wait_time = 2 ** attempt  
                print(f"  [RATE LIMIT] {wait_time}s bekleniyor...")
                time.sleep(wait_time)
                continue
            else:
                return None
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                time.sleep(1)
            else:
                return None
        except Exception as e:
            return None
    return None
def update_series_posters_tvmaze():
    print("=" * 60)
    print("DİZİ POSTERLERİ GÜNCELLENİYOR (TVMaze API)")
    print("API KEY GEREKTİRMEZ - TAMAMEN ÜCRETSİZ!")
    print("=" * 60)
    db = SessionLocal()
    series = db.query(Icerik).filter(
        Icerik.tur == 'Dizi',
        (Icerik.poster_url == None) | 
        (Icerik.poster_url.like('%placehold%')) |
        (Icerik.poster_url == '')
    ).all()
    print(f"\n📺 Güncellenecek {len(series)} dizi bulundu")
    print("⏱️  Bu işlem 10-15 dakika sürebilir (rate limit nedeniyle)\n")
    updated_count = 0
    not_found_count = 0
    error_count = 0
    for idx, show in enumerate(series):
        try:
            progress = ((idx + 1) / len(series)) * 100
            print(f"[{progress:.1f}%] {show.baslik[:40]}...", end=" ")
            poster_url = search_series_tvmaze(show.baslik)
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
            if (idx + 1) % 10 == 0:
                time.sleep(1)  
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
    print("\n🎉 TVMaze API - HİÇ API KEY GEREKTİRMEZ!")
    print("Hemen başlıyoruz...\n")
    time.sleep(2)
    update_series_posters_tvmaze()