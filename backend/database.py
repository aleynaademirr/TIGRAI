from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime, UniqueConstraint, func, case, and_, or_, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from datetime import datetime
try:
    from config import settings
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
except ImportError:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./recommendation_system.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    execution_options={"sqlite_foreign_keys": True} 
)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class Icerik(Base):
    __tablename__ = "icerikler"
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String, nullable=False, index=True)
    tur = Column(String, nullable=False, index=True)  
    kategoriler = Column(String)  
    ozet = Column(Text)  
    yil = Column(Integer)
    imdb_puani = Column(Float)  
    poster_url = Column(String)
    oy_sayisi = Column(Integer, default=0)
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    puanlar = relationship("Puan", back_populates="icerik")
    yorumlar = relationship("Yorum", back_populates="icerik")
    watchlist_items = relationship("Watchlist", back_populates="icerik")
class Kullanici(Base):
    __tablename__ = "kullanicilar"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_adi = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  
    is_admin = Column(Integer, default=0)  
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    puanlar = relationship("Puan", back_populates="kullanici")
    yorumlar = relationship("Yorum", back_populates="kullanici")
    reset_tokens = relationship("PasswordResetToken", back_populates="kullanici")
    watchlist = relationship("Watchlist", back_populates="kullanici")
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Integer, default=0)  
    created_at = Column(DateTime, default=datetime.utcnow)
    kullanici = relationship("Kullanici", back_populates="reset_tokens")
class Puan(Base):
    __tablename__ = "puanlar"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    icerik_id = Column(Integer, ForeignKey("icerikler.id"), nullable=False)
    puan = Column(Integer, nullable=False)  
    puanlama_tarihi = Column(DateTime, default=datetime.utcnow)
    kullanici = relationship("Kullanici", back_populates="puanlar")
    icerik = relationship("Icerik", back_populates="puanlar")
    __table_args__ = (
        UniqueConstraint('kullanici_id', 'icerik_id', name='unique_user_content_rating'),
    )
class Yorum(Base):
    __tablename__ = "yorumlar"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    icerik_id = Column(Integer, ForeignKey("icerikler.id"), nullable=False)
    yorum_metni = Column(Text, nullable=False)
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    kullanici = relationship("Kullanici", back_populates="yorumlar")
    icerik = relationship("Icerik", back_populates="yorumlar")
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_user = Column(Integer, default=1)  
    timestamp = Column(DateTime, default=datetime.utcnow)

class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"), nullable=False)
    icerik_id = Column(Integer, ForeignKey("icerikler.id"), nullable=False)
    eklenme_tarihi = Column(DateTime, default=datetime.utcnow)
    
    kullanici = relationship("Kullanici", back_populates="watchlist")
    icerik = relationship("Icerik", back_populates="watchlist_items")
    
    __table_args__ = (
        UniqueConstraint('kullanici_id', 'icerik_id', name='unique_user_watchlist'),
    )

def init_db():
    Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()