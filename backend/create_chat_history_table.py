import sqlite3
import os
DB_PATH = "recommendation_system.db"
def create_chat_history_table():
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı bulunamadı: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute()
        cursor.execute()
        conn.commit()
        print("✅ 'chat_history' tablosu başarıyla oluşturuldu (veya zaten vardı).")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
    finally:
        conn.close()
if __name__ == "__main__":
    create_chat_history_table()