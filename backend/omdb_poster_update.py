"""
OMDb API kullanarak gerçek posterler çek (Çok daha hızlı!)
"""
import requests
from database import SessionLocal, Icerik
import time
import os
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '2a8a018c')
OMDB_URL = "http://www.omdbapi.com/"

def update_with_omdb():
    print("\n" + "="*60)
    print("OMDb API İLE GERÇEK POSTERLER ÇEKİLİYOR")
    print("="*60)
    
    db = SessionLocal()
    
    # Diziler
    print("\n📺 Diziler güncelleniyor...")
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').limit(1000).all()
    
    series_updated = 0
    series_failed = 0
    
    for i, show in enumerate(series):
        try:
            params = {
                'apikey': OMDB_API_KEY,
                't': show.baslik,
                'type': 'series'
            }
            
            response = requests.get(OMDB_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    show.poster_url = data['Poster']
                    series_updated += 1
                    
                    if series_updated % 50 == 0:
                        print(f"  ✅ {series_updated}/1000 dizi bulundu", end='\r')
                else:
                    series_failed += 1
            
            # OMDb rate limit: 1000 requests per day (free tier)
            if (i + 1) % 100 == 0:
                time.sleep(1)
                
        except Exception as e:
            series_failed += 1
            continue
    
    print(f"\n✅ {series_updated} dizi posteri güncellendi!")
    print(f"⚠️  {series_failed} dizi için poster bulunamadı")
    
    # Filmler (eksik olanlar için)
    print("\n📽️  Eksik film posterleri güncelleniyor...")
    movies = db.query(Icerik).filter(
        Icerik.tur == 'Film',
        Icerik.poster_url == None
    ).limit(500).all()
    
    movies_updated = 0
    
    for i, movie in enumerate(movies):
        try:
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
                    movies_updated += 1
                    
                    if movies_updated % 50 == 0:
                        print(f"  ✅ {movies_updated}/500 film bulundu", end='\r')
            
            if (i + 1) % 100 == 0:
                time.sleep(1)
                
        except:
            continue
    
    print(f"\n✅ {movies_updated} film posteri güncellendi!")
    
    # Kitaplar (Google Books)
    print("\n📚 Kitaplar güncelleniyor (Google Books)...")
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').limit(500).all()
    
    books_updated = 0
    
    for i, book in enumerate(books):
        try:
            params = {
                'q': book.baslik,
                'maxResults': 1,
                'printType': 'books'
            }
            
            response = requests.get('https://www.googleapis.com/books/v1/volumes', params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('items'):
                    image_links = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
                    cover = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                    
                    if cover:
                        book.poster_url = cover.replace('http://', 'https://')
                        books_updated += 1
                        
                        if books_updated % 50 == 0:
                            print(f"  ✅ {books_updated}/500 kitap bulundu", end='\r')
            
            if (i + 1) % 100 == 0:
                time.sleep(1)
                
        except:
            continue
    
    print(f"\n✅ {books_updated} kitap kapağı güncellendi!")
    
    # Kaydet
    db.commit()
    db.close()
    
    print("\n" + "="*60)
    print("✅ TAMAMLANDI!")
    print(f"   📺 {series_updated} dizi posteri")
    print(f"   📽️  {movies_updated} film posteri")
    print(f"   📚 {books_updated} kitap kapağı")
    print(f"   📊 TOPLAM: {series_updated + movies_updated + books_updated}")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_with_omdb()
