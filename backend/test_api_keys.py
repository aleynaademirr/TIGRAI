import os
import requests
from dotenv import load_dotenv
load_dotenv()
def test_tmdb_api():
    api_key = os.getenv("TMDB_API_KEY", "")
    print("=" * 60)
    print("TMDB API KEY TEST")
    print("=" * 60)
    if not api_key:
        print("❌ TMDB_API_KEY bulunamadı (.env dosyasında yok)")
        return False
    print(f"📝 API Key: {api_key[:8]}... (uzunluk: {len(api_key)} karakter)")
    if len(api_key) < 32:
        print("⚠️  UYARI: TMDB API key'leri genelde 32 karakter uzunluğunda!")
        print("   Eksik olabilir. Tam key'i kontrol edin.")
    print("\n🔍 Test ediliyor...")
    try:
        url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&query=Breaking+Bad"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                print("✅ TMDB API KEY ÇALIŞIYOR!")
                print(f"   Test sonucu: {data['results'][0]['name']} bulundu")
                return True
            else:
                print("⚠️  API çalışıyor ama sonuç bulunamadı")
                return True
        elif response.status_code == 401:
            print("❌ API KEY GEÇERSİZ!")
            print("   401 Unauthorized - Key yanlış veya eksik")
            return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"   Hata: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False
def test_omdb_api():
    api_key = os.getenv("OMDB_API_KEY", "")
    print("\n" + "=" * 60)
    print("OMDb API KEY TEST")
    print("=" * 60)
    if not api_key:
        print("❌ OMDB_API_KEY bulunamadı (.env dosyasında yok)")
        return False
    print(f"📝 API Key: {api_key[:8]}...")
    print("\n🔍 Test ediliyor...")
    try:
        url = f"http://www.omdbapi.com/?apikey={api_key}&t=Breaking+Bad&type=series"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                print("✅ OMDb API KEY ÇALIŞIYOR!")
                print(f"   Test sonucu: {data['Title']} bulundu")
                return True
            elif data.get("Error"):
                print(f"❌ API KEY GEÇERSİZ!")
                print(f"   Hata: {data['Error']}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False
if __name__ == "__main__":
    tmdb_ok = test_tmdb_api()
    omdb_ok = test_omdb_api()
    print("\n" + "=" * 60)
    print("SONUÇ")
    print("=" * 60)
    if tmdb_ok:
        print("✅ TMDB API kullanılabilir (update_series_tmdb.py)")
    else:
        print("❌ TMDB API kullanılamaz")
    if omdb_ok:
        print("✅ OMDb API kullanılabilir (update_series_omdb.py)")
    else:
        print("❌ OMDb API kullanılamaz")
    if not tmdb_ok and not omdb_ok:
        print("\n⚠️  HİÇBİR API ÇALIŞMIYOR!")
        print("   En az birini düzgün ayarlamanız gerekiyor.")
        print("\n📝 OMDb öneriyorum (daha kolay):")
        print("   http://www.omdbapi.com/apikey.aspx")