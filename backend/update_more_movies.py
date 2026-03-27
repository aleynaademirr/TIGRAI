"""
Kalan filmlerin posterlerini OMDB ile güncelle (Yeni API ile devam)
"""
import requests
from database import SessionLocal, Icerik
import time
import os
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '6fc2b2fd')
OMDB_URL = "http://www.omdbapi.com/"

def update_more_movies(limit=2000):
    print("\n" + "="*70)
    print(f"🎬 {limit} FİLMİN POSTERLERİ OMDB İLE GÜNCELLENİYOR (YENİ API)")
    print("="*70)
    
    db = SessionLocal()
    
    # Placeholder posterli filmleri getir (IMDB puanına göre sıralı)
    print("\n📊 Placeholder posterli filmler getiriliyor...")
    movies = db.query(Icerik).filter(
        Icerik.tur == 'Film',
        Icerik.poster_url.like('%placehold%')
    ).order_by(Icerik.imdb_puani.desc()).limit(limit).all()
    
    print(f"✅ {len(movies)} film bulundu\n")
    print(f"🔑 API Key: {OMDB_API_KEY}\n")
    
    updated = 0
    failed = 0
    
    for i, movie in enumerate(movies, 1):
        try:
            # OMDB'den çek
            params = {
                'apikey': OMDB_API_KEY,
                't': movie.baslik,
                'type': 'movie'
            }
            
            response = requests.get(OMDB_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    movie.poster_url = data['Poster']
                    updated += 1
                    
                    if updated % 10 == 0:
                        print(f"✅ [{i}/{len(movies)}] {movie.baslik[:50]:<50} | Güncellendi: {updated}")
                else:
                    failed += 1
                    if failed % 50 == 0:
                        print(f"⚠️  [{i}/{len(movies)}] Başarısız: {failed}")
            else:
                failed += 1
            
            # Rate limit için bekleme
            if i % 100 == 0:
                print(f"\n⏸️  100 istek yapıldı, 2 saniye bekleniyor...")
                time.sleep(2)
                # Veritabanını kaydet
                db.commit()
                print(f"💾 İlerleme kaydedildi: {updated} güncellendi, {failed} başarısız\n")
            elif i % 10 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            failed += 1
            continue
    
    # Son kayıt
    print("\n💾 Son değişiklikler kaydediliyor...")
    db.commit()
    db.close()
    
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print(f"   ✅ {updated} film posteri güncellendi")
    print(f"   ⚠️  {failed} film için poster bulunamadı")
    print(f"   📊 TOPLAM: {len(movies)} film işlendi")
    print(f"   📈 Başarı oranı: {(updated/len(movies)*100):.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    # 2000 film daha güncelle
    update_more_movies(2000)
