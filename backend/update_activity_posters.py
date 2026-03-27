"""
Aktivitelerde kullanılan içeriklerin posterlerini OMDB ile güncelle
"""
import requests
from database import SessionLocal, Icerik, Yorum, Puan
import time
import os
from dotenv import load_dotenv
from sqlalchemy import or_

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '2a8a018c')
OMDB_URL = "http://www.omdbapi.com/"

def update_activity_posters():
    print("\n" + "="*60)
    print("AKTİVİTE İÇERİKLERİNİN POSTERLERİ GÜNCELLENİYOR")
    print("="*60)
    
    db = SessionLocal()
    
    # Aktivitelerde kullanılan içerik ID'lerini bul
    print("\n📊 Aktivitelerde kullanılan içerikler bulunuyor...")
    
    # Yorumlanan içerikler
    commented_ids = db.query(Yorum.icerik_id).distinct().all()
    commented_ids = [id[0] for id in commented_ids]
    
    # Puanlanan içerikler
    rated_ids = db.query(Puan.icerik_id).distinct().all()
    rated_ids = [id[0] for id in rated_ids]
    
    # Birleştir
    all_activity_ids = list(set(commented_ids + rated_ids))
    
    print(f"✅ {len(all_activity_ids)} farklı içerik bulundu")
    print(f"   💬 {len(commented_ids)} yorumlanan içerik")
    print(f"   ⭐ {len(rated_ids)} puanlanan içerik")
    
    # Bu içerikleri getir
    contents = db.query(Icerik).filter(Icerik.id.in_(all_activity_ids)).all()
    
    print(f"\n🔄 {len(contents)} içerik için gerçek posterler çekiliyor...\n")
    
    updated = 0
    failed = 0
    skipped = 0
    
    for i, content in enumerate(contents, 1):
        try:
            # Zaten gerçek poster varsa atla (placeholder değilse)
            if content.poster_url and 'placehold' not in content.poster_url.lower():
                skipped += 1
                continue
            
            # Türe göre OMDB'den çek
            content_type = 'movie' if content.tur == 'Film' else 'series' if content.tur == 'Dizi' else None
            
            if content_type:
                params = {
                    'apikey': OMDB_API_KEY,
                    't': content.baslik,
                    'type': content_type
                }
                
                response = requests.get(OMDB_URL, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                        old_url = content.poster_url
                        content.poster_url = data['Poster']
                        updated += 1
                        
                        icon = "📺" if content.tur == 'Dizi' else "🎬"
                        print(f"{icon} [{i}/{len(contents)}] {content.baslik[:40]:<40} ✅")
                    else:
                        failed += 1
                        print(f"⚠️  [{i}/{len(contents)}] {content.baslik[:40]:<40} (bulunamadı)")
                else:
                    failed += 1
            else:
                # Kitaplar için Google Books kullan
                if content.tur == 'Kitap':
                    params = {
                        'q': content.baslik,
                        'maxResults': 1,
                        'printType': 'books'
                    }
                    
                    response = requests.get('https://www.googleapis.com/books/v1/volumes', params=params, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('items'):
                            image_links = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
                            cover = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                            
                            if cover:
                                content.poster_url = cover.replace('http://', 'https://')
                                updated += 1
                                print(f"📚 [{i}/{len(contents)}] {content.baslik[:40]:<40} ✅")
                            else:
                                failed += 1
                        else:
                            failed += 1
                else:
                    skipped += 1
            
            # Rate limit için bekleme
            if i % 10 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            failed += 1
            print(f"❌ [{i}/{len(contents)}] {content.baslik[:40]:<40} (hata: {str(e)[:30]})")
            continue
    
    # Kaydet
    print("\n💾 Değişiklikler kaydediliyor...")
    db.commit()
    db.close()
    
    print("\n" + "="*60)
    print("✅ TAMAMLANDI!")
    print(f"   ✅ {updated} içerik güncellendi")
    print(f"   ⚠️  {failed} içerik bulunamadı")
    print(f"   ⏭️  {skipped} içerik zaten güncel")
    print(f"   📊 TOPLAM: {len(contents)} içerik işlendi")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_activity_posters()
