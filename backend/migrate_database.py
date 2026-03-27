import sqlite3
import shutil
from datetime import datetime
def migrate_database():
    db_path = "recommendation_system.db"
    backup_path = f"recommendation_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print("=" * 60)
    print("VERİTABANI MİGRATION")
    print("=" * 60)
    print(f"\n[1/4] Veritabanı yedekleniyor: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print("✅ Yedek alındı!")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM icerikler")
    icerik_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM kullanicilar")
    user_count = cursor.fetchone()[0]
    print(f"\n[2/4] Mevcut veriler:")
    print(f"  - İçerik sayısı: {icerik_count}")
    print(f"  - Kullanıcı sayısı: {user_count}")
    print(f"\n[3/4] Kullanıcı tablosu güncelleniyor...")
    cursor.execute()
    cursor.execute("DROP TABLE kullanicilar")
    cursor.execute()
    cursor.execute()
    cursor.execute("DROP TABLE kullanicilar_temp")
    conn.commit()
    print("✅ Kullanıcı tablosu güncellendi!")
    cursor.execute("SELECT COUNT(*) FROM icerikler")
    final_icerik = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM kullanicilar")
    final_users = cursor.fetchone()[0]
    print(f"\n[4/4] Migration tamamlandı!")
    print(f"  - İçerik sayısı: {final_icerik} (korundu ✅)")
    print(f"  - Kullanıcı sayısı: {final_users}")
    print(f"\n⚠️  ÖNEMLİ: Eski kullanıcılar geçici email/şifre ile oluşturuldu.")
    print(f"   Kullanıcıların yeniden kayıt olması gerekiyor!")
    print(f"\n💾 Yedek dosya: {backup_path}")
    conn.close()
if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        print("Yedek dosyadan geri yükleyebilirsiniz.")