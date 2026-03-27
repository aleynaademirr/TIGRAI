"""
HIZLI VERSİYON: Sadece ilk 500 dizi ve 500 kitap için gerçek posterler
"""
import requests
from database import SessionLocal, Icerik
import time
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '2a8a018c')
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/tv"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"

def quick_update():
    print("\n" + "="*60)
    print("HIZLI POSTER GÜNCELLEME (İlk 500 dizi + 500 kitap)")
    print("="*60)
    
    db = SessionLocal()
    
    # İlk 500 dizi
    print("\n📺 Diziler güncelleniyor...")
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').limit(500).all()
    
    series_updated = 0
    for i, show in enumerate(series):
        try:
            params = {'api_key': TMDB_API_KEY, 'query': show.baslik}
            response = requests.get(TMDB_SEARCH_URL, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and data['results'][0].get('poster_path'):
                    show.poster_url = f"{TMDB_IMAGE_BASE}{data['results'][0]['poster_path']}"
                    series_updated += 1
                    
                    if series_updated % 20 == 0:
                        print(f"  ✅ {series_updated}/500 dizi", end='\r')
            
            if (i + 1) % 40 == 0:
                time.sleep(1)
        except:
            continue
    
    print(f"\n✅ {series_updated} dizi posteri güncellendi!")
    
    # İlk 500 kitap
    print("\n📚 Kitaplar güncelleniyor...")
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').limit(500).all()
    
    books_updated = 0
    for i, book in enumerate(books):
        try:
            params = {'q': book.baslik, 'maxResults': 1}
            response = requests.get(GOOGLE_BOOKS_API, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    image_links = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
                    cover = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                    
                    if cover:
                        book.poster_url = cover.replace('http://', 'https://')
                        books_updated += 1
                        
                        if books_updated % 20 == 0:
                            print(f"  ✅ {books_updated}/500 kitap", end='\r')
            
            if (i + 1) % 50 == 0:
                time.sleep(1)
        except:
            continue
    
    print(f"\n✅ {books_updated} kitap kapağı güncellendi!")
    
    db.commit()
    db.close()
    
    print("\n" + "="*60)
    print(f"✅ TOPLAM: {series_updated + books_updated} poster güncellendi!")
    print("="*60 + "\n")

if __name__ == "__main__":
    quick_update()
