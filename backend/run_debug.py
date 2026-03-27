import debug_chatbot_full
import sys
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    original_stdout = sys.stdout
    sys.stdout = f
    try:
        debug_chatbot_full.test_chatbot()
    except Exception as e:
        print(e)
    finally:
        sys.stdout = original_stdout
print("Debug finished.")