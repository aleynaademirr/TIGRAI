import requests
import os
from database import SessionLocal, Icerik
from sqlalchemy import desc
import time
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_real_posters():
    print("="*60)
    print("GERÇEK POSTERLER İNDİRİLİYOR (OMDb/TMDB)")
    print("="*60)
    
    if not OMDB_API_KEY and not TMDB_API_KEY:
        print("❌ API Key bulunamadı (.env dosyasını kontrol et)")
        return

    db = SessionLocal()
    # Sadece Placeholder olanları veya bozuk olanları güncelle
    # Öncelik: En yüksek IMDB puanlı veya en çok yorum alanlar (veritabanında popülarite varsa)
    # Şimdilik IMDB puanına göre sıralayalım ki en iyi filmlerin posteri olsun.
    movies = db.query(Icerik).filter(
        Icerik.tur == 'Film',
        (Icerik.poster_url.like('%placehold%') | (Icerik.poster_url == None))
    ).order_by(desc(Icerik.yil)).limit(1000).all() 
    # Limit koydum, API kotasını bitirmeyelim diye. İlk etapta 1000 film.

    print(f"Hedef: {len(movies)} film için poster aranacak...")
    
    updated = 0
    not_found = 0
    
    for i, movie in enumerate(movies):
        title = movie.baslik
        year = movie.yil
        
        poster_url = None
        
        # 1. OMDb API Dene
        if OMDB_API_KEY:
            try:
                # Yıl parametresi de ekleyelim doğruluk artsın
                url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
                r = requests.get(url, timeout=5)
                data = r.json()
                
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    poster_url = data.get('Poster')
            except Exception as e:
                print(f"OMDb Error ({title}): {e}")

        # 2. Eğer OMDb bulamazsa ve TMDB Key varsa TMDB dene (Search)
        if not poster_url and TMDB_API_KEY:
            try:
                url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&year={year}"
                r = requests.get(url, timeout=5)
                data = r.json()
                if data.get('results'):
                    path = data['results'][0].get('poster_path')
                    if path:
                        poster_url = f"https://image.tmdb.org/t/p/w500{path}"
            except Exception as e:
                 print(f"TMDB Error ({title}): {e}")

        if poster_url:
            movie.poster_url = poster_url
            updated += 1
            print(f"✅ {title} -> Poster Bulundu")
        else:
            not_found += 1
            print(f"❌ {title} -> Bulunamadı")
            
        # Her 10 isteği commit edelim
        if i % 10 == 0:
            db.commit()
            
        # API Rate Limit (biraz bekleme)
        time.sleep(0.2)

    db.commit()
    db.close()
    print(f"\nTAMAMLANDI: {updated} film güncellendi. {not_found} bulunamadı.")

if __name__ == "__main__":
    fetch_real_posters()
