from database import engine, SessionLocal
from sqlalchemy import text
import sys

def migrate_vote_count():
    print("=" * 60)
    print("MIGRATION: oy_sayisi kolonu ekleniyor...")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(icerikler)"))
            columns = [row[1] for row in result]
            
            if 'oy_sayisi' in columns:
                print("⚠️ 'oy_sayisi' kolonu zaten var.")
            else:
                conn.execute(text("ALTER TABLE icerikler ADD COLUMN oy_sayisi INTEGER DEFAULT 0"))
                print("✅ 'oy_sayisi' kolonu başarıyla eklendi.")
                
            conn.commit()
            
    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_vote_count()
