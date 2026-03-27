from database import SessionLocal, Icerik, Puan, Kullanici
from sqlalchemy import func
def check_stats():
    db = SessionLocal()
    try:
        total_icerik = db.query(func.count(Icerik.id)).scalar()
        total_puan = db.query(func.count(Puan.id)).scalar()
        total_user = db.query(func.count(Kullanici.id)).scalar()
        film_count = db.query(func.count(Icerik.id)).filter(Icerik.tur == 'Film').scalar()
        dizi_count = db.query(func.count(Icerik.id)).filter(Icerik.tur == 'Dizi').scalar()
        kitap_count = db.query(func.count(Icerik.id)).filter(Icerik.tur == 'Kitap').scalar()
        print("="*40)
        print("GERÇEK VERİ SETİ İSTATİSTİKLERİ")
        print("="*40)
        print(f"TOPLAM İÇERİK: {total_icerik}")
        print(f"  - Film: {film_count}")
        print(f"  - Dizi: {dizi_count}")
        print(f"  - Kitap: {kitap_count}")
        print(f"TOPLAM PUAN: {total_puan}")
        print(f"KULLANICI SAYISI: {total_user}")
        print("="*40)
    finally:
        db.close()
if __name__ == "__main__":
    check_stats()