from chatbot_service import chatbot_service
def test_chatbot():
    db = SessionLocal()
    try:
        msg1 = "Komedi filmi öner"
        print(f"User: {msg1}")
        resp1 = chatbot_service.process_message(msg1, 1, db)
        print(f"Bot: {resp1.get('response')}")
        print("-" * 20)
        msg2 = "Canım sıkkın"
        print(f"User: {msg2}")
        resp2 = chatbot_service.process_message(msg2, 1, db)
        print(f"Bot: {resp2.get('response')}")
        print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
if __name__ == "__main__":
    test_chatbot()