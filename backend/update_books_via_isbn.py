from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import os
def update_book_covers():
    print("=== KITAP KAPAKLARI GÜNCELLENİYOR (ISBN BAZLI) ===")
    csv_path = "books.csv"
    if not os.path.exists(csv_path):
        for root, dirs, files in os.walk("."):
            if "books.csv" in files:
                csv_path = os.path.join(root, "books.csv")
                break
    if not os.path.exists(csv_path):
        print("❌ books.csv bulunamadı!")
        return
    print(f"📖 CSV Okunuyor: {csv_path}")
    try:
        df = pd.read_csv(csv_path, on_bad_lines='skip', low_memory=False)
        if 'title' not in df.columns or 'isbn' not in df.columns:
            print("❌ CSV formatı hatalı (title veya isbn sütunu yok)")
            return
        print(f"📦 Toplam {len(df)} satır işleniyor...")
        book_isbn_map = {}
        for _, row in df.iterrows():
            title = str(row['title']).strip().lower()
            isbn = str(row['isbn']).strip()
            if title and isbn and len(isbn) >= 10:
                book_isbn_map[title] = isbn
        print(f"🔍 {len(book_isbn_map)} eşsiz kitap ISBN bilgisi hazır.")
        db = SessionLocal()
        books = db.query(Icerik).filter(Icerik.tur == 'Kitap').all()
        updated_count = 0
        skipped_count = 0
        for book in books:
            current_url = book.poster_url or ""
            if "covers.openlibrary.org" in current_url:
                continue 
            title_key = book.baslik.strip().lower()
            if title_key in book_isbn_map:
                isbn = book_isbn_map[title_key]
                new_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                book.poster_url = new_url
                updated_count += 1
            else:
                skipped_count += 1
            if updated_count % 100 == 0:
                print(f"  Güncellenen: {updated_count}...", end='\r')
        db.commit()
        db.close()
        print(f"\n✅ TAMAMLANDI!")
        print(f"   Güncellenen Kitap Sayısı: {updated_count}")
        print(f"   Eşleşemeyen (Placeholder kaldı): {skipped_count}")
    except Exception as e:
        print(f"❌ HATA: {e}")
if __name__ == "__main__":
    update_book_covers()