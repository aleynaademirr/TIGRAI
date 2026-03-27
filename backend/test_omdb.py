"""
HIZLI VE BASIT - OMDb ile poster güncelle
"""
import requests
from database import SessionLocal, Icerik
import time

OMDB_API_KEY = '6fc2b2fd'
OMDB_URL = "http://www.omdbapi.com/"

db = SessionLocal()

# Sadece ilk 100 filmi test et
print("\n📽️  İlk 100 film test ediliyor...")
movies = db.query(Icerik).filter(Icerik.tur == 'Film').limit(100).all()

updated = 0
for i, movie in enumerate(movies):
    try:
        params = {'apikey': OMDB_API_KEY, 't': movie.baslik, 'type': 'movie'}
        response = requests.get(OMDB_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                movie.poster_url = data['Poster']
                updated += 1
                print(f"✅ {updated}/100 - {movie.baslik}")
        
        time.sleep(0.1)  # Rate limiting
    except Exception as e:
        print(f"❌ Hata: {movie.baslik} - {e}")

db.commit()
db.close()

print(f"\n✅ {updated} film posteri güncellendi!")
