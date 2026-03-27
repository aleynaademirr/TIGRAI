"""
TMDB CSV'den TÜM film posterlerini güncelle
API limiti yok, çok hızlı!
"""
import pandas as pd
from database import SessionLocal, Icerik
import os

def update_all_movies_from_csv():
    print("\n" + "="*60)
    print("TMDB CSV'DEN TÜM FİLM POSTERLERİ GÜNCELLENİYOR")
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
    print("📖 CSV okunuyor...")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✅ {len(df)} film verisi okundu")
    
    # Sadece geçerli poster_path olanları al
    df = df[['title', 'poster_path']].dropna()
    df = df[df['poster_path'].str.startswith('/')]  # TMDB path'leri / ile başlar
    print(f"✅ {len(df)} filmde geçerli poster var")
    
    # Poster haritası oluştur (küçük harfe çevir)
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
    poster_dict = {}
    
    for _, row in df.iterrows():
        title = str(row['title']).lower().strip()
        path = str(row['poster_path']).strip()
        poster_dict[title] = f"{TMDB_IMAGE_BASE}{path}"
    
    print(f"✅ {len(poster_dict)} poster haritası oluşturuldu")
    
    # Veritabanını güncelle
    print("\n💾 Veritabanı güncelleniyor...")
    db = SessionLocal()
    
    # TÜM filmleri al
    all_movies = db.query(Icerik).filter(Icerik.tur == 'Film').all()
    print(f"✅ Veritabanında {len(all_movies)} film var")
    
    updated = 0
    not_found = 0
    
    for i, movie in enumerate(all_movies):
        title_lower = movie.baslik.lower().strip()
        
        if title_lower in poster_dict:
            movie.poster_url = poster_dict[title_lower]
            updated += 1
            
            if updated % 1000 == 0:
                print(f"  ✅ {updated} film güncellendi")
                db.commit()  # Her 1000'de bir kaydet
        else:
            not_found += 1
        
        # İlerleme göster
        if (i + 1) % 5000 == 0:
            print(f"  📊 İşlenen: {i+1}/{len(all_movies)}")
    
    # Son kayıt
    db.commit()
    db.close()
    
    print("\n" + "="*60)
    print("✅ TAMAMLANDI!")
    print(f"   ✅ {updated} film posteri güncellendi")
    print(f"   ⚠️  {not_found} film için poster bulunamadı")
    print(f"   📊 Başarı oranı: {updated/len(all_movies)*100:.1f}%")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_all_movies_from_csv()
