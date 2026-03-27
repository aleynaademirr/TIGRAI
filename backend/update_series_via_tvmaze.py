import time
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import urllib.parse
def update_series_covers():
    print("=== DİZİ POSTERLERİ TVMAZE API İLE GÜNCELLENİYOR ===")
    db = SessionLocal()
    series = db.query(Icerik).filter(
        Icerik.tur == 'Dizi',
        (Icerik.poster_url == None) | (Icerik.poster_url.like('%placehold%'))
    ).all()
    print(f"📦 Güncellenecek Dizi Sayısı: {len(series)}")
    updated_count = 0
    not_found_count = 0
    error_count = 0
    for index, show in enumerate(series):
        try:
            if index > 0 and index % 10 == 0:
                time.sleep(1) 
            query = urllib.parse.quote(show.baslik)
            url = f"http://api.tvmaze.com/search/shows?q={query}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    show_data = results[0].get('show', {})
                    image_data = show_data.get('image', {})
                    poster_url = None
                    if image_data:
                        poster_url = image_data.get('original') or image_data.get('medium')
                    if poster_url:
                        show.poster_url = poster_url
                        updated_count += 1
                        print(f"  [OK] {show.baslik[:20]}... -> Bulundu", end='\r')
                    else:
                        print(f"  [--] {show.baslik[:20]}... -> Resim Yok", end='\r')
                        not_found_count += 1
                else:
                    not_found_count += 1
            else:
                error_count += 1
            if updated_count % 50 == 0:
                db.commit()
        except Exception as e:
            error_count += 1
            print(f"  [ERR] {show.baslik}: {e}")
    db.commit()
    db.close()
    print("\n" + "="*40)
    print("✅ GÜNCELLEME TAMAMLANDI")
    print(f"   Güncellenen: {updated_count}")
    print(f"   Bulunamayan: {not_found_count}")
    print(f"   Hatalar: {error_count}")
if __name__ == "__main__":
    update_series_covers()