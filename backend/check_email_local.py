import os
sys.path.append(os.getcwd())
try:
    from email_service import email_service
except ImportError:
    print("email_service.py bulunamadı!")
    sys.exit(1)
def simulate_email():
    print("\n=== EMAIL SİSTEMİ TEST SİMÜLASYONU ===\n")
    email = "deneme_hesabi@example.com"
    token = email_service.generate_reset_token()
    username = "DenemeKullanici"
    print(f"Senaryo: Kullanıcı '{email}' şifresini unuttu butonuna bastı.")
    print("Email servisi tetikleniyor...")
    success = email_service.send_password_reset_email(email, token, username)
    if success:
        print("\n✅ SONUÇ: BAŞARILI")
        print("   Sistem 'True' cevabını döndü.")
        print("   Bu, uygulamanın ekrana 'Başarılı' mesajı çıkarmasını sağlar.")
        print("\n[Konsol Çıktısı Analizi]")
        print(f"   Kod içinde görülen token: {token[:8].upper()}")
        print("   Sistem email ayarı bulamadığı için kodu buraya (sunucu ekranına) yazdı.")
        print("   Eğer email ayarı yapılsaydı, bu kod kullanıcının posta kutusuna gidecekti.")
    else:
        print("\n❌ SONUÇ: BAŞARISIZ")
if __name__ == "__main__":
    simulate_email()