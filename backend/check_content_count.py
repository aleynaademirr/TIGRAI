from database import SessionLocal, Icerik

db = SessionLocal()
print("\n" + "="*50)
print("MEVCUT İÇERİK SAYILARI")
print("="*50)
print(f"📽️  Filmler: {db.query(Icerik).filter(Icerik.tur == 'Film').count()}")
print(f"📺 Diziler: {db.query(Icerik).filter(Icerik.tur == 'Dizi').count()}")
print(f"📚 Kitaplar: {db.query(Icerik).filter(Icerik.tur == 'Kitap').count()}")
print(f"📊 TOPLAM: {db.query(Icerik).count()}")
print("="*50 + "\n")
db.close()
