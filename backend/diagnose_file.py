import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = "http://127.0.0.1:8000"
def run_diagnostics():
    with open("diagnostic_results.txt", "w", encoding="utf-8") as f:
        f.write("=== TIGRAI DIAGNOSTIC RESULTS ===\n\n")
        f.write("[1] API KEY CHECK\n")
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            f.write(f"   [OK] Found: {api_key[:5]}...{api_key[-3:]}\n")
        else:
            f.write("   [ERROR] GEMINI_API_KEY NOT FOUND!\n")
        f.write("\n" + "-"*30 + "\n")
        f.write("[2] POSTER URL CHECK (API)\n")
        try:
            r = requests.get(f"{BASE_URL}/api/icerikler?tur=Film&limit=3")
            if r.status_code == 200:
                items = r.json()
                for item in items:
                    title = item.get('baslik', 'Unknown')
                    poster = item.get('poster_url')
                    f.write(f"   - {title}: {poster}\n")
            else:
                f.write(f"   [ERROR] Status: {r.status_code}\n")
        except Exception as e:
            f.write(f"   [CRITICAL] Connection failed: {e}\n")
        f.write("\n" + "-"*30 + "\n")
        f.write("[3] CHATBOT CHECK\n")
        try:
            r = requests.post(f"{BASE_URL}/api/chatbot/sohbet", json={"message": "merhaba", "kullanici_id": 1})
            f.write(f"   Status: {r.status_code}\n")
            f.write(f"   Body: {r.text}\n")
        except Exception as e:
             f.write(f"   [CRITICAL] Chatbot failed: {e}\n")
        f.write("\n" + "-"*30 + "\n")
        f.write("[4] FORGOT PASSWORD CHECK\n")
        try:
            r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": "test@example.com"})
            f.write(f"   Status: {r.status_code}\n")
            f.write(f"   Body: {r.text}\n")
        except Exception as e:
             f.write(f"   [CRITICAL] Auth failed: {e}\n")
if __name__ == "__main__":
    run_diagnostics()