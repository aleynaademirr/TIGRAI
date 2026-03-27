import json
BASE_URL = "http://127.0.0.1:8000"
def test_forgot_password():
    print("\n=== ŞİFREMİ UNUTTUM TESTİ ===\n")
    email = "test@example.com"
    print(f"1. İstek gönderiliyor: {email}")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": email})
        print(f"   Durum Kodu: {r.status_code}")
        print(f"   Cevap: {r.text}")
        if r.status_code == 200:
            data = r.json()
            print("\n   [BAŞARILI] Backend onayı verdi.")
            print(f"   Mesaj: '{data.get('message')}'")
            print("   (Mobil ekranda bu mesaj görünecek)")
            print("\n   [LOG KONTROLÜ] Backend konsolunda token görünmeli...")
            print("   Çünkü email ayarları henüz yapılmadı, sistem 'mock' modunda çalışıyor.")
        else:
            print("   [HATA] Beklenmedik durum.")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
if __name__ == "__main__":
    test_forgot_password()