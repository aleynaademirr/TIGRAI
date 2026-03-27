import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import os
import time
def update_book_covers_comprehensive():
    print("=" * 60)
    print("KİTAP KAPAKLARI GÜNCELLENİYOR (ISBN BAZLI)")
    print("=" * 60)
    csv_path = "books.csv"
    if not os.path.exists(csv_path):
        print(f"❌ {csv_path} bulunamadı!")
        return 0
    print(f"📖 CSV Okunuyor: {csv_path}")
    try:
        df = pd.read_csv(csv_path, on_bad_lines='skip', low_memory=False)
        if 'title' not in df.columns or 'isbn' not in df.columns:
            print("❌ CSV formatı hatalı (title veya isbn sütunu yok)")
            return 0
        print(f"📦 Toplam {len(df)} satır okundu")
        book_isbn_map = {}
        for _, row in df.iterrows():
            title = str(row['title']).strip().lower()
            isbn = str(row['isbn']).strip()
            if title and isbn and isbn != 'nan' and len(isbn) >= 10:
                book_isbn_map[title] = isbn
        print(f"🔍 {len(book_isbn_map)} kitap için ISBN bilgisi hazır")
        db = SessionLocal()
        books = db.query(Icerik).filter(
            Icerik.tur == 'Kitap',
            (Icerik.poster_url == None) | 
            (Icerik.poster_url.like('%placehold%')) |
            (Icerik.poster_url == '')
        ).all()
        print(f"📚 Güncellenecek {len(books)} kitap bulundu")
        updated_count = 0
        skipped_count = 0
        for idx, book in enumerate(books):
            title_key = book.baslik.strip().lower()
            if title_key in book_isbn_map:
                isbn = book_isbn_map[title_key]
                new_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                book.poster_url = new_url
                updated_count += 1
                if updated_count % 100 == 0:
                    db.commit()
                    print(f"  ✅ {updated_count} kitap güncellendi...", end='\r')
            else:
                skipped_count += 1
            if (idx + 1) % 500 == 0:
                progress = ((idx + 1) / len(books)) * 100
                print(f"  İlerleme: {progress:.1f}% ({idx + 1}/{len(books)})", end='\r')
        db.commit()
        db.close()
        print(f"\n\n{'=' * 60}")
        print("✅ GÜNCELLEME TAMAMLANDI!")
        print(f"   Güncellenen: {updated_count}")
        print(f"   Eşleşmeyen: {skipped_count}")
        print("=" * 60)
        return updated_count
    except Exception as e:
        print(f"❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        return 0
if __name__ == "__main__":
    update_book_covers_comprehensive()