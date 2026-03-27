from sqlalchemy import create_engine, text
from config import settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
def add_poster_url_column():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(icerikler)"))
            columns = [row[1] for row in result]
            if 'poster_url' not in columns:
                print("poster_url kolonu ekleniyor...")
                conn.execute(text("ALTER TABLE icerikler ADD COLUMN poster_url TEXT"))
                conn.commit()
                print("[OK] poster_url kolonu eklendi!")
            else:
                print("[INFO] poster_url kolonu zaten mevcut")
    except Exception as e:
        print(f"[ERR] Hata: {e}")
if __name__ == "__main__":
    add_poster_url_column()