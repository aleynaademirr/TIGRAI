import requests
from database import SessionLocal, Icerik
import random

def check_posters():
    db = SessionLocal()
    # Rastgele 5 film seç (poster_url olanlardan)
    icerikler = db.query(Icerik).filter(Icerik.poster_url != None, Icerik.tur == 'Film').all()
    
    if not icerikler:
        print("Film bulunamadı!")
        return

    sample = random.sample(icerikler, 5)
    
    print(f"\n{'='*60}")
    print("POSTER URL KONTROLÜ")
    print(f"{'='*60}")
    
    for item in sample:
        print(f"\nFilm: {item.baslik}")
        print(f"URL:  {item.poster_url}")
        
        try:
            r = requests.head(item.poster_url, timeout=5)
            if r.status_code == 200:
                print("✅ Durum: ÇALIŞIYOR")
            else:
                print(f"❌ Durum: BOZUK (Kod: {r.status_code})")
        except Exception as e:
            print(f"❌ Durum: HATA ({e})")
            
    db.close()

if __name__ == "__main__":
    check_posters()
