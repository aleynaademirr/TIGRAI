import os
import pandas as pd
from sqlalchemy import create_engine
from database import Base, Icerik, Kullanici, Puan
SOURCE_URL = os.getenv("SOURCE_URL", "sqlite:///./recommendation_system.db")
TARGET_MSSQL_URL = os.getenv(


)
TABLES = ["icerikler", "kullanicilar", "puanlar"]
def migrate():
    src_engine = create_engine(SOURCE_URL)
    dst_engine = create_engine(TARGET_MSSQL_URL, fast_executemany=True)
    Base.metadata.create_all(bind=dst_engine)
    for table in TABLES:
        print(f"[+] {table} tablosu okunuyor...")
        df = pd.read_sql_table(table_name=table, con=src_engine)
        if df.empty:
            print(f"[-] {table} boş, atlanıyor.")
            continue
        print(f"[+] {table} MSSQL'e yazılıyor... ({len(df)} satır)")
        df.to_sql(
            name=table,
            con=dst_engine,
            if_exists="append",
            index=False,
            method=None,  
            chunksize=500,
        )
        print(f"[✓] {table} tamamlandı.")
    print("Tüm tablolar taşındı.")
if __name__ == "__main__":
    migrate()