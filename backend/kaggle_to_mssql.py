import pandas as pd
import pyodbc
import json
import os
from datetime import datetime
class KaggleToMSSQL:
    def __init__(self, server, database, username=None, password=None, trusted_connection=True):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.conn = None
    def connect(self):
        try:
            if self.trusted_connection:
                conn_str = (
                    f'DRIVER={ ODBC Driver 17 for SQL Server} ;'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'Trusted_Connection=yes;'
                )
            else:
                conn_str = (
                    f'DRIVER={ ODBC Driver 17 for SQL Server} ;'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password};'
                )
            self.conn = pyodbc.connect(conn_str)
            print(f"[OK] MS SQL Server'a bağlanıldı: {self.server}/{self.database}")
            return True
        except pyodbc.Error as e:
            print(f"[ERR] Bağlantı hatası: {e}")
            print("\n[İPUCU] ODBC Driver kurulu değilse:")
            print("  https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
            return False
    def close(self):
        if self.conn:
            self.conn.close()
            print("[OK] Bağlantı kapatıldı")
    def import_movies_from_csv(self, csv_path: str, limit: int = None):
        try:
            print(f"\n[FİLM] CSV okunuyor: {csv_path}")
            df = pd.read_csv(csv_path, low_memory=False)
            if limit:
                df = df.head(limit)
            print(f"  Toplam {len(df)} satır bulundu")
            cursor = self.conn.cursor()
            imported = 0
            skipped = 0
            for idx, row in df.iterrows():
                try:
                    baslik = str(row.get('title', 'Unknown')).strip()
                    if not baslik or baslik == 'nan':
                        skipped += 1
                        continue
                    cursor.execute(

                        (baslik,)
                    )
                    if cursor.fetchone()[0] > 0:
                        skipped += 1
                        continue
                    kategoriler = None
                    genres = row.get('genres', '')
                    if pd.notna(genres) and genres:
                        try:
                            genres_json = json.loads(str(genres).replace("'", '"'))
                            kategori_list = [g.get('name', '') for g in genres_json if isinstance(g, dict)]
                            kategoriler = ', '.join(kategori_list) if kategori_list else None
                        except:
                            kategoriler = str(genres)[:500] if len(str(genres)) > 0 else None
                    ozet = row.get('overview', '')
                    if pd.notna(ozet) and len(str(ozet)) > 10:
                        ozet = str(ozet)
                    else:
                        ozet = None
                    yil = None
                    if pd.notna(row.get('release_date')):
                        try:
                            yil = int(str(row.get('release_date', ''))[:4])
                            if yil < 1800 or yil > 2100:
                                yil = None
                        except:
                            pass
                    imdb_puani = None
                    if pd.notna(row.get('vote_average')):
                        try:
                            imdb_puani = float(row.get('vote_average', 0))
                            if imdb_puani < 0 or imdb_puani > 10:
                                imdb_puani = None
                        except:
                            pass
                    poster_url = None
                    if pd.notna(row.get('poster_path')):
                        poster_path = str(row.get('poster_path', ''))
                        if poster_path and poster_path != 'nan' and len(poster_path) > 0:
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    cursor.execute(, (baslik, 'Film', kategoriler, ozet, yil, imdb_puani, poster_url))
                    imported += 1
                    if imported % 100 == 0:
                        self.conn.commit()
                        print(f"  {imported} film import edildi...")
                except Exception as e:
                    skipped += 1
                    if imported % 500 == 0:
                        print(f"  Hata (satır {idx}): {e}")
                    continue
            self.conn.commit()
            print(f"[OK] {imported} film import edildi, {skipped} atlandı")
            return imported
        except Exception as e:
            self.conn.rollback()
            print(f"[ERR] Film import hatası: {e}")
            raise
    def import_tv_shows_from_csv(self, csv_path: str, limit: int = None):
        try:
            print(f"\n[DİZİ] CSV okunuyor: {csv_path}")
            df = pd.read_csv(csv_path, low_memory=False)
            if limit:
                df = df.head(limit)
            print(f"  Toplam {len(df)} satır bulundu")
            cursor = self.conn.cursor()
            imported = 0
            skipped = 0
            for idx, row in df.iterrows():
                try:
                    baslik = str(row.get('title', '') or row.get('name', 'Unknown')).strip()
                    if not baslik or baslik == 'nan':
                        skipped += 1
                        continue
                    cursor.execute(

                        (baslik,)
                    )
                    if cursor.fetchone()[0] > 0:
                        skipped += 1
                        continue
                    kategoriler = None
                    if pd.notna(row.get('listed_in')):
                        kategoriler = str(row.get('listed_in', ''))[:500]
                    elif pd.notna(row.get('genres')):
                        kategoriler = str(row.get('genres', ''))[:500]
                    ozet = row.get('description', '') or row.get('overview', '')
                    if pd.notna(ozet) and len(str(ozet)) > 10:
                        ozet = str(ozet)
                    else:
                        ozet = None
                    yil = None
                    release_year = row.get('release_year', '') or row.get('first_air_date', '')
                    if pd.notna(release_year):
                        try:
                            yil = int(str(release_year)[:4])
                            if yil < 1800 or yil > 2100:
                                yil = None
                        except:
                            pass
                    imdb_puani = None
                    if pd.notna(row.get('vote_average')):
                        try:
                            imdb_puani = float(row.get('vote_average', 0))
                            if imdb_puani < 0 or imdb_puani > 10:
                                imdb_puani = None
                        except:
                            pass
                    poster_url = None
                    if pd.notna(row.get('poster_path')):
                        poster_path = str(row.get('poster_path', ''))
                        if poster_path and poster_path != 'nan':
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    cursor.execute(, (baslik, 'Dizi', kategoriler, ozet, yil, imdb_puani, poster_url))
                    imported += 1
                    if imported % 100 == 0:
                        self.conn.commit()
                        print(f"  {imported} dizi import edildi...")
                except Exception as e:
                    skipped += 1
                    continue
            self.conn.commit()
            print(f"[OK] {imported} dizi import edildi, {skipped} atlandı")
            return imported
        except Exception as e:
            self.conn.rollback()
            print(f"[ERR] Dizi import hatası: {e}")
            raise
    def import_books_from_csv(self, csv_path: str, limit: int = None):
        try:
            print(f"\n[KİTAP] CSV okunuyor: {csv_path}")
            df = pd.read_csv(csv_path, low_memory=False)
            if limit:
                df = df.head(limit)
            print(f"  Toplam {len(df)} satır bulundu")
            cursor = self.conn.cursor()
            imported = 0
            skipped = 0
            for idx, row in df.iterrows():
                try:
                    baslik = str(row.get('title', 'Unknown')).strip()
                    if not baslik or baslik == 'nan':
                        skipped += 1
                        continue
                    cursor.execute(

                        (baslik,)
                    )
                    if cursor.fetchone()[0] > 0:
                        skipped += 1
                        continue
                    authors = str(row.get('authors', '')).strip() if pd.notna(row.get('authors')) else ''
                    kategoriler = None
                    if pd.notna(row.get('publisher')):
                        kategoriler = str(row.get('publisher', ''))[:500]
                    ozet = f"Yazar: {authors}" if authors else "Kitap detayları"
                    if pd.notna(row.get('num_pages')):
                        try:
                            pages = int(row.get('num_pages', 0))
                            ozet += f" | Sayfa: {pages}"
                        except:
                            pass
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
                            if yil and (yil < 1800 or yil > 2100):
                                yil = None
                        except:
                            pass
                    imdb_puani = None
                    if pd.notna(row.get('average_rating')):
                        try:
                            rating = float(row.get('average_rating', 0))
                            if rating > 0:
                                imdb_puani = rating * 2  
                                if imdb_puani > 10:
                                    imdb_puani = 10.0
                        except:
                            pass
                    poster_url = None
                    if pd.notna(row.get('isbn')):
                        isbn = str(row.get('isbn', '')).strip()
                        if isbn and isbn != 'nan':
                            poster_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
                    cursor.execute(, (baslik, 'Kitap', kategoriler, ozet, yil, imdb_puani, poster_url))
                    imported += 1
                    if imported % 500 == 0:
                        self.conn.commit()
                        print(f"  {imported} kitap import edildi...")
                except Exception as e:
                    skipped += 1
                    continue
            self.conn.commit()
            print(f"[OK] {imported} kitap import edildi, {skipped} atlandı")
            return imported
        except Exception as e:
            self.conn.rollback()
            print(f"[ERR] Kitap import hatası: {e}")
            raise
    def get_statistics(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM icerikler")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT tur, COUNT(*) FROM icerikler GROUP BY tur")
            stats = cursor.fetchall()
            print("\n" + "=" * 60)
            print("VERİTABANI İSTATİSTİKLERİ")
            print("=" * 60)
            print(f"Toplam İçerik: {total}")
            for tur, count in stats:
                print(f"  - {tur}: {count}")
            print("=" * 60)
        except Exception as e:
            print(f"[ERR] İstatistik hatası: {e}")
def main():
    print("=" * 60)
    print("KAGGLE VERİLERİNİ MS SQL'E AKTARMA")
    print("=" * 60)
    print()
    print("MS SQL Server Bağlantı Bilgileri:")
    print("-" * 60)
    server = input("Server (örn: localhost): ").strip() or "localhost"
    database = input("Database (örn: OneriSistemi): ").strip() or "OneriSistemi"
    print("\nKimlik Doğrulama Yöntemi:")
    print("1. Windows Authentication (Trusted Connection)")
    print("2. SQL Server Authentication (Username/Password)")
    auth_choice = input("Seçim (1-2): ").strip()
    if auth_choice == "2":
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        importer = KaggleToMSSQL(server, database, username, password, trusted_connection=False)
    else:
        importer = KaggleToMSSQL(server, database, trusted_connection=True)
    if not importer.connect():
        return
    try:
        print("\n" + "=" * 60)
        print("CSV DOSYALARINI İMPORT ET")
        print("=" * 60)
        print("\n[1] FİLMLER")
        film_csv = input("Film CSV yolu (boş = atla): ").strip()
        if film_csv and os.path.exists(film_csv):
            limit = input("Limit (boş = tümü): ").strip()
            limit = int(limit) if limit else None
            importer.import_movies_from_csv(film_csv, limit)
        print("\n[2] DİZİLER")
        dizi_csv = input("Dizi CSV yolu (boş = atla): ").strip()
        if dizi_csv and os.path.exists(dizi_csv):
            limit = input("Limit (boş = tümü): ").strip()
            limit = int(limit) if limit else None
            importer.import_tv_shows_from_csv(dizi_csv, limit)
        print("\n[3] KİTAPLAR")
        kitap_csv = input("Kitap CSV yolu (boş = atla): ").strip()
        if kitap_csv and os.path.exists(kitap_csv):
            limit = input("Limit (boş = tümü, önerilen: 10000): ").strip()
            limit = int(limit) if limit else None
            importer.import_books_from_csv(kitap_csv, limit)
        importer.get_statistics()
        print("\n[OK] Import işlemi tamamlandı!")
    except Exception as e:
        print(f"\n[ERR] Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()
if __name__ == "__main__":
    main()