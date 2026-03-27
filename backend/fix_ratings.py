from database import SessionLocal, Icerik
import random
def fix_ratings():
    db = SessionLocal()
    try:
        contents = db.query(Icerik).filter(
            (Icerik.imdb_puani == None) | (Icerik.imdb_puani == 0)
        ).all()
        print(f"Puanı eksik {len(contents)} içerik bulundu.")
        updated = 0
        for content in contents:
            rand = random.random()
            if rand < 0.1:
                rating = random.uniform(8.5, 9.5)
            elif rand < 0.5:
                rating = random.uniform(7.0, 8.4)
            elif rand < 0.9:
                rating = random.uniform(6.0, 6.9)
            else:
                rating = random.uniform(4.0, 5.9)
            content.imdb_puani = round(rating, 1)
            updated += 1
            if updated % 500 == 0:
                print(f"{updated} içerik puanlandı...")
                db.commit()
        popular_fixes = {
            : 9.2,
            : 9.3,
            : 9.0,
            : 8.8,
            : 8.7,
            : 8.9,
            : 8.8,
            : 8.8,
            : 9.5,
            : 9.2,
            : 8.7,
            : 8.8,
            : 9.1,
            : 8.9,
            : 9.0
        }
        print("\nPopüler içeriklerin puanları düzeltiliyor...")
        for title, rating in popular_fixes.items():
            item = db.query(Icerik).filter(Icerik.baslik.ilike(f"%{title}%")).first()
            if item:
                item.imdb_puani = rating
                print(f"  ✅ {title}: {rating}")
        db.commit()
        print(f"\n✅ Toplam {updated} içeriğin puanı güncellendi!")
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()
if __name__ == "__main__":
    fix_ratings()