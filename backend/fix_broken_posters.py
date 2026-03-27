"""
Bozuk TMDB poster URL'lerini temizle ve OMDb ile güncelle
"""
import requests
from database import SessionLocal, Icerik
import time

OMDB_API_KEY = '6fc2b2fd'
OMDB_URL = "http://www.omdbapi.com/"

db = SessionLocal()

print("\n" + "="*60)
print("BOZUK POSTER URL'LERİ TEMİZLENİYOR VE GÜNCELLENİYOR")
print("="*60)

# TMDB posterli filmleri al
movies = db.query(Icerik).filter(
    Icerik.tur == 'Film',
    Icerik.poster_url.like('%tmdb%')
).limit(1000).all()  # İlk 1000 film (API limiti)

print(f"\n✅ {len(movies)} TMDB posterli film bulundu")

updated = 0
failed = 0

for i, movie in enumerate(movies):
    try:
        # OMDb'den poster al
        response = requests.get(OMDB_URL, params={
            'apikey': OMDB_API_KEY,
            't': movie.baslik,
            'type': 'movie'
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                movie.poster_url = data['Poster']
                updated += 1
                
                if updated % 50 == 0:
                    print(f"  ✅ {updated}/1000 film güncellendi")
                    db.commit()
            else:
                failed += 1
        
        # Rate limiting
        if (i + 1) % 100 == 0:
            time.sleep(1)
            
    except:
        failed += 1
        continue

db.commit()
db.close()

print(f"\n" + "="*60)
print("✅ TAMAMLANDI!")
print(f"   ✅ {updated} film OMDb posteri ile güncellendi")
print(f"   ⚠️  {failed} film için poster bulunamadı")
print("="*60 + "\n")
