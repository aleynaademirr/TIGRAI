import csv
import json
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik, init_db
from typing import List, Dict
def import_from_csv(csv_file_path: str, db: Session):
    imported_count = 0
    skipped_count = 0
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mevcut = db.query(Icerik).filter(Icerik.baslik == row['baslik']).first()
                if mevcut:
                    skipped_count += 1
                    continue
                icerik = Icerik(
                    baslik=row['baslik'],
                    tur=row.get('tur', 'Film'),
                    kategoriler=row.get('kategoriler'),
                    ozet=row.get('ozet'),
                    yil=int(row['yil']) if row.get('yil') else None,
                    imdb_puani=float(row['imdb_puani']) if row.get('imdb_puani') else None
                )
                db.add(icerik)
                imported_count += 1
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"  {imported_count} içerik import edildi...")
        db.commit()
        print(f"[OK] CSV'den {imported_count} içerik import edildi, {skipped_count} atlandı")
    except Exception as e:
        db.rollback()
        print(f"[ERR] CSV import hatası: {e}")
        raise
def import_from_json(json_file_path: str, db: Session):
    imported_count = 0
    skipped_count = 0
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                mevcut = db.query(Icerik).filter(Icerik.baslik == item['baslik']).first()
                if mevcut:
                    skipped_count += 1
                    continue
                icerik = Icerik(**item)
                db.add(icerik)
                imported_count += 1
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"  {imported_count} içerik import edildi...")
        db.commit()
        print(f"[OK] JSON'dan {imported_count} içerik import edildi, {skipped_count} atlandı")
    except Exception as e:
        db.rollback()
        print(f"[ERR] JSON import hatası: {e}")
        raise
def import_from_omdb_api(api_key: str, movie_titles: List[str], db: Session):
    imported_count = 0
    for title in movie_titles:
        try:
            mevcut = db.query(Icerik).filter(Icerik.baslik == title).first()
            if mevcut:
                continue
            url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    icerik = Icerik(
                        baslik=data.get('Title', title),
                        tur='Film',
                        kategoriler=data.get('Genre', ''),
                        ozet=data.get('Plot', ''),
                        yil=int(data.get('Year', 0)) if data.get('Year', '').isdigit() else None,
                        imdb_puani=float(data.get('imdbRating', 0)) if data.get('imdbRating') != 'N/A' else None
                    )
                    db.add(icerik)
                    imported_count += 1
                    print(f"  ✓ {title} import edildi")
            import time
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ {title} import edilemedi: {e}")
            continue
    db.commit()
    print(f"[OK] OMDB API'den {imported_count} film import edildi")
def create_sample_csv(output_file: str = "sample_movies.csv"):
    sample_data = [
        {
            : 'The Matrix',
            : 'Film',
            : 'Bilim Kurgu, Aksiyon',
            : 'Bir bilgisayar programcısı, gerçek dünyanın bir simülasyon olduğunu keşfeder.',
            : 1999,
            : 8.7
        },
        {
            : 'Pulp Fiction',
            : 'Film',
            : 'Suç, Dram',
            : 'Los Angeles\'ta birbirine bağlı birkaç suç hikayesi.',
            : 1994,
            : 8.9
        },
    ]
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['baslik', 'tur', 'kategoriler', 'ozet', 'yil', 'imdb_puani'])
        writer.writeheader()
        writer.writerows(sample_data)
    print(f"[OK] Örnek CSV dosyası oluşturuldu: {output_file}")
if __name__ == "__main__":
    print("=" * 60)
    print("GENİŞ VERİ SETİ IMPORT SCRIPTİ")
    print("=" * 60)
    print()
    init_db()
    db = SessionLocal()
    try:
        print("Import yöntemini seçin:")
        print("1. CSV dosyasından import")
        print("2. JSON dosyasından import")
        print("3. OMDB API'den import (API key gerekli)")
        print("4. Örnek CSV dosyası oluştur")
        choice = input("\nSeçiminiz (1-4): ").strip()
        if choice == "1":
            csv_file = input("CSV dosya yolu: ").strip()
            import_from_csv(csv_file, db)
        elif choice == "2":
            json_file = input("JSON dosya yolu: ").strip()
            import_from_json(json_file, db)
        elif choice == "3":
            api_key = input("OMDB API Key: ").strip()
            titles_input = input("Film başlıkları (virgülle ayırın): ").strip()
            titles = [t.strip() for t in titles_input.split(',')]
            import_from_omdb_api(api_key, titles, db)
        elif choice == "4":
            output = input("Çıktı dosya adı (varsayılan: sample_movies.csv): ").strip()
            if not output:
                output = "sample_movies.csv"
            create_sample_csv(output)
        else:
            print("[ERR] Geçersiz seçim!")
        total_count = db.query(Icerik).count()
        print(f"\n[INFO] Toplam içerik sayısı: {total_count}")
    except Exception as e:
        print(f"[ERR] Hata: {e}")
        db.rollback()
    finally:
        db.close()