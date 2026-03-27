import sys
import os
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, ChatHistory, Icerik, engine
from chatbot_service import chatbot_service
from rag_service import is_rag_available
def check_database():
    print("\n[1/4] Checking Database...")
    try:
        with engine.connect() as conn:
            print("  ✅ Database Connection Successful")
        db = SessionLocal()
        content_count = db.query(Icerik).count()
        print(f"  ✅ 'icerikler' table accessed. Total content: {content_count}")
        history_count = db.query(ChatHistory).count()
        print(f"  ✅ 'chat_history' table accessed. Total history: {history_count}")
        db.close()
        return True
    except Exception as e:
        print(f"  ❌ Database Error: {e}")
        return False
def check_rag():
    print("\n[2/4] Checking RAG System...")
    try:
        if is_rag_available():
            print("  ✅ RAG Service is AVAILABLE")
            return True
        else:
            print("  ⚠️ RAG Service is NOT available (Vectors might need building)")
            return True 
    except Exception as e:
        print(f"  ❌ RAG Check Error: {e}")
        return False
def check_chatbot():
    print("\n[3/4] Checking Chatbot Logic...")
    try:
        db = SessionLocal()
        response = chatbot_service.process_message("Sistem kontrolü 1-2-3", 1, db)
        if response and response.get('bot_response'):
            print("  ✅ Chatbot responded successfully")
            print(f"  🤖 Logic Test Response: {response['bot_response'][:50]}...")
            return True
        else:
            print("  ❌ Chatbot returned empty response")
            return False
    except Exception as e:
        print(f"  ❌ Chatbot Logic Error: {e}")
        return False
    finally:
        db.close()
def main():
    print("🚀 STARTING FULL SYSTEM DIAGNOSTIC\n" + "="*40)
    db_ok = check_database()
    rag_ok = check_rag()
    chat_ok = check_chatbot()
    print("\n" + "="*40)
    if db_ok and chat_ok:
        print("✅ SYSTEM READY! Backend seems healthy.")
    else:
        print("❌ SYSTEM ISSUES DETECTED. See logs above.")
if __name__ == "__main__":
    main()