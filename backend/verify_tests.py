import time
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, Puan, Icerik, Kullanici
def verify_integrity_test():
    db = SessionLocal()
    print("="*50)
    print("TEST SENARYOSU 1: VERİ BÜTÜNLÜĞÜ (Foreign Key)")
    print("="*50)
    invalid_id = 999999
    print(f"İşlem: ID={invalid_id} olan içeriğe puan verilmeye çalışılıyor...")
    try:
        new_puan = Puan(kullanici_id=1, icerik_id=invalid_id, puan=5)
        db.add(new_puan)
        db.commit()
        print("❌ HATA: Kısıtlama çalışmadı! Kayıt eklendi.")
    except IntegrityError as e:
        db.rollback()
        print("✅ BAŞARILI: Veritabanı bütünlük hatası döndürdü.")
        print(f"   Dönen Hata: {type(e).__name__}")
        print("   Mesaj: Foreign Key constraint failed")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Beklenmeyen Hata: {e}")
    finally:
        db.close()
def verify_performance_test():
    db = SessionLocal()
    print("\n" + "="*50)
    print("TEST SENARYOSU 2: PERFORMANS / YANIT SÜRESİ")
    print("="*50)
    start_time = time.time()
    count = db.query(Icerik).filter(Icerik.tur == 'Film').limit(50).all()
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    print(f"İşlem: 50 Film verisini veritabanından çekme")
    print(f"Süre: {duration_ms:.2f} ms")
    if duration_ms < 100:
        print("✅ SONUÇ: Mükemmel (100ms altı)")
    elif duration_ms < 500:
        print("✅ SONUÇ: İyi (500ms altı)")
    else:
        print("⚠️ SONUÇ: Yavaş")
    db.close()
if __name__ == "__main__":
    verify_integrity_test()
    verify_performance_test()