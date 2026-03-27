"""
Film posterlerini TMDB'den güncelle
"""
import pandas as pd
from database import SessionLocal, Icerik
import os

def update_all_posters():
    print("\n" + "="*60)
    print("POSTER GÜNCELLEME BAŞLIYOR")
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
    df = df[df['poster_path'].str.startswith('/')]  # TMDB path'leri / ile başlar
    print(f"✅ {len(df)} filmde geçerli poster var")
    
    # Poster haritası oluştur (küçük harfe çevir)
    poster_dict = {}
    for _, row in df.iterrows():
        title = str(row['title']).lower().strip()
        path = str(row['poster_path']).strip()
        poster_dict[title] = f"https://image.tmdb.org/t/p/w500{path}"
    
    print(f"✅ {len(poster_dict)} poster haritası oluşturuldu")
    
    # Veritabanını güncelle
    db = SessionLocal()
    
    # Tüm filmleri al
    all_content = db.query(Icerik).all()
    print(f"✅ Veritabanında {len(all_content)} içerik var")
    
    updated = 0
    for content in all_content:
        title_lower = content.baslik.lower().strip()
        
        # Eğer poster yoksa veya geçersizse
        if not content.poster_url or content.poster_url == 'null' or len(content.poster_url) < 10:
            # Haritada varsa güncelle
            if title_lower in poster_dict:
                content.poster_url = poster_dict[title_lower]
                updated += 1
                if updated % 100 == 0:
                    print(f"  📝 {updated} içerik güncellendi...", end='\r')
    
    # Değişiklikleri kaydet
    db.commit()
    db.close()
    
    print(f"\n✅ TAMAMLANDI! {updated} içerik güncellendi!")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_all_posters()
