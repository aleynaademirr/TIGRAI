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
    openlibrary_posters = db.query(Icerik).filter(Icerik.poster_url.like("%openlibrary%")).count()
    with open("db_stats_full.txt", "w") as f:
        f.write("=== DATABASE POSTER STATISTICS ===\n")
        f.write(f"Total Content: {total}\n")
        f.write(f"NULL/Empty   : {null_posters}\n")
        f.write(f"Placeholders : {placeholders}\n")
        f.write(f"TMDB/Real    : {tmdb_posters} (Movies)\n")
        f.write(f"Amazon/Real  : {amazon_posters} (Books)\n")
        f.write(f"OpenLibrary  : {openlibrary_posters} (Books)\n")
        f.write("================================\n")
        for tur in ['Film', 'Dizi', 'Kitap']:
            count = db.query(Icerik).filter(Icerik.tur == tur).count()
            missing = db.query(Icerik).filter(Icerik.tur == tur, (Icerik.poster_url == None) | (Icerik.poster_url == "")).count()
            f.write(f"{tur}: Total {count}, Missing {missing}\n")
if __name__ == "__main__":
    check_stats()