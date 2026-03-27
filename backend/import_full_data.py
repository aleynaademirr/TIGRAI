import os
import sys
import json
import traceback
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, Icerik, engine, Base
def import_movies(db, limit=None):
    print("Importing Movies from 'movies_metadata.csv'...")
    file_path = os.path.join(os.path.dirname(__file__), 'movies_metadata.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    count = 0
    csv.field_size_limit(sys.maxsize)
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if limit and count >= limit:
                    break
                title = row.get('title', '').strip()
                if not title:
                    continue
                existing = db.query(Icerik).filter(Icerik.baslik == title, Icerik.tur == 'Film').first()
                if existing:
                    continue
                genres_str = row.get('genres', '[]').replace("'", '"')
                try:
                    genres_list = json.loads(genres_str)
                    genres = ", ".join([g['name'] for g in genres_list])
                except:
                    genres = None
                release_date = row.get('release_date', '')
                year = None
                if release_date and len(release_date) >= 4:
                    try:
                        year = int(release_date[:4])
                    except:
                        pass
                vote_average = row.get('vote_average')
                imdb_score = None
                if vote_average:
                    try:
                        imdb_score = float(vote_average)
                    except:
                        pass
                poster_path = row.get('poster_path')
                poster_url = None
                if poster_path:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                icerik = Icerik(
                    baslik=title,
                    tur='Film',
                    kategoriler=genres,
                    ozet=row.get('overview'),
                    yil=year,
                    imdb_puani=imdb_score,
                    poster_url=poster_url,
                    olusturma_tarihi=datetime.now()
                )
                db.add(icerik)
                count += 1
                if count % 100 == 0:
                    print(f"Movies imported: {count}", end='\r')
                    db.commit()
            except Exception as e:
                continue
    db.commit()
    print(f"\nFinished importing {count} Movies.")
def import_books(db, limit=None):
    print("Importing Books from 'books.csv'...")
    file_path = os.path.join(os.path.dirname(__file__), 'books.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    count = 0
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if limit and count >= limit:
                    break
                title = row.get('title', '').strip()
                if not title:
                    continue
                existing = db.query(Icerik).filter(Icerik.baslik == title, Icerik.tur == 'Kitap').first()
                if existing:
                    continue
                authors = row.get('authors', '')
                pub_date = row.get('publication_date', '')
                year = None
                if pub_date:
                    try:
                        parts = pub_date.split('/')
                        if len(parts) == 3:
                            year = int(parts[2])
                    except:
                        pass
                rating = row.get('average_rating')
                imdb_score = None
                if rating:
                    try:
                        imdb_score = float(rating)
                    except:
                        pass
                icerik = Icerik(
                    baslik=title,
                    tur='Kitap',
                    kategoriler=authors, 
                    ozet=f"Author: {authors}",
                    yil=year,
                    imdb_puani=imdb_score,
                    poster_url=None, 
                    olusturma_tarihi=datetime.now()
                )
                db.add(icerik)
                count += 1
                if count % 100 == 0:
                    print(f"Books imported: {count}", end='\r')
                    db.commit()
            except Exception as e:
                continue
    db.commit()
    print(f"\nFinished importing {count} Books.")
def import_series(db, limit=None):
    print("Importing Series from 'netflix_titles.csv'...")
    file_path = os.path.join(os.path.dirname(__file__), 'netflix_titles.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    count = 0
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if limit and count >= limit:
                    break
                if row.get('type') != 'TV Show':
                    continue
                title = row.get('title', '').strip()
                if not title:
                    continue
                existing = db.query(Icerik).filter(Icerik.baslik == title, Icerik.tur == 'Dizi').first()
                if existing:
                    continue
                release_year = row.get('release_year')
                year = None
                if release_year:
                    try:
                        year = int(release_year)
                    except:
                        pass
                icerik = Icerik(
                    baslik=title,
                    tur='Dizi',
                    kategoriler=row.get('listed_in'),
                    ozet=row.get('description'),
                    yil=year,
                    imdb_puani=None, 
                    poster_url=None, 
                    olusturma_tarihi=datetime.now()
                )
                db.add(icerik)
                count += 1
                if count % 100 == 0:
                    print(f"Series imported: {count}", end='\r')
                    db.commit()
            except Exception as e:
                continue
    db.commit()
    print(f"\nFinished importing {count} Series.")
if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Starting Full Import...")
        import_books(db)
        import_series(db)
        print("Full Import Completed Successfully.")
    except Exception as e:
        print(f"Fatal Error: {e}")
        traceback.print_exc()
    finally:
        db.close()