from database import SessionLocal, Icerik
from sqlalchemy import desc

def diagnose_imdb():
    db = SessionLocal()
    
    total_movies = db.query(Icerik).filter(Icerik.tur == 'Film').count()
    scored_movies = db.query(Icerik).filter(Icerik.tur == 'Film', Icerik.imdb_puani > 0).count()
    
    print(f"Toplam Film: {total_movies}")
    print(f"Puanlı Film (>0): {scored_movies}")
    print(f"Puansız Film: {total_movies - scored_movies}")
    
    print("\nVeritabanındaki En Yüksek Puanlı 20 Film:")
    print("-" * 50)
    top_movies = db.query(Icerik).filter(Icerik.tur == 'Film').order_by(desc(Icerik.imdb_puani)).limit(20).all()
    
    for m in top_movies:
        print(f"[{m.imdb_puani}] {m.baslik} ({m.yil})")
        
    # Check specifically for a known movie
    print("\nÖrnek Kontrol (Inception):")
    inception = db.query(Icerik).filter(Icerik.baslik.like("%Inception%")).first()
    if inception:
        print(f"Inception Puanı: {inception.imdb_puani}")
    else:
        print("Inception bulunamadı.")

    db.close()

if __name__ == "__main__":
    diagnose_imdb()
