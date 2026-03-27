from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import urllib.parse
def fill_all_missing_images():
    db = SessionLocal()
    try:
        missing_contents = db.query(Icerik).filter(
            (Icerik.poster_url == None) | (Icerik.poster_url == "") | (Icerik.poster_url == "null")
        ).all()
        print(f"Found {len(missing_contents)} items (Movies/Series/Books) without posters.")
        count = 0
        colors = ['1abc9c', '2ecc71', '3498db', '9b59b6', '34495e', '16a085', '27ae60', '2980b9', '8e44ad', '2c3e50',
                  , 'e67e22', 'e74c3c', 'ecf0f1', '95a5a6', 'f39c12', 'd35400', 'c0392b', 'bdc3c7', '7f8c8d']
        for item in missing_contents:
            safe_title = urllib.parse.quote(item.baslik)
            bg_color = random.choice(colors)
            url = f"https://placehold.co/300x450/{bg_color}/ffffff/png?text={safe_title}"
            item.poster_url = url
            count += 1
            if count % 100 == 0:
                print(f"Updated {count} items...", end='\r')
        db.commit()
        print(f"\nSuccessfully generated placeholders for {count} items.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
if __name__ == "__main__":
    fill_all_missing_images()