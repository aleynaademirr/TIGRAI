import pandas as pd
from database import SessionLocal, Icerik
from sqlalchemy import func
import os

def update_imdb_scores():
    print("="*60)
    print("IMDB PUANLARI GÜNCELLENİYOR (Movie_data.csv)")
    print("="*60)
    
    csv_path = "../Movie_data.csv"
    if not os.path.exists(csv_path):
        print(f"❌ '{csv_path}' bulunamadı!")
        return

    try:
        # Pandas ile oku (Encoding hatası için try-except)
        try:
            df = pd.read_csv(csv_path, usecols=['movie_title', 'imdb_score'], encoding='utf-8')
        except UnicodeDecodeError:
            print("⚠️ UTF-8 okunamadı, ISO-8859-1 deneniyor...")
            df = pd.read_csv(csv_path, usecols=['movie_title', 'imdb_score'], encoding='ISO-8859-1')
            
        # Boşlukları temizle
        df['movie_title'] = df['movie_title'].str.strip()
        df = df.dropna()
        
        # Dictionary'e çevir: { "title_lower": score }
        # Aynı isimde birden fazla varsa, en yüksek puanlıyı alalım veya sonuncuyu.
        # Drop duplicates keeping last usually works fine or sort by something.
        # Basitçe dictionary yapalım.
        score_map = dict(zip(df['movie_title'].str.lower(), df['imdb_score']))
        
        print(f"✅ {len(score_map)} film puanı hafızaya alındı.")
        
        db = SessionLocal()
        movies = db.query(Icerik).filter(Icerik.tur == 'Film').all()
        
        updated_count = 0
        for movie in movies:
            title_lower = movie.baslik.strip().lower()
            if title_lower in score_map:
                new_score = float(score_map[title_lower])
                # Sadece puan farklıysa veya 0 ise güncelle
                if movie.imdb_puani != new_score:
                    movie.imdb_puani = new_score
                    updated_count += 1
        
        db.commit()
        db.close()
        print(f"\n✅ {updated_count} filmin IMDB puanı güncellendi!")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    update_imdb_scores()
