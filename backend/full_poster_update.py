"""
TÜM İÇERİKLERİ OMDb İLE GÜNCELLE (Tam Versiyon)
Film, Dizi, Kitap - Hepsi için gerçek posterler
"""
import requests
from database import SessionLocal, Icerik
import time

OMDB_API_KEY = '6fc2b2fd'
OMDB_URL = "http://www.omdbapi.com/"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

def update_all():
    db = SessionLocal()
    
    # 1. FİLMLER (5000 film)
    print("\n" + "="*60)
    print("📽️  FİLMLER GÜNCELLENİYOR (5000 film)")
    print("="*60)
    
    movies = db.query(Icerik).filter(Icerik.tur == 'Film').limit(5000).all()
    movie_count = 0
    
    for i, movie in enumerate(movies):
        try:
            response = requests.get(OMDB_URL, params={
                'apikey': OMDB_API_KEY,
                't': movie.baslik,
                'type': 'movie'
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    movie.poster_url = data['Poster']
                    movie_count += 1
                    
                    if movie_count % 10 == 0:
                        print(f"  ✅ {movie_count}/5000 film", end='\r')
                    
                    if movie_count % 100 == 0:
                        db.commit()  # Her 100'de bir kaydet
                        print(f"\n  💾 {movie_count} film kaydedildi")
            
            if (i + 1) % 100 == 0:
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            continue
    
    db.commit()
    print(f"\n✅ {movie_count} film posteri güncellendi!")
    
    # 2. DİZİLER (2000 dizi)
    print("\n" + "="*60)
    print("📺 DİZİLER GÜNCELLENİYOR (2000 dizi)")
    print("="*60)
    
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').limit(2000).all()
    series_count = 0
    
    for i, show in enumerate(series):
        try:
            response = requests.get(OMDB_URL, params={
                'apikey': OMDB_API_KEY,
                't': show.baslik,
                'type': 'series'
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    show.poster_url = data['Poster']
                    series_count += 1
                    
                    if series_count % 100 == 0:
                        print(f"  ✅ {series_count}/2000 dizi")
                        db.commit()
            
            if (i + 1) % 100 == 0:
                time.sleep(1)
                
        except:
            continue
    
    db.commit()
    print(f"\n✅ {series_count} dizi posteri güncellendi!")
    
    # 3. KİTAPLAR (2000 kitap)
    print("\n" + "="*60)
    print("📚 KİTAPLAR GÜNCELLENİYOR (2000 kitap)")
    print("="*60)
    
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').limit(2000).all()
    book_count = 0
    
    for i, book in enumerate(books):
        try:
            response = requests.get(GOOGLE_BOOKS_URL, params={
                'q': book.baslik,
                'maxResults': 1
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    img = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
                    cover = img.get('thumbnail') or img.get('smallThumbnail')
                    
                    if cover:
                        book.poster_url = cover.replace('http://', 'https://')
                        book_count += 1
                        
                        if book_count % 100 == 0:
                            print(f"  ✅ {book_count}/2000 kitap")
                            db.commit()
            
            if (i + 1) % 100 == 0:
                time.sleep(1)
                
        except:
            continue
    
    db.commit()
    print(f"\n✅ {book_count} kitap kapağı güncellendi!")
    
    db.close()
    
    print("\n" + "="*60)
    print("✅ TAMAMLANDI!")
    print(f"   📽️  {movie_count} film")
    print(f"   📺 {series_count} dizi")
    print(f"   📚 {book_count} kitap")
    print(f"   📊 TOPLAM: {movie_count + series_count + book_count}")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_all()
