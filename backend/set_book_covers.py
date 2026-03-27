from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import urllib.parse
def set_book_covers():
    db = SessionLocal()
    try:
        books = db.query(Icerik).filter(Icerik.tur == 'Kitap', Icerik.poster_url == None).all()
        print(f"Found {len(books)} books without covers.")
        count = 0
        colors = ['1abc9c', '2ecc71', '3498db', '9b59b6', '34495e', '16a085', '27ae60', '2980b9', '8e44ad', '2c3e50',
                  , 'e67e22', 'e74c3c', 'ecf0f1', '95a5a6', 'f39c12', 'd35400', 'c0392b', 'bdc3c7', '7f8c8d']
        for book in books:
            safe_title = urllib.parse.quote(book.baslik)
            bg_color = random.choice(colors)
            url = f"https://placehold.co/300x450/{bg_color}/ffffff/png?text={safe_title}"
            book.poster_url = url
            count += 1
            if count % 100 == 0:
                print(f"Updated {count} books...", end='\r')
        db.commit()
        print(f"\nSuccessfully set covers for {count} books.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
if __name__ == "__main__":
    set_book_covers()