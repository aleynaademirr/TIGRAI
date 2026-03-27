import sqlite3
import pandas as pd
def check_users():
    try:
        conn = sqlite3.connect('recommendation_system.db')
        df = pd.read_sql_query("SELECT id, kullanici_adi, email, password_hash FROM kullanicilar", conn)
        conn.close()
        print("\n--- KAYITLI KULLANICILAR ---")
        if df.empty:
            print("❌ HİÇ KULLANICI YOK! (Lütfen 'Kayıt Ol' ekranını kullanın)")
        else:
            print(df)
            print(f"\nToplam {len(df)} kullanıcı var.")
    except Exception as e:
        print(f"Hata: {e}")
if __name__ == "__main__":
    check_users()