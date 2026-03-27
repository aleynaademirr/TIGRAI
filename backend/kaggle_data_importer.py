import os
import pandas as pd
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik, init_db
from typing import List, Dict
import json
class KaggleDataImporter:
    def __init__(self):
        self.api_base = "https://www.kaggle.com/api/v1"
    def download_kaggle_dataset(self, dataset_name: str, output_dir: str = "kaggle_data"):
        try:
            import kaggle
            kaggle.api.dataset_download_files(dataset_name, path=output_dir, unzip=True)
            print(f"[OK] Kaggle veri seti indirildi: {dataset_name}")
            return True
        except ImportError:
            print("[UYARI] Kaggle API kurulu değil. pip install kaggle")
            return False
        except Exception as e:
            print(f"[ERR] Kaggle indirme hatası: {e}")
            return False
    def import_movies_from_csv(self, csv_path: str, db: Session, limit: int = None):
        try:
            df = pd.read_csv(csv_path, nrows=limit)
            imported = 0
            skipped = 0
            for _, row in df.iterrows():
                try:
                    mevcut = db.query(Icerik).filter(
                        Icerik.baslik == str(row.get('title', ''))
                    ).first()
                    if mevcut:
                        skipped += 1
                        continue
                    genres = row.get('genres', '')
                    if isinstance(genres, str):
                        try:
                            genres_json = json.loads(genres.replace("'", '"'))
                            kategori_list = [g.get('name', '') for g in genres_json if isinstance(g, dict)]
                            kategoriler = ', '.join(kategori_list) if kategori_list else None
                        except:
                            kategoriler = genres if genres else None
                    else:
                        kategoriler = None
                    poster_url = None
                    if pd.notna(row.get('poster_path')):
                        poster_path = str(row.get('poster_path', ''))
                        if poster_path and poster_path != 'nan':
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    ozet = row.get('overview', '') or row.get('description', '')
                    yil = None
                    if pd.notna(row.get('release_date')):
                        try:
                            yil = int(str(row.get('release_date', ''))[:4])
                        except:
                            pass
                    imdb_puani = None
                    if pd.notna(row.get('vote_average')):
                        try:
                            imdb_puani = float(row.get('vote_average', 0))
                        except:
                            pass
                    icerik = Icerik(
                        baslik=str(row.get('title', 'Unknown')),
                        tur='Film',
                        kategoriler=kategoriler,
                        ozet=ozet if ozet and len(ozet) > 10 else None,
                        yil=yil,
                        imdb_puani=imdb_puani,
                        poster_url=poster_url
                    )
                    db.add(icerik)
                    imported += 1
                    if imported % 100 == 0:
                        db.commit()
                        print(f"  {imported} film import edildi...")
                except Exception as e:
                    print(f"  Hata (satır {_ + 1}): {e}")
                    continue
            db.commit()
            print(f"[OK] {imported} film import edildi, {skipped} atlandı")
            return imported
        except Exception as e:
            db.rollback()
            print(f"[ERR] CSV import hatası: {e}")
            raise
    def import_tv_shows_from_csv(self, csv_path: str, db: Session, limit: int = None):
        try:
            df = pd.read_csv(csv_path, nrows=limit)
            imported = 0
            for _, row in df.iterrows():
                try:
                    mevcut = db.query(Icerik).filter(
                        Icerik.baslik == str(row.get('title', ''))
                    ).first()
                    if mevcut:
                        continue
                    genres = row.get('genres', '')
                    if isinstance(genres, str):
                        try:
                            genres_json = json.loads(genres.replace("'", '"'))
                            kategori_list = [g.get('name', '') for g in genres_json if isinstance(g, dict)]
                            kategoriler = ', '.join(kategori_list) if kategori_list else None
                        except:
                            kategoriler = genres if genres else None
                    else:
                        kategoriler = None
                    poster_url = None
                    if pd.notna(row.get('poster_path')):
                        poster_path = str(row.get('poster_path', ''))
                        if poster_path and poster_path != 'nan':
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    icerik = Icerik(
                        baslik=str(row.get('title', 'Unknown')),
                        tur='Dizi',
                        kategoriler=kategoriler,
                        ozet=row.get('overview', '') or row.get('description', ''),
                        yil=int(str(row.get('first_air_date', ''))[:4]) if pd.notna(row.get('first_air_date')) else None,
                        imdb_puani=float(row.get('vote_average', 0)) if pd.notna(row.get('vote_average')) else None,
                        poster_url=poster_url
                    )
                    db.add(icerik)
                    imported += 1
                    if imported % 100 == 0:
                        db.commit()
                        print(f"  {imported} dizi import edildi...")
                except Exception as e:
                    continue
            db.commit()
            print(f"[OK] {imported} dizi import edildi")
            return imported
        except Exception as e:
            db.rollback()
            print(f"[ERR] Dizi import hatası: {e}")
            raise
    def import_books_from_csv(self, csv_path: str, db: Session, limit: int = None):
        try:
            print(f"  CSV okunuyor: {csv_path}")
            df = pd.read_csv(csv_path, low_memory=False)
            if limit:
                df = df.head(limit)
            print(f"  Toplam {len(df)} satır bulundu")
            imported = 0
            skipped = 0
            for idx, row in df.iterrows():
                try:
                    title = str(row.get('title', '')).strip()
                    if not title or title == 'nan' or title == 'Unknown':
                        skipped += 1
                        continue
                    mevcut = db.query(Icerik).filter(
                        Icerik.baslik == title,
                        Icerik.tur == 'Kitap'
                    ).first()
                    if mevcut:
                        skipped += 1
                        continue
                    authors = str(row.get('authors', '')).strip() if pd.notna(row.get('authors')) else ''
                    kategoriler = ''
                    if pd.notna(row.get('publisher')):
                        kategoriler = str(row.get('publisher', ''))
                    ozet = f"Yazar: {authors}" if authors else "Kitap detayları"
                    if pd.notna(row.get('num_pages')):
                        ozet += f" | Sayfa: {int(row.get('num_pages', 0))}"
                    yil = None
                    if pd.notna(row.get('publication_date')):
                        try:
                            pub_date = str(row.get('publication_date', ''))
                            if '/' in pub_date:
                                parts = pub_date.split('/')
                                if len(parts) >= 3:
                                    yil = int(parts[-1])
                            elif '-' in pub_date:
                                yil = int(pub_date.split('-')[0])
                            else:
                                yil = int(pub_date[:4]) if len(pub_date) >= 4 else None
                        except:
                            pass
                    rating = None
                    if pd.notna(row.get('average_rating')):
                        try:
                            rating = float(row.get('average_rating', 0))
                            if rating > 0:
                                rating = rating * 2  
                        except:
                            pass
                    poster_url = None
                    if pd.notna(row.get('isbn')):
                        isbn = str(row.get('isbn', '')).strip()
                        if isbn:
                            poster_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
                    icerik = Icerik(
                        baslik=title,
                        tur='Kitap',
                        kategoriler=kategoriler,
                        ozet=ozet,
                        yil=yil if yil and yil > 1900 and yil < 2030 else None,
                        imdb_puani=rating if rating and rating > 0 else None,
                        poster_url=poster_url
                    )
                    db.add(icerik)
                    imported += 1
                    if imported % 500 == 0:
                        db.commit()
                        print(f"  {imported} kitap import edildi... (atlanan: {skipped})")
                except Exception as e:
                    skipped += 1
                    if imported % 1000 == 0:
                        print(f"  Hata (atlanan): {e}")
                    continue
            db.commit()
            print(f"[OK] {imported} kitap import edildi, {skipped} atlandı")
            return imported
        except Exception as e:
            db.rollback()
            print(f"[ERR] Kitap import hatası: {e}")
            import traceback
            traceback.print_exc()
            raise
    def create_large_dataset_from_kaggle(self, db: Session):
        print("=" * 60)
        print("KAGGLE VERİ SETİ İMPORT İŞLEMİ")
        print("=" * 60)
        print()
        try:
            import kaggle
            print("[OK] Kaggle API kurulu")
        except ImportError:
            print("[UYARI] Kaggle API kurulu değil!")
            print("Kurulum: pip install kaggle")
            print("Kaggle API key gerekli: ~/.kaggle/kaggle.json")
            return
        datasets = {
            : 'rounakbanik/the-movies-dataset',
            : 'shivamb/netflix-shows',
            : 'jealousleopard/goodreadsbooks'
        }
        for data_type, dataset_name in datasets.items():
            print(f"\n[{data_type.upper()}] {dataset_name} indiriliyor...")
            output_dir = f"kaggle_data/{data_type}"
            os.makedirs(output_dir, exist_ok=True)
            if self.download_kaggle_dataset(dataset_name, output_dir):
                csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                for csv_file in csv_files[:1]:  
                    csv_path = os.path.join(output_dir, csv_file)
                    print(f"  Import ediliyor: {csv_file}")
                    if data_type == 'movies':
                        self.import_movies_from_csv(csv_path, db, limit=None)
                    elif data_type == 'tv_shows':
                        self.import_tv_shows_from_csv(csv_path, db, limit=None)
                    elif data_type == 'books':
                        self.import_books_from_csv(csv_path, db, limit=5000)
        total = db.query(Icerik).count()
        print(f"\n[OK] Toplam {total} içerik veritabanında!")
def import_from_local_csv(csv_path: str, tur: str, db: Session, limit: int = None):
    importer = KaggleDataImporter()
    if tur.lower() == 'film':
        return importer.import_movies_from_csv(csv_path, db, limit)
    elif tur.lower() == 'dizi':
        return importer.import_tv_shows_from_csv(csv_path, db, limit)
    elif tur.lower() == 'kitap':
        return importer.import_books_from_csv(csv_path, db, limit)
    else:
        print(f"[ERR] Bilinmeyen tür: {tur}")
if __name__ == "__main__":
    print("=" * 60)
    print("KAGGLE VERİ SETİ İMPORT SCRIPTİ")
    print("=" * 60)
    print()
    init_db()
    db = SessionLocal()
    try:
        print("Import yöntemini seçin:")
        print("1. Kaggle API ile otomatik indir ve import et")
        print("2. Yerel CSV dosyasından import et")
        choice = input("\nSeçiminiz (1-2): ").strip()
        if choice == "1":
            importer = KaggleDataImporter()
            importer.create_large_dataset_from_kaggle(db)
        elif choice == "2":
            csv_file = input("CSV dosya yolu: ").strip()
            tur = input("Tür (Film/Dizi/Kitap): ").strip()
            limit_input = input("Limit (boş bırakın = tümü): ").strip()
            limit = int(limit_input) if limit_input else None
            import_from_local_csv(csv_file, tur, db, limit)
        total_count = db.query(Icerik).count()
        film_count = db.query(Icerik).filter(Icerik.tur == 'Film').count()
        dizi_count = db.query(Icerik).filter(Icerik.tur == 'Dizi').count()
        kitap_count = db.query(Icerik).filter(Icerik.tur == 'Kitap').count()
        print(f"\n[INFO] Toplam içerik: {total_count}")
        print(f"  - Film: {film_count}")
        print(f"  - Dizi: {dizi_count}")
        print(f"  - Kitap: {kitap_count}")
    except Exception as e:
        print(f"[ERR] Hata: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()