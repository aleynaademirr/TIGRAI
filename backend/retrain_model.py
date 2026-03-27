"""
ML modelini yeniden eğit (shuffle kaldırıldı)
"""
from database import SessionLocal
from ml_model import recommendation_engine

print("\n" + "="*60)
print("ML MODELİ YENİDEN EĞİTİLİYOR")
print("="*60)

db = SessionLocal()

# Modeli yeniden eğit
recommendation_engine.train(db)

db.close()

print("\n" + "="*60)
print("✅ MODEL YENİDEN EĞİTİLDİ!")
print("   Artık öneriler daha alakalı olacak")
print("="*60 + "\n")