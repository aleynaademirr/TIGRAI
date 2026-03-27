import pandas as pd
from database import SessionLocal, Icerik
import os

def update_book_covers():
    print("=" * 60)
    print("KİTAP KAPAKLARI GÜNCELLENİYOR (info.csv)")
    print("=" * 60)
    
    csv_path = "../info.csv"
    if not os.path.exists(csv_path):
        print("❌ info.csv bulunamadı!")
        return

    try:
        # Header'ı kontrol et
        df_head = pd.read_csv(csv_path, nrows=1)
        print("Kolonlar:", df_head.columns.tolist())
        
        # 'image_url' veya 'url' içeren kolonu bul
        img_col = None
        for col in df_head.columns:
            if 'image' in col.lower() or 'url' in col.lower():
                img_col = col
                break
        
        if not img_col:
            print("❌ Resim kolonu bulunamadı!")
            return
            
        print(f"✅ Resim kolonu bulundu: {img_col}")
        
        # Veriyi oku
        df = pd.read_csv(csv_path, usecols=['original_title', img_col])
        df = df.dropna()
        df['original_title'] = df['original_title'].str.strip()
        
        # Map: title -> url
        cover_map = dict(zip(df['original_title'].str.lower(), df[img_col]))
        
        print(f"✅ {len(cover_map)} kitap kapağı hafızaya alındı.")
        
        db = SessionLocal()
        books = db.query(Icerik).filter(Icerik.tur == 'Kitap').all()
        
        updated = 0
        for book in books:
            title_lower = book.baslik.strip().lower()
            if title_lower in cover_map:
                url = cover_map[title_lower]
                if url and len(url) > 10:
                    book.poster_url = url
                    updated += 1
        
        db.commit()
        db.close()
        print(f"\n✅ {updated} kitap kapağı güncellendi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    update_book_covers()
