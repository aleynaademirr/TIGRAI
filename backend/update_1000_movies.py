"""
1000 filmin posterlerini OMDB ile güncelle
"""
import requests
from database import SessionLocal, Icerik
import time
import os
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '2a8a018c')
OMDB_URL = "http://www.omdbapi.com/"

def update_1000_movies():
    print("\n" + "="*70)
    print("🎬 1000 FİLMİN POSTERLERİ OMDB İLE GÜNCELLENİYOR")
    print("="*70)
    
    db = SessionLocal()
    
    # İlk 1000 filmi getir (IMDB puanına göre sıralı)
    print("\n📊 Filmler getiriliyor...")
    movies = db.query(Icerik).filter(
        Icerik.tur == 'Film'
    ).order_by(Icerik.imdb_puani.desc()).limit(1000).all()
    
    print(f"✅ {len(movies)} film bulundu\n")
    
    updated = 0
    failed = 0
    skipped = 0
    
    for i, movie in enumerate(movies, 1):
        try:
            # Zaten gerçek poster varsa atla
            if movie.poster_url and 'placehold' not in movie.poster_url.lower() and 'media-amazon' in movie.poster_url:
                skipped += 1
                if i % 50 == 0:
                    print(f"⏭️  [{i}/1000] {skipped} film zaten güncel", end='\r')
                continue
            
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
                        print(f"✅ [{i}/1000] {movie.baslik[:50]:<50} | Güncellendi: {updated}")
                else:
                    failed += 1
            else:
                failed += 1
            
            # Rate limit için bekleme
            if i % 100 == 0:
                print(f"\n⏸️  100 istek yapıldı, 2 saniye bekleniyor...")
                time.sleep(2)
                # Veritabanını kaydet
                db.commit()
                print(f"💾 İlerleme kaydedildi: {updated} güncellendi, {failed} başarısız, {skipped} atlandı\n")
            elif i % 10 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            failed += 1
            if i % 50 == 0:
                print(f"❌ [{i}/1000] Hata: {str(e)[:30]}")
            continue
    
    # Son kayıt
    print("\n💾 Son değişiklikler kaydediliyor...")
    db.commit()
    db.close()
    
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print(f"   ✅ {updated} film posteri güncellendi")
    print(f"   ⚠️  {failed} film için poster bulunamadı")
    print(f"   ⏭️  {skipped} film zaten günceldi")
    print(f"   📊 TOPLAM: {len(movies)} film işlendi")
    print("="*70 + "\n")

if __name__ == "__main__":
    update_1000_movies()
