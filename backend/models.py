from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re
class IcerikBase(BaseModel):
    baslik: str
    tur: str  
    kategoriler: Optional[str] = None
    ozet: Optional[str] = None
    yil: Optional[int] = None
    imdb_puani: Optional[float] = None
    poster_url: Optional[str] = None
class IcerikCreate(IcerikBase):
    pass
class IcerikResponse(IcerikBase):
    id: int
    olusturma_tarihi: datetime
    class Config:
        from_attributes = True
class KullaniciBase(BaseModel):
    kullanici_adi: str
    email: str
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Geçerli bir email adresi giriniz')
        return v
class KullaniciCreate(KullaniciBase):
    password: str = Field(..., min_length=6, description="Şifre en az 6 karakter olmalıdır")
class KullaniciLogin(BaseModel):
    email: str
    password: str
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Geçerli bir email adresi giriniz')
        return v
class KullaniciResponse(KullaniciBase):
    id: int
    is_admin: bool = False
    olusturma_tarihi: datetime
    class Config:
        from_attributes = True
class AuthResponse(BaseModel):
    user: KullaniciResponse
    token: str
    message: str
class PuanBase(BaseModel):
    kullanici_id: int
    icerik_id: int
    puan: int = Field(..., ge=0, le=10, description="Puan 0-10 arası olmalıdır (0: Sadece İzlendi)")
class PuanCreate(PuanBase):
    pass
class PuanResponse(PuanBase):
    id: int
    puanlama_tarihi: datetime
    class Config:
        from_attributes = True
class OneriRequest(BaseModel):
    kullanici_id: int
    icerik_id: int
    puan: int = Field(..., ge=1, le=10)
class OneriResponse(BaseModel):
    oneriler: List[IcerikResponse]
    oneri_tipi: str  
    aciklama: str
class YorumBase(BaseModel):
    icerik_id: int
    yorum_metni: str = Field(..., min_length=1, max_length=1000)
class YorumCreate(YorumBase):
    kullanici_id: int 
class YorumResponse(YorumBase):
    id: int
    kullanici_id: int
    kullanici_adi: str 
    olusturma_tarihi: datetime
    class Config:
        from_attributes = True