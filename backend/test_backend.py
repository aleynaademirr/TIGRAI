import requests
import sys
def test_backend():
    base_url = "http://localhost:8000"
    print("=" * 60)
    print("BACKEND BAĞLANTI TESTİ")
    print("=" * 60)
    try:
        print("\n1. Ana endpoint testi...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✓ Backend çalışıyor!")
        else:
            print(f"   ✗ Beklenmeyen durum kodu: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Backend'e bağlanılamıyor!")
        print("   → Backend'i başlatın: venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return False
    try:
        print("\n2. İçerikler endpoint testi...")
        response = requests.get(f"{base_url}/api/icerikler?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {len(data)} içerik bulundu")
            if len(data) > 0:
                print(f"   → İlk içerik: {data[0].get('baslik', 'N/A')}")
        else:
            print(f"   ✗ Beklenmeyen durum kodu: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return False
    try:
        print("\n3. Kullanıcılar endpoint testi...")
        response = requests.get(f"{base_url}/api/kullanicilar", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {len(data)} kullanıcı bulundu")
        else:
            print(f"   ✗ Beklenmeyen durum kodu: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Hata: {e}")
        return False
    print("\n" + "=" * 60)
    print("✓ Tüm testler başarılı!")
    print("=" * 60)
    print("\nFlutter uygulaması için:")
    print("  - Android Emulator: http://10.0.2.2:8000")
    print("  - iOS Simulator: http://localhost:8000")
    print("  - Gerçek cihaz: http://[BILGISAYAR_IP]:8000")
    print("\nBilgisayar IP adresini öğrenmek için:")
    print("  Windows: ipconfig")
    print("  Mac/Linux: ifconfig veya ip addr")
    return True
if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)