"""
Admin aktivite için örnek veri oluştur
"""
from database import SessionLocal, Kullanici, Icerik, Puan, Yorum
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Admin kullanıcıyı al
admin = db.query(Kullanici).filter(Kullanici.is_admin == 1).first()
if not admin:
    print("❌ Admin kullanıcı bulunamadı!")
    exit()

# Test kullanıcıyı al veya oluştur
test_user = db.query(Kullanici).filter(Kullanici.kullanici_adi == 'test_user').first()
if not test_user:
    from auth import hash_password
    test_user = Kullanici(
        kullanici_adi='test_user',
        email='test@tigrai.com',
        password_hash=hash_password('test123')
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

# Rastgele 10 film al
filmler = db.query(Icerik).filter(Icerik.tur == 'Film').limit(10).all()

print("\n" + "="*60)
print("ÖRNEK AKTİVİTE VERİLERİ OLUŞTURULUYOR")
print("="*60)

# Puanlar ekle
print("\n📊 Puanlar ekleniyor...")
for i, film in enumerate(filmler[:5]):
    try:
        puan = Puan(
            kullanici_id=test_user.id,
            icerik_id=film.id,
            puan=random.randint(7, 10),
            puanlama_tarihi=datetime.now() - timedelta(days=i)
        )
        db.add(puan)
        print(f"  ✅ {film.baslik} - {puan.puan}/10")
    except:
        pass

db.commit()

# Yorumlar ekle
print("\n💬 Yorumlar ekleniyor...")
yorumlar = [
    "Harika bir film! Kesinlikle izlenmeli.",
    "Çok etkileyici bir hikaye. Beğendim.",
    "Görsel efektler muhteşem!",
    "Oyunculuklar çok başarılı.",
    "Müzikleri de çok güzel."
]

for i, film in enumerate(filmler[:5]):
    try:
        yorum = Yorum(
            kullanici_id=test_user.id,
            icerik_id=film.id,
            yorum_metni=yorumlar[i],
            olusturma_tarihi=datetime.now() - timedelta(hours=i*2)
        )
        db.add(yorum)
        print(f"  ✅ {film.baslik}")
    except:
        pass

db.commit()
db.close()

print("\n" + "="*60)
print("✅ TAMAMLANDI!")
print("   📊 5 puan eklendi")
print("   💬 5 yorum eklendi")
print("="*60 + "\n")
print("Admin panelindeki 'Aktivite' sekmesini kontrol edin!")
