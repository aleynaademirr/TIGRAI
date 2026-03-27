"""
TÜM POSTERLERİ SIFIRLA VE YENİDEN YÜKLE
"""
import pandas as pd
from database import SessionLocal, Icerik
import os

def force_update_posters():
    print("\n" + "="*60)
    print("TÜM POSTERLER YENİDEN YÜKLENİYOR (FORCE UPDATE)")
    print("="*60)
    
    # CSV dosyasını bul
    csv_path = 'movies_metadata.csv'
    if not os.path.exists(csv_path):
        csv_path = 'backend/movies_metadata.csv'
    if not os.path.exists(csv_path):
        print("❌ movies_metadata.csv bulunamadı!")
        return
    
    print(f"✅ CSV bulundu: {csv_path}")
    
    # CSV'yi oku
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✅ {len(df)} film verisi okundu")
    
    # Sadece geçerli poster_path olanları al
    df = df[['title', 'poster_path']].dropna()
    df = df[df['poster_path'].str.startswith('/')]
    print(f"✅ {len(df)} filmde geçerli poster var")
    
    # Poster haritası oluştur
    poster_dict = {}
    for _, row in df.iterrows():
        title = str(row['title']).lower().strip()
        path = str(row['poster_path']).strip()
        poster_dict[title] = f"https://image.tmdb.org/t/p/w500{path}"
    
    print(f"✅ {len(poster_dict)} poster haritası oluşturuldu")
    
    # Veritabanını güncelle
    db = SessionLocal()
    
    # Sadece filmleri al
    movies = db.query(Icerik).filter(Icerik.tur == 'Film').all()
    print(f"✅ Veritabanında {len(movies)} film var")
    
    updated = 0
    not_found = 0
    
    for movie in movies:
        title_lower = movie.baslik.lower().strip()
        
        if title_lower in poster_dict:
            movie.poster_url = poster_dict[title_lower]
            updated += 1
            if updated % 500 == 0:
                print(f"  📝 {updated} film güncellendi...", end='\r')
        else:
            not_found += 1
    
    # Değişiklikleri kaydet
    db.commit()
    db.close()
    
    print(f"\n✅ TAMAMLANDI!")
    print(f"   ✅ {updated} film posteri güncellendi")
    print(f"   ⚠️  {not_found} film için poster bulunamadı")
    print("="*60 + "\n")

if __name__ == "__main__":
    force_update_posters()
