import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, ChatHistory, Kullanici
from chatbot_service import chatbot_service
def verify_memory():
    print("Starting verification...")
    db = SessionLocal()
    try:
        user = db.query(Kullanici).filter(Kullanici.email == "test_memory@tigrai.com").first()
        if not user:
            print("Creating test user...")
            user = Kullanici(kullanici_adi="MemoryTester", email="test_memory@tigrai.com", password_hash="dummy")
            db.add(user)
            db.commit()
        user_id = user.id
        print(f"Test User ID: {user_id}")
        db.query(ChatHistory).filter(ChatHistory.kullanici_id == user_id).delete()
        db.commit()
        print("Cleared previous history.")
        print("\n--- Sending Message 1 ---")
        msg1 = "Merhaba, benim adım TIGRAI_TESTER. Bunu unutma."
        resp1 = chatbot_service.process_message(msg1, user_id, db)
        print(f"Bot Response 1: {resp1.get('bot_response')}")
        print("\n--- Sending Message 2 (Memory Check) ---")
        msg2 = "Benim adım ne? Az önce söylemiştim."
        resp2 = chatbot_service.process_message(msg2, user_id, db)
        print(f"Bot Response 2: {resp2.get('bot_response')}")
        history = db.query(ChatHistory).filter(ChatHistory.kullanici_id == user_id).all()
        print(f"\n--- Database Verification ---")
        print(f"Total History Entries: {len(history)} (Expected 4: 2 User + 2 Bot)")
        for h in history:
            role = "User" if h.is_user else "Bot"
            print(f"{role}: {h.message}")
        if "TIGRAI_TESTER" in resp2.get('bot_response', ''):
             print("\n✅ MEMORY TEST PASSED! Bot remembered the name.")
        else:
             print("\n⚠️ MEMORY TEST RESULT UNCERTAIN (Check logs above)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
if __name__ == "__main__":
    verify_memory()