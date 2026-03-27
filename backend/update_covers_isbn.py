import pandas as pd
from database import SessionLocal, Icerik
import os

def update_covers_isbn():
    print("=" * 60)
    print("ISBN İLE KİTAP KAPAKLARI GÜNCELLENİYOR (OpenLibrary)")
    print("=" * 60)
    
    csv_path = "books.csv"
    if not os.path.exists(csv_path):
        print("❌ books.csv bulunamadı!")
        return

    try:
        # Hatalı satırları atlayarak oku (on_bad_lines='skip' pandas sürümüne göre değişebilir, error_bad_lines daha eski)
        try:
            df = pd.read_csv(csv_path, on_bad_lines='skip', low_memory=False)
        except:
             df = pd.read_csv(csv_path, error_bad_lines=False, low_memory=False)

        print("Kolonlar:", df.columns.tolist())
        
        # Gerekli kolonlar var mı?
        # Genelde: title, isbn
        if 'title' not in df.columns or 'isbn' not in df.columns:
            print("❌ Gerekli kolonlar (title, isbn) bulunamadı.")
            return

        # Temizlik
        df['title'] = df['title'].astype(str).str.strip()
        df['isbn'] = df['isbn'].astype(str).str.strip()
        
        # Map: title -> isbn
        # Aynı isimli kitaplarda ilk ISBN'i al
        isbn_map = dict(zip(df['title'].str.lower(), df['isbn']))
        
        print(f"✅ {len(isbn_map)} kitap ISBN bilgisi hafızaya alındı.")
        
        db = SessionLocal()
        books = db.query(Icerik).filter(Icerik.tur == 'Kitap').all()
        
        updated = 0
        for book in books:
            title_lower = book.baslik.strip().lower()
            
            # Tam eşleşme ara
            if title_lower in isbn_map:
                isbn = isbn_map[title_lower]
                
                # ISBN varsa URL oluştur
                if isbn and len(isbn) > 5:
                    # OpenLibrary Cover URL
                    # Large size (-L)
                    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                    
                    # Mevcut URL placeholder ise VEYA info.csv'den gelen bozuk dosya yoluysa güncelle
                    current = book.poster_url
                    is_placeholder = not current or 'placehold' in current 
                    is_local_file = current and not current.startswith('http') # "439554934.jpg" gibi
                    
                    if is_placeholder or is_local_file:
                        book.poster_url = url
                        updated += 1
        
        db.commit()
        db.close()
        print(f"\n✅ {updated} kitap kapağı ISBN kullanılarak güncellendi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    update_covers_isbn()
