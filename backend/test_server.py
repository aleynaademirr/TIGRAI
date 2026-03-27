import requests
try:
    response = requests.get("http://localhost:8000/")
    print(f"✅ Sunucu çalışıyor! Status: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Sunucu çalışmıyor! Lütfen sunucuyu başlatın:")
    print("   cd backend")
    print("   .\\venv\\Scripts\\activate.bat")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
except Exception as e:
    print(f"❌ Hata: {e}")