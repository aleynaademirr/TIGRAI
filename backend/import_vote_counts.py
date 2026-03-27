import pandas as pd
from database import SessionLocal, Icerik
import os
import time

def import_vote_data():
    print("=" * 60)
    print("VOTE DATA IMPORT (movies_metadata.csv)")
    print("=" * 60)
    
    csv_path = "movies_metadata.csv"
    if not os.path.exists(csv_path):
        print("❌ CSV bulunamadı!")
        return

    try:
        # Sadece gerekli kolonları oku
        print("CSV okunuyor...")
        df = pd.read_csv(csv_path, usecols=['title', 'vote_count', 'vote_average'], low_memory=False)
        
        # Sayısal değerlere çevir (hatalı satırları temizle)
        df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').fillna(0).astype(int)
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0.0)
        
        # Title temizliği
        df = df.dropna(subset=['title'])
        df['title'] = df['title'].astype(str).str.strip()
        
        # Map oluştur
        # Key: lowercase title -> Value: (vote_count, vote_average)
        # Duplicate varsa en çok oyu alanı alalım
        df = df.sort_values('vote_count', ascending=False).drop_duplicates('title')
        
        vote_map = dict(zip(
            df['title'].str.lower(), 
            zip(df['vote_count'], df['vote_average'])
        ))
        
        print(f"✅ {len(vote_map)} film verisi hazırlandı.")
        
        db = SessionLocal()
        movies = db.query(Icerik).filter(Icerik.tur == 'Film').all()
        
        updated_count = 0
        for movie in movies:
            title_lower = movie.baslik.strip().lower()
            if title_lower in vote_map:
                count, avg = vote_map[title_lower]
                
                # Update logic
                movie.oy_sayisi = int(count)
                
                # Eğer vote_count < 10 ise puanı 0 yapabiliriz (opsiyonel)
                # Ama şimdilik sadece count'u kaydedelim, sıralamayı backend yapacak.
                
                # Mevcut puan 0 ise veya çok düşük oylu ise güncelle
                if movie.imdb_puani == 0 or movie.imdb_puani is None:
                    movie.imdb_puani = float(avg)
                
                updated_count += 1
                
                if updated_count % 1000 == 0:
                    print(f"  Güncellendi: {updated_count}...", end='\r')
        
        db.commit()
        db.close()
        print(f"\n✅ Toplam {updated_count} filmin oy sayısı güncellendi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    import_vote_data()
