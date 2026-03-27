import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
import os
import urllib.parse
import random

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

PLACEHOLDER_COLORS = [
    '1abc9c', '2ecc71', '3498db', '9b59b6', '34495e',
    '16a085', '27ae60', '2980b9', '8e44ad', '2c3e50',
    'f1c40f', 'e67e22', 'e74c3c', '95a5a6', 'f39c12'
]

def update_movies():
    print("=" * 50)
    print("FİLM POSTERLERİ GÜNCELLENİYOR (Placeholder ile)...")
    print("=" * 50)
    
    # Dataset linkleri bozuk olduğu için (404), direkt placeholder kullanıyoruz.
    return _fill_placeholders('Film')

    # ESKİ KOD (CSV KONTROLÜ)
    """
    possible_paths = [
        'movies_metadata.csv',
        'backend/movies_metadata.csv',
        'kaggle_data/movies_metadata.csv',
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break
            
    if not csv_path:
        return _fill_placeholders('Film')
    
    # ... CSV logic skipped ...
    """


def update_series():
    print("\n" + "=" * 50)
    print("DİZİ POSTERLERİ GÜNCELLENİYOR...")
    print("=" * 50)
    return _fill_placeholders('Dizi')

def update_books():
    print("\n" + "=" * 50)
    print("KİTAP KAPAKLARI GÜNCELLENİYOR...")
    print("=" * 50)
    return _fill_placeholders('Kitap')

def _fill_placeholders(tur: str):
    print(f"[INFO] {tur} için placeholder kapaklar oluşturuluyor...")
    
    db = SessionLocal()
    items = db.query(Icerik).filter(Icerik.tur == tur).all()
    
    count = 0
    for item in items:
        current_url = item.poster_url or ""
        needs_update = (
            not current_url or
            current_url == "null" or
            "tmdb" in current_url or 
            len(current_url) < 10
        )
        
        if needs_update:
            safe_title = urllib.parse.quote(item.baslik[:30])
            bg_color = random.choice(PLACEHOLDER_COLORS)
            url = f"https://placehold.co/300x450/{bg_color}/ffffff/png?text={safe_title}"
            item.poster_url = url
            count += 1
    
    db.commit()
    db.close()
    print(f"[OK] {count} {tur} için placeholder oluşturuldu!")
    return count

def main():
    print("\n" + "=" * 60)
    print("   POSTER/KAPAK GÜNCELLEME BAŞLIYOR")
    print("=" * 60 + "\n")
    
    total = 0
    total += update_movies()
    total += update_series()
    total += update_books()
    
    print("\n" + "=" * 60)
    print(f"   TAMAMLANDI! Toplam {total} içerik güncellendi.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()