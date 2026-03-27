import requests
import json

# Test the activity API endpoint
base_url = "http://172.20.10.6:8000"

print("=" * 60)
print("Testing Admin Activity API")
print("=" * 60)

try:
    print(f"\n1. Testing: {base_url}/admin/api/recent-activity")
    response = requests.get(f"{base_url}/admin/api/recent-activity", timeout=5)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Returned {len(data)} activities")
        
        if len(data) > 0:
            print("\n   First 3 activities:")
            for i, activity in enumerate(data[:3]):
                print(f"\n   Activity {i+1}:")
                print(f"      Type: {activity.get('type')}")
                print(f"      User: {activity.get('user')}")
                print(f"      Content: {activity.get('content')}")
                if activity.get('type') == 'comment':
                    print(f"      Text: {activity.get('text', '')[:50]}...")
                else:
                    print(f"      Rating: {activity.get('rating')}")
        else:
            print("   ⚠️  API returned empty list!")
    else:
        print(f"   ❌ Error! Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print(f"   ❌ Connection Error! Backend sunucusu çalışmıyor olabilir.")
    print(f"   Backend'i başlattın mı? (python main.py)")
except requests.exceptions.Timeout:
    print(f"   ❌ Timeout! Sunucu yanıt vermiyor.")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print("\n" + "=" * 60)
