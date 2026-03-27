from database import SessionLocal, Icerik
import random
def fix_poster_urls():
    db = SessionLocal()
    try:
        contents_without_posters = db.query(Icerik).filter(
            (Icerik.poster_url == None) | (Icerik.poster_url == "")
        ).all()
        print(f"Poster URL'si olmayan {len(contents_without_posters)} içerik bulundu.")
        colors = ['1abc9c', '2ecc71', '3498db', '9b59b6', '34495e', '16a085', '27ae60', '2980b9', '8e44ad', '2c3e50',
                  , 'e67e22', 'e74c3c', 'ecf0f1', '95a5a6', 'f39c12', 'd35400', 'c0392b', 'bdc3c7', '7f8c8d']
        updated = 0
        for content in contents_without_posters:
            safe_title = content.baslik[:30].replace(' ', '+')  
            bg_color = random.choice(colors)
            if content.tur == "Kitap":
                content.poster_url = f"https://placehold.co/300x450/{bg_color}/ffffff/png?text={safe_title}"
            else:
                content.poster_url = f"https://placehold.co/300x450/{bg_color}/ffffff/png?text={safe_title}"
            updated += 1
            if updated % 100 == 0:
                print(f"{updated} içerik güncellendi...")
                db.commit()
        db.commit()
        print(f"\n✅ Toplam {updated} içeriğin poster URL'si güncellendi!")
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()
if __name__ == "__main__":
    fix_poster_urls()