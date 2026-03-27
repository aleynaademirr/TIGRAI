import sqlite3
import json
BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "recommendation_system.db"
def test_auth():
    print("\n=== KULLANICI KAYIT VE GİRİŞ TESTİ ===\n")
    username = "guvenlik_test_user"
    email = "guvenlik_test@example.com"
    password = "guclu_sifre_123"
    print(f"1. Kayıt olunuyor: {email} / {password}")
    register_data = {
        : username,
        : email,
        : password
    }
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kullanicilar WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        r = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if r.status_code == 201:
            print("   [OK] Kayıt başarılı!")
        else:
            print(f"   [HATA] Kayıt başarısız: {r.text}")
            return
        print(f"\n2. Giriş yapılıyor: {email} / {password}")
        login_data = {
            : email,
            : password
        }
        r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if r.status_code == 200:
            print("   [OK] Giriş başarılı! Token alındı.")
        else:
            print(f"   [HATA] Giriş başarısız: {r.text}")
        print("\n3. Veritabanı Güvenlik Kontrolü")
        print("   Kullanıcı tablosundaki 'password_hash' sütunu okunuyor...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT kullanici_adi, password_hash FROM kullanicilar WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            db_user, db_hash = user
            print(f"   Kullanıcı: {db_user}")
            print(f"   Kayıtlı Şifre (DB): {db_hash}")
            if password not in db_hash:
                print("\n   [GÜVENLİ] Harika! Şifreniz açık şekilde SAKLANMIYOR.")
                print("   Veritabanında şifreli (hash) hali tutuluyor.")
                print("   Bu sayede veritabanı çalınsa bile şifreniz güvende.")
            else:
                print("\n   [RİSK] Şifre düz metin olarak saklanıyor!")
    except Exception as e:
        print(f"Test hatası: {e}")
        print("Backend çalışıyor mu kontrol edin!")
if __name__ == "__main__":
    test_auth()