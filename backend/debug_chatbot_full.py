import sys
import logging
from database import SessionLocal
from chatbot_service import chatbot_service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot_debug")
def test_chatbot():
    db = SessionLocal()
    user_id = 1 
    test_inputs = [







    ]
    print("\n" + "="*50)
    print("CHATBOT DEBUG SESSION")
    print("="*50 + "\n")
    for msg in test_inputs:
        print(f"TEST INPUT: '{msg}'")
        try:
            intent = chatbot_service._detect_intent(msg)
            print(f"  -> Detected Intent: {intent}")
            content = chatbot_service._extract_content_name(msg, db)
            if content:
                print(f"  -> Extracted Content: {content.baslik}")
            else:
                print("  -> No Content Extracted")
            response = chatbot_service.process_message(msg, user_id, db)
            print(f"  -> RESPONSE TYPE: {response.get('response_type')}")
            print(f"  -> TEXT: {response.get('bot_response')}")
            if response.get('recommended_content'):
                print(f"  -> REC: {response['recommended_content']['baslik']}")
        except Exception as e:
            print(f"  -> ERROR: {e}")
            import traceback
            traceback.print_exc()
        print("-" * 30)
    db.close()
if __name__ == "__main__":
    test_chatbot()