from sqlalchemy.orm import Session
from database import SessionLocal, Icerik, Puan
from sqlalchemy import text
def cleanup_database():
    db = SessionLocal()
    print("Starting database cleanup...")
    try:
        print("Cleaning items with empty titles...")
        db.query(Icerik).filter(
            (Icerik.baslik == None) | (Icerik.baslik == "") | (Icerik.baslik == "null") | (Icerik.baslik == "Unknown")
        ).delete(synchronize_session=False)
        print("Cleaning items with empty types...")
        db.query(Icerik).filter(
            (Icerik.tur == None) | (Icerik.tur == "")
        ).delete(synchronize_session=False)
        db.commit()
        print("Database cleanup completed successfully.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()
if __name__ == "__main__":
    cleanup_database()