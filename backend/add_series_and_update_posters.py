"""
Netflix'ten daha fazla dizi ekle ve tüm dizi/kitap posterlerini güncelle
"""
import pandas as pd
from database import SessionLocal, Icerik
import os
import random

def add_more_series():
    print("\n" + "="*60)
    print("NETFLIX'TEN DAHA FAZLA DİZİ EKLENİYOR")
    print("="*60)
    
    csv_path = 'netflix_titles.csv'
    if not os.path.exists(csv_path):
        print("❌ netflix_titles.csv bulunamadı!")
        return 0
    
    print(f"✅ CSV bulundu: {csv_path}")
    
   
    df = pd.read_csv(csv_path)
    print(f"✅ {len(df)} Netflix içeriği okundu")
    
  
    series_df = df[df['type'] == 'TV Show'].copy()
    print(f"✅ {len(series_df)} dizi bulundu")
    
    db = SessionLocal()
    
    
    existing_titles = set([s.baslik.lower() for s in db.query(Icerik).filter(Icerik.tur == 'Dizi').all()])
    print(f"✅ Veritabanında {len(existing_titles)} dizi var")
    
    added = 0
    for _, row in series_df.iterrows():
        title = str(row['title']).strip()
        
        
        if title.lower() not in existing_titles:
            # Kategorileri ayıkla
            categories = str(row.get('listed_in', 'Drama')).replace(',', ', ')
            
            # Yılı ayıkla
            year = None
            if pd.notna(row.get('release_year')):
                try:
                    year = int(row['release_year'])
                except:
                    pass
            
            # Özet
            description = str(row.get('description', ''))[:500] if pd.notna(row.get('description')) else ''
            
            # Rastgele IMDB puanı (7-9 arası)
            imdb_score = round(random.uniform(7.0, 9.0), 1)
            
            # Yeni dizi ekle
            new_series = Icerik(
                baslik=title,
                tur='Dizi',
                kategoriler=categories,
                ozet=description,
                yil=year,
                imdb_puani=imdb_score,
                poster_url=None  # Sonra güncellenecek
            )
            
            db.add(new_series)
            added += 1
            
            if added % 100 == 0:
                print(f"  📺 {added} yeni dizi eklendi...", end='\r')
            
            # 5000'e ulaşınca dur
            if added >= 5000:
                break
    
    db.commit()
    db.close()
    
    print(f"\n✅ {added} yeni dizi eklendi!")
    return added

def update_series_posters():
    print("\n" + "="*60)
    print("DİZİ POSTERLERİ GÜNCELLENİYOR")
    print("="*60)
    
    db = SessionLocal()
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').all()
    
    colors = ['1abc9c', '2ecc71', '3498db', '9b59b6', 'e74c3c', 'f39c12']
    updated = 0
    
    for s in series:
        if not s.poster_url or s.poster_url == 'null':
            # Başlığı URL-safe yap
            safe_title = s.baslik[:30].replace(' ', '+')
            color = random.choice(colors)
            s.poster_url = f"https://placehold.co/300x450/{color}/ffffff/png?text={safe_title}"
            updated += 1
            
            if updated % 100 == 0:
                print(f"  🎨 {updated} dizi posteri oluşturuldu...", end='\r')
    
    db.commit()
    db.close()
    
    print(f"\n✅ {updated} dizi posteri güncellendi!")
    return updated

def update_book_covers():
    print("\n" + "="*60)
    print("KİTAP KAPAKLARI GÜNCELLENİYOR")
    print("="*60)
    
    db = SessionLocal()
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').all()
    
    colors = ['e67e22', '2ecc71', '3498db', '9b59b6', 'e74c3c', 'f1c40f']
    updated = 0
    
    for book in books:
        if not book.poster_url or book.poster_url == 'null':
            # Başlığı URL-safe yap
            safe_title = book.baslik[:30].replace(' ', '+')
            color = random.choice(colors)
            book.poster_url = f"https://placehold.co/300x450/{color}/ffffff/png?text={safe_title}"
            updated += 1
            
            if updated % 100 == 0:
                print(f"  📚 {updated} kitap kapağı oluşturuldu...", end='\r')
    
    db.commit()
    db.close()
    
    print(f"\n✅ {updated} kitap kapağı güncellendi!")
    return updated

def main():
    print("\n" + "="*70)
    print("  DİZİ EKLEME VE POSTER/KAPAK GÜNCELLEME")
    print("="*70)
    
    total_added = add_more_series()
    total_series_posters = update_series_posters()
    total_book_covers = update_book_covers()
    
    print("\n" + "="*70)
    print("  TAMAMLANDI!")
    print(f"  ✅ {total_added} yeni dizi eklendi")
    print(f"  ✅ {total_series_posters} dizi posteri güncellendi")
    print(f"  ✅ {total_book_covers} kitap kapağı güncellendi")
    print("="*70 + "\n")
    
    # Yeni sayıları göster
    from database import SessionLocal, Icerik
    db = SessionLocal()
    print("YENİ İÇERİK SAYILARI:")
    print(f"📽️  Filmler: {db.query(Icerik).filter(Icerik.tur == 'Film').count()}")
    print(f"📺 Diziler: {db.query(Icerik).filter(Icerik.tur == 'Dizi').count()}")
    print(f"📚 Kitaplar: {db.query(Icerik).filter(Icerik.tur == 'Kitap').count()}")
    print(f"📊 TOPLAM: {db.query(Icerik).count()}")
    db.close()

if __name__ == "__main__":
    main()
