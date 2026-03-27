import sys
import os
sys.path.append(os.getcwd())
try:
    from auth import hash_password, verify_password
except ImportError:
    print("auth.py bulunamadı!")
    sys.exit(1)
DB_PATH = "recommendation_system.db"
def simulate_auth():
    print("\n=== ŞİFRE GÜVENLİK SİMÜLASYONU ===\n")
    email = "guvenlik_demo@example.com"
    raw_password = "gizli_sifre_123"
    print(f"1. Kullanıcı Kayıt Oluyor")
    print(f"   Email: {email}")
    print(f"   Girilen Şifre: {raw_password}")
    hashed_password = hash_password(raw_password)
    print(f"   Sistem tarafından oluşturulan 'Hash': {hashed_password}")
    print(f"   (Bu karmaşık kod veritabanına yazılır)\n")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kullanicilar WHERE email = ?", (email,))
    cursor.execute(

        ("guvenlik_demo", email, hashed_password)
    )
    conn.commit()
    print("2. Veritabanına Kaydedildi [OK]")
    print("\n3. Veritabanı Kontrolü (Hacker gözüyle)")
    cursor.execute("SELECT email, password_hash FROM kullanicilar WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        db_email, db_hash = user
        print(f"   Veritabanında görünen: {db_hash}")
        if raw_password not in db_hash:
            print("   ✅ GÜVENLİ: Gerçek şifre ('gizli_sifre_123') burada GÖRÜNMÜYOR.")
        else:
            print("   ❌ RİSK: Şifre açıkça görünüyor!")
    print("\n4. Giriş Yapma Denemesi")
    print("   Kullanıcı şifresini giriyor: 'gizli_sifre_123'")
    is_valid = verify_password(raw_password, db_hash)
    if is_valid:
        print("   ✅ BAŞARILI: Sistem şifreyi doğruladı ve girişe izin verdi.")
    else:
        print("   ❌ BAŞARISIZ: Doğrulama hatası.")
    print("\n===========================================")
if __name__ == "__main__":
    simulate_auth()