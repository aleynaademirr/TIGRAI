from sqlalchemy.orm import sessionmaker
from database import Icerik, Base
DB_URL = "sqlite:///./recommendation_system.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
def check_stats():
    db = SessionLocal()
    total = db.query(Icerik).count()
    null_posters = db.query(Icerik).filter((Icerik.poster_url == None) | (Icerik.poster_url == "")).count()
    placeholders = db.query(Icerik).filter(Icerik.poster_url.like("%placehold.co%")).count()
    tmdb_posters = db.query(Icerik).filter(Icerik.poster_url.like("%tmdb.org%")).count()
    amazon_posters = db.query(Icerik).filter(Icerik.poster_url.like("%amazon%")).count()
    print("=== DATABASE POSTER STATISTICS ===")
    print(f"Total Content: {total}")
    print(f"NULL/Empty   : {null_posters}")
    print(f"Placeholders : {placeholders}")
    print(f"TMDB/Real    : {tmdb_posters} (Movies)")
    print(f"Amazon/Real  : {amazon_posters} (Books)")
    print("================================")
    for tur in ['Film', 'Dizi', 'Kitap']:
        count = db.query(Icerik).filter(Icerik.tur == tur).count()
        missing = db.query(Icerik).filter(Icerik.tur == tur, (Icerik.poster_url == None) | (Icerik.poster_url == "")).count()
        print(f"{tur}: Total {count}, Missing {missing}")
if __name__ == "__main__":
    check_stats()