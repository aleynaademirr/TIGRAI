"""
Sadece dizi ve kitap posterlerini güncelle
"""
from database import SessionLocal, Icerik
import random
import urllib.parse

def update_all_posters():
    print("\n" + "="*60)
    print("DİZİ VE KİTAP POSTERLERİ GÜNCELLENİYOR")
    print("="*60)
    
    db = SessionLocal()
    
    # Diziler
    print("\n📺 Diziler güncelleniyor...")
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').all()
    colors = ['1abc9c', '2ecc71', '3498db', '9b59b6', 'e74c3c', 'f39c12', '16a085', '27ae60']
    
    series_updated = 0
    for s in series:
        safe_title = urllib.parse.quote(s.baslik[:30])
        color = random.choice(colors)
        s.poster_url = f"https://placehold.co/300x450/{color}/ffffff/png?text={safe_title}"
        series_updated += 1
        
        if series_updated % 200 == 0:
            print(f"  {series_updated}/{len(series)} dizi güncellendi...", end='\r')
    
    print(f"\n✅ {series_updated} dizi posteri güncellendi!")
    
    # Kitaplar
    print("\n📚 Kitaplar güncelleniyor...")
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').all()
    book_colors = ['e67e22', '2ecc71', '3498db', '9b59b6', 'e74c3c', 'f1c40f', 'd35400', 'c0392b']
    
    books_updated = 0
    for book in books:
        safe_title = urllib.parse.quote(book.baslik[:30])
        color = random.choice(book_colors)
        book.poster_url = f"https://placehold.co/300x450/{color}/ffffff/png?text={safe_title}"
        books_updated += 1
        
        if books_updated % 500 == 0:
            print(f"  {books_updated}/{len(books)} kitap güncellendi...", end='\r')
    
    print(f"\n✅ {books_updated} kitap kapağı güncellendi!")
    
    # Kaydet
    db.commit()
    db.close()
    
    print("\n" + "="*60)
    print(f"✅ TOPLAM: {series_updated + books_updated} poster güncellendi!")
    print("="*60 + "\n")

if __name__ == "__main__":
    update_all_posters()
