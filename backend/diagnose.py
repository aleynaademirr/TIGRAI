import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = "http://127.0.0.1:8000"
def run_diagnostics():
    print("=== TIGRAI DIAGNOSTIC TOOL ===\n")
    print("[1] Environment Viariables Check")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   [OK] GEMINI_API_KEY found: {api_key[:5]}...{api_key[-3:]}")
    else:
        print("   [ERROR] GEMINI_API_KEY NOT FOUND in environment!")
        print("   -> Chatbot will fail or use fallback.")
    print("\n" + "-"*30 + "\n")
    print("[2] API Poster URL Check (Home Feed)")
    try:
        r = requests.get(f"{BASE_URL}/api/icerikler?tur=Film&limit=3")
        if r.status_code == 200:
            items = r.json()
            print(f"   Fetched {len(items)} items from API.")
            for item in items:
                title = item.get('baslik', 'Unknown')
                poster = item.get('poster_url')
                print(f"   - {title}:  {poster[:50] if poster else 'NULL/NONE'}")
                if not poster or "placehold" in poster:
                     print("     [WARNING] Poster is missing or placeholder!")
        else:
            print(f"   [ERROR] Failed to fetch content: {r.status_code}")
    except Exception as e:
        print(f"   [CRITICAL] Could not connect to API: {e}")
    print("\n" + "-"*30 + "\n")
    print("[3] Forgot Password Response Check")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": "test@example.com"})
        print(f"   Status: {r.status_code}")
        print(f"   Response Body: {r.text}")
        if r.status_code == 200:
            print("   [OK] Endpoint works.")
        else:
            print("   [ERROR] Endpoint failed.")
    except Exception as e:
        print(f"   [CRITICAL] Connection failed: {e}")
    print("\n" + "-"*30 + "\n")
    print("[4] Chatbot Check")
    try:
        chat_body = {"message": "merhaba", "kullanici_id": 1}
        r = requests.post(f"{BASE_URL}/api/chatbot/sohbet", json=chat_body)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except Exception as e:
         print(f"   [CRITICAL] Connection failed: {e}")
if __name__ == "__main__":
    run_diagnostics()