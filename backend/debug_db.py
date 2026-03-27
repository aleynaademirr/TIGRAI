from sqlalchemy.orm import Session
from database import SessionLocal, Icerik, engine
from sqlalchemy import text

def debug_series():
    db = SessionLocal()
    
    # 1. Toplam içerik
    total = db.query(Icerik).count()
    print(f"Toplam İçerik: {total}")
    
    # 2. Dizi Sayısı
    dizi_count = db.query(Icerik).filter(Icerik.tur == 'Dizi').count()
    print(f"Toplam Dizi: {dizi_count}")
    
    # 3. İlk 20 Dizi Örneği
    print("\n--- İlk 20 Dizi ---")
    diziler = db.query(Icerik).filter(Icerik.tur == 'Dizi').limit(20).all()
    for d in diziler:
        print(f"ID: {d.id} | Başlık: {d.baslik} | Tür: {d.tur} | Poster: {d.poster_url}")

if __name__ == "__main__":
    debug_series()
