import os
import sys
from database import SessionLocal, init_db
from kaggle_data_importer import KaggleDataImporter, import_from_local_csv
def main():
    print("=" * 60)
    print("VERİ YÜKLEME SCRİPTİ")
    print("=" * 60)
    print()
    init_db()
    db = SessionLocal()
    try:
        importer = KaggleDataImporter()
        books_csv = "books.csv"
        if os.path.exists(books_csv):
            print(f"\n[KITAPLAR] {books_csv} dosyası bulundu, yükleniyor...")
            import_from_local_csv(books_csv, "Kitap", db, limit=5000)
        else:
            print(f"\n[UYARI] {books_csv} bulunamadı, atlanıyor...")
        movies_csv = "kaggle_data/movies/movies_metadata.csv"
        if os.path.exists(movies_csv):
            print(f"\n[FİLMLER] {movies_csv} dosyası bulundu, yükleniyor...")
            import_from_local_csv(movies_csv, "Film", db, limit=None)
        else:
            print(f"\n[UYARI] {movies_csv} bulunamadı, atlanıyor...")
        tv_csv_options = [

        ]
        tv_csv = None
        for option in tv_csv_options:
            if os.path.exists(option):
                tv_csv = option
                break
        if tv_csv:
            print(f"\n[DİZİLER] {tv_csv} dosyası bulundu, yükleniyor...")
            import_from_local_csv(tv_csv, "Dizi", db, limit=None)
        else:
            print(f"\n[UYARI] Dizi dosyası bulunamadı, atlanıyor...")
        from database import Icerik
        total_count = db.query(Icerik).count()
        film_count = db.query(Icerik).filter(Icerik.tur == 'Film').count()
        dizi_count = db.query(Icerik).filter(Icerik.tur == 'Dizi').count()
        kitap_count = db.query(Icerik).filter(Icerik.tur == 'Kitap').count()
        print("\n" + "=" * 60)
        print("YÜKLEME TAMAMLANDI!")
        print("=" * 60)
        print(f"\nToplam içerik: {total_count}")
        print(f"  - Film: {film_count}")
        print(f"  - Dizi: {dizi_count}")
        print(f"  - Kitap: {kitap_count}")
        print()
        print("\n[ML] Yapay zeka modeli eğitiliyor...")
        from ml_model import recommendation_engine
        recommendation_engine.train(db)
        print("[ML] Model başarıyla eğitildi ve kaydedildi!")
    except Exception as e:
        print(f"\n[HATA] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
    print("\n✅ İşlem tamamlandı! Backend'i yeniden başlatabilirsiniz.")
if __name__ == "__main__":
    main()