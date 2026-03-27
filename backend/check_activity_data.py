from database import SessionLocal, Yorum, Puan, Kullanici, Icerik
from sqlalchemy import func
import traceback

def check_data():
    db = SessionLocal()
    try:
        print("Checking Comments integrity...")
        comments = db.query(Yorum).order_by(Yorum.olusturma_tarihi.desc()).limit(20).all()
        for i, c in enumerate(comments):
            try:
                user = c.kullanici
                content = c.icerik
                print(f"Comment {c.id}: User={user.kullanici_adi if user else 'None'}, Content={content.baslik if content else 'None'}")
                if not user or not content:
                    print(f"  WARNING: Orphaned comment {c.id}")
            except Exception as e:
                print(f"  ERROR accessing relations for comment {c.id}: {e}")
                
        print("\nChecking Ratings integrity...")
        ratings = db.query(Puan).order_by(Puan.puanlama_tarihi.desc()).limit(20).all()
        for i, r in enumerate(ratings):
            try:
                user = r.kullanici
                content = r.icerik
                print(f"Rating {r.id}: User={user.kullanici_adi if user else 'None'}, Content={content.baslik if content else 'None'}")
                if not user or not content:
                    print(f"  WARNING: Orphaned rating {r.id}")
            except Exception as e:
                print(f"  ERROR accessing relations for rating {r.id}: {e}")

    except Exception as e:
        print(f"General Error: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
