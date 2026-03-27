from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from database import Base, engine, get_db, Icerik, Kullanici, Puan, Yorum, PasswordResetToken, Watchlist, init_db
from models import IcerikCreate
from models import IcerikResponse
from models import KullaniciCreate
from models import KullaniciResponse
from models import KullaniciLogin
from models import AuthResponse
from models import PuanCreate
from models import PuanResponse
from models import OneriRequest
from models import OneriResponse
from models import YorumCreate
from models import YorumResponse
from ml_model import recommendation_engine
from config import settings
from logger import logger
from sql_queries import AdvancedSQLQueries
from chatbot_service import chatbot_service
from gemini_chatbot import gemini_chatbot
from admin_routes import admin_router

app = FastAPI(
    title="Kişiselleştirilmiş İçerik Öneri Sistemi API",
    description="Film, Dizi ve Kitap önerileri için AI destekli API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Uygulama başlatılıyor...")
    init_db()
    logger.info("Veritabanı başlatıldı")
    try:
        if recommendation_engine.load_model():
            logger.info("ML modeli diskten yüklendi")
        else:
            db = next(get_db())
            try:
                logger.info("ML modeli eğitiliyor...")
                recommendation_engine.train(db)
                logger.info("ML modeli başarıyla eğitildi")
            except Exception as e:
                logger.error(f"Model eğitimi başarısız: {e}", exc_info=True)
            finally:
                db.close()
    except Exception as e:
        logger.error(f"Model başlatma hatası: {e}", exc_info=True)
    logger.info("Uygulama başlatıldı")

@app.get("/")
async def root():
    return {
        "message": "Kişiselleştirilmiş İçerik Öneri Sistemi API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/icerikler", response_model=IcerikResponse, status_code=status.HTTP_201_CREATED)
async def icerik_olustur(icerik: IcerikCreate, db: Session = Depends(get_db)):
    db_icerik = Icerik(**icerik.dict())
    db.add(db_icerik)
    db.commit()
    db.refresh(db_icerik)
    recommendation_engine.train(db)
    return db_icerik

@app.get("/api/icerikler", response_model=List[IcerikResponse])
async def icerikleri_listele(
    skip: int = 0,
    limit: int = 100,
    tur: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Icerik).filter(
        Icerik.baslik != None,
        Icerik.baslik != "",
        Icerik.baslik != "null"
    )
    if tur:
        query = query.filter(Icerik.tur == tur)
    
    # SADECE GERÇEK POSTERLİ OLANLARI GÖSTER
    # Placeholder'ları (placehold.co) tamamen filtrele
    query = query.filter(
        Icerik.poster_url != None,
        Icerik.poster_url != ""
        # Placeholder'ları artık kabul ediyoruz çünkü veri seti linkleri bozuk
        # ~Icerik.poster_url.like('%placehold%') 
    )
    
    # Filter low vote outliers to prevent obscure 10.0 ratings (ONLY FOR MOVIES)
    # Diziler ve kitaplar için oy verisi olmadığı için (0) onları filtrelememeliyiz.
    from sqlalchemy import or_
    query = query.filter(
        or_(
            Icerik.tur != 'Film',
            Icerik.oy_sayisi > 50
        )
    )
    
    # IMDB puanına göre sırala (en yüksek önce)
    from sqlalchemy import desc
    query = query.order_by(desc(Icerik.imdb_puani))
    
    icerikler = query.offset(skip).limit(limit).all()
    return icerikler

@app.get("/api/icerikler/{icerik_id}", response_model=IcerikResponse)
async def icerik_getir(icerik_id: int, db: Session = Depends(get_db)):
    icerik = db.query(Icerik).filter(Icerik.id == icerik_id).first()
    if not icerik:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"İçerik ID {icerik_id} bulunamadı"
        )
    return icerik

@app.post("/api/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(kullanici: KullaniciCreate, db: Session = Depends(get_db)):
    from auth import hash_password, generate_token
    from models import AuthResponse
    mevcut_email = db.query(Kullanici).filter(Kullanici.email == kullanici.email).first()
    if mevcut_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kullanılıyor"
        )
    mevcut_kullanici = db.query(Kullanici).filter(
        Kullanici.kullanici_adi == kullanici.kullanici_adi
    ).first()
    if mevcut_kullanici:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    password_hash = hash_password(kullanici.password)
    db_kullanici = Kullanici(
        kullanici_adi=kullanici.kullanici_adi,
        email=kullanici.email,
        password_hash=password_hash
    )
    db.add(db_kullanici)
    db.commit()
    db.refresh(db_kullanici)
    token = generate_token()
    return AuthResponse(
        user=db_kullanici,
        token=token,
        message="Kayıt başarılı!"
    )

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(credentials: KullaniciLogin, db: Session = Depends(get_db)):
    from auth import verify_password, generate_token
    from models import AuthResponse, KullaniciLogin
    kullanici = db.query(Kullanici).filter(Kullanici.email == credentials.email).first()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    if not verify_password(credentials.password, kullanici.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    token = generate_token()
    return AuthResponse(
        user=kullanici,
        token=token,
        message="Giriş başarılı!"
    )

@app.post("/api/auth/forgot-password")
async def forgot_password(request: dict, db: Session = Depends(get_db)):
    from email_service import email_service
    from datetime import datetime
    email = request.get("email", "").strip()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email adresi gerekli"
        )
    kullanici = db.query(Kullanici).filter(Kullanici.email == email).first()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu email adresiyle kayıtlı bir kullanıcı bulunamadı. Lütfen kayıt olun."
        )
    db.query(PasswordResetToken).filter(
        PasswordResetToken.kullanici_id == kullanici.id,
        PasswordResetToken.used == 0
    ).delete()
    token = email_service.generate_reset_token()
    expires_at = email_service.get_token_expiry()
    db_token = PasswordResetToken(
        kullanici_id=kullanici.id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    email_service.send_password_reset_email(
        to_email=kullanici.email,
        reset_token=token,
        username=kullanici.kullanici_adi
    )
    logger.info(f"Password reset requested for user: {kullanici.kullanici_adi}")
    return {
        "success": True,
        "message": "Şifre sıfırlama kodu email adresinize gönderildi."
    }

@app.post("/api/auth/reset-password")
async def reset_password(request: dict, db: Session = Depends(get_db)):
    from auth import hash_password
    from datetime import datetime
    token = request.get("token", "").strip()
    new_password = request.get("new_password", "").strip()
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token ve yeni şifre gerekli"
        )
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Şifre en az 6 karakter olmalı"
        )
    db_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token.like(f"{token}%")
    ).first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş kod"
        )
    if db_token.used == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kod zaten kullanılmış"
        )
    if datetime.utcnow() > db_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kodun süresi dolmuş. Yeni kod talep edin."
        )
    kullanici = db.query(Kullanici).filter(Kullanici.id == db_token.kullanici_id).first()
    kullanici.password_hash = hash_password(new_password)
    db_token.used = 1
    db.commit()
    logger.info(f"Password reset successful for user: {kullanici.kullanici_adi}")
    return {
        "success": True,
        "message": "Şifreniz başarıyla değiştirildi. Giriş yapabilirsiniz."
    }

class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str

@app.post("/api/auth/change-password")
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    from auth import verify_password, hash_password
    
    kullanici = db.query(Kullanici).filter(Kullanici.id == request.user_id).first()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if not verify_password(request.old_password, kullanici.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mevcut şifre hatalı"
        )
    
    kullanici.password_hash = hash_password(request.new_password)
    db.commit()
    
    logger.info(f"Password changed successfully for user id: {kullanici.id}")
    return {
        "success": True,
        "message": "Şifreniz başarıyla değiştirildi"
    }

@app.post("/api/puanlar", response_model=PuanResponse, status_code=status.HTTP_201_CREATED)
async def puan_ver(puan: PuanCreate, db: Session = Depends(get_db)):
    kullanici = db.query(Kullanici).filter(Kullanici.id == puan.kullanici_id).first()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kullanıcı ID {puan.kullanici_id} bulunamadı"
        )
    icerik = db.query(Icerik).filter(Icerik.id == puan.icerik_id).first()
    if not icerik:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"İçerik ID {puan.icerik_id} bulunamadı"
        )
    mevcut_puan = db.query(Puan).filter(
        Puan.kullanici_id == puan.kullanici_id,
        Puan.icerik_id == puan.icerik_id
    ).first()
    if mevcut_puan:
        mevcut_puan.puan = puan.puan
        db.commit()
        db.refresh(mevcut_puan)
        return mevcut_puan
    db_puan = Puan(**puan.dict())
    db.add(db_puan)
    db.commit()
    db.refresh(db_puan)
    return db_puan

@app.get("/api/kullanicilar/{kullanici_id}/puanlar", response_model=List[PuanResponse])
async def kullanici_puanlarini_getir(kullanici_id: int, db: Session = Depends(get_db)):
    puanlar = db.query(Puan).filter(Puan.kullanici_id == kullanici_id).all()
    return puanlar

@app.post("/api/yorumlar", response_model=YorumResponse, status_code=status.HTTP_201_CREATED)
async def yorum_yap(yorum: YorumCreate, db: Session = Depends(get_db)):
    kullanici = db.query(Kullanici).filter(Kullanici.id == yorum.kullanici_id).first()
    if not kullanici:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    icerik = db.query(Icerik).filter(Icerik.id == yorum.icerik_id).first()
    if not icerik:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    db_yorum = Yorum(**yorum.dict())
    db.add(db_yorum)
    db.commit()
    db.refresh(db_yorum)
    db_yorum.kullanici_adi = kullanici.kullanici_adi
    response = YorumResponse.from_orm(db_yorum)
    return response

@app.get("/api/icerikler/{icerik_id}/yorumlar", response_model=List[YorumResponse])
async def icerik_yorumlari(icerik_id: int, db: Session = Depends(get_db)):
    yorumlar = db.query(Yorum).filter(Yorum.icerik_id == icerik_id).order_by(Yorum.olusturma_tarihi.desc()).all()
    for y in yorumlar:
        y.kullanici_adi = y.kullanici.kullanici_adi
    return yorumlar

@app.get("/api/kullanicilar/{kullanici_id}/gecmis", response_model=List[dict])
async def kullanici_kutuphanesi(kullanici_id: int, db: Session = Depends(get_db)):
    puanlar = db.query(Puan).filter(Puan.kullanici_id == kullanici_id).order_by(Puan.puanlama_tarihi.desc()).all()
    gecmis = []
    for p in puanlar:
        gecmis.append({
            "id": p.icerik.id,
            "baslik": p.icerik.baslik,
            "tur": p.icerik.tur,
            "poster_url": p.icerik.poster_url,
            "puan": p.puan,
            "tarih": p.puanlama_tarihi
        })
    return gecmis

@app.post("/api/oneriler", response_model=OneriResponse)
async def oneri_al(request: OneriRequest, db: Session = Depends(get_db)):
    kullanici = db.query(Kullanici).filter(Kullanici.id == request.kullanici_id).first()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kullanıcı ID {request.kullanici_id} bulunamadı"
        )
    icerik = db.query(Icerik).filter(Icerik.id == request.icerik_id).first()
    if not icerik:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"İçerik ID {request.icerik_id} bulunamadı"
        )
    mevcut_puan = db.query(Puan).filter(
        Puan.kullanici_id == request.kullanici_id,
        Puan.icerik_id == request.icerik_id
    ).first()
    if not mevcut_puan:
        db_puan = Puan(
            kullanici_id=request.kullanici_id,
            icerik_id=request.icerik_id,
            puan=request.puan
        )
        db.add(db_puan)
        db.commit()
    oneriler, oneri_tipi, aciklama = recommendation_engine.get_recommendations(
        icerik_id=request.icerik_id,
        puan=request.puan,
        kullanici_id=request.kullanici_id,
        db=db,
        top_n=5
    )
    if not oneriler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uygun öneri bulunamadı. Lütfen daha fazla içerik ekleyin."
        )
    return OneriResponse(
        oneriler=oneriler,
        oneri_tipi=oneri_tipi,
        aciklama=aciklama
    )

@app.get("/api/kullanicilar/{kullanici_id}/oneriler", response_model=List[IcerikResponse])
async def kullanici_genel_onerileri(kullanici_id: int, db: Session = Depends(get_db)):
    yuksek_puanli_icerikler = db.query(Puan).filter(
        Puan.kullanici_id == kullanici_id,
        Puan.puan >= 7
    ).all()
    if not yuksek_puanli_icerikler:
        yuksek_puanli_icerikler = db.query(Puan).filter(
            Puan.kullanici_id == kullanici_id
        ).order_by(Puan.puan.desc()).limit(1).all()
    if not yuksek_puanli_icerikler:
        return db.query(Icerik).order_by(Icerik.imdb_puani.desc().nullslast()).limit(5).all()
    ana_icerik_id = yuksek_puanli_icerikler[0].icerik_id
    oneriler, _, _ = recommendation_engine.get_recommendations(
        icerik_id=ana_icerik_id,
        puan=8,  
        kullanici_id=kullanici_id,
        db=db,
        top_n=5
    )
    return oneriler

@app.post("/api/model/yeniden-egit")
async def modeli_yeniden_egit(db: Session = Depends(get_db)):
    recommendation_engine.train(db)
    return {"message": "Model başarıyla yeniden eğitildi", "trained": recommendation_engine.trained}

@app.get("/api/sql/top-rated")
async def top_rated_contents(limit: int = 10, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_top_rated_contents_raw_sql(limit)
    return results

@app.get("/api/sql/user-statistics/{kullanici_id}")
async def user_statistics(kullanici_id: int, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_user_statistics_raw_sql(kullanici_id)
    return results

@app.get("/api/sql/similar-contents/{icerik_id}")
async def similar_contents_sql(icerik_id: int, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_content_recommendations_raw_sql(icerik_id)
    return results

@app.get("/api/sql/popular-by-category")
async def popular_by_category(kategori: str = None, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_popular_contents_by_category_raw_sql(kategori)
    return results

@app.get("/api/sql/yearly-statistics")
async def yearly_statistics(db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_yearly_statistics_raw_sql()
    return results

@app.get("/api/sql/user-similarity/{kullanici_id1}/{kullanici_id2}")
async def user_similarity(kullanici_id1: int, kullanici_id2: int, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_user_similarity_raw_sql(kullanici_id1, kullanici_id2)
    return results

@app.get("/api/sql/trending")
async def trending_contents(days: int = 30, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_trending_contents_raw_sql(days)
    return results

@app.get("/api/sql/category-statistics")
async def category_statistics(db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_category_statistics_raw_sql()
    return results

@app.get("/api/sql/contents-with-stats")
async def contents_with_rating_stats(db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_contents_with_rating_stats()
    return [
        {
            "id": r.id,
            "baslik": r.baslik,
            "tur": r.tur,
            "kategoriler": r.kategoriler,
            "ozet": r.ozet,
            "yil": r.yil,
            "imdb_puani": float(r.imdb_puani) if r.imdb_puani else None,
            "puan_sayisi": r.puan_sayisi,
            "ortalama_puan": float(r.ortalama_puan) if r.ortalama_puan else None,
            "min_puan": r.min_puan,
            "max_puan": r.max_puan,
        }
        for r in results
    ]

@app.get("/api/sql/user-favorite-categories/{kullanici_id}")
async def user_favorite_categories(kullanici_id: int, db: Session = Depends(get_db)):
    sql_queries = AdvancedSQLQueries(db)
    results = sql_queries.get_user_favorite_categories(kullanici_id)
    return [
        {
            "kategori": r.kategoriler,
            "puan_sayisi": r.puan_sayisi,
            "ortalama_puan": float(r.ortalama_puan) if r.ortalama_puan else None,
        }
        for r in results
    ]

@app.post("/api/chatbot/sohbet")
async def chatbot_sohbet(
    request: dict,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Chatbot request received: {request}")
        message = request.get("message", "").strip()
        kullanici_id = request.get("kullanici_id")

        if not message:
            logger.warning(f"Empty message received. Request: {request}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mesaj boş olamaz"
            )

        if not kullanici_id:
            logger.warning(f"Missing kullanici_id. Request: {request}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kullanıcı ID gerekli"
            )

        kullanici = db.query(Kullanici).filter(Kullanici.id == kullanici_id).first()
        if not kullanici:
            logger.warning(f"User not found: {kullanici_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

        logger.info(f"Processing message for user {kullanici_id}: {message[:50]}...")
        response = chatbot_service.process_message(message, kullanici_id, db)

        return {
            "success": True,
            "bot_response": response["bot_response"],
            "response_type": response["response_type"],
            "recommended_content": response["recommended_content"],
            "explanation": response["explanation"],
            "original_message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot servisi hatası: {str(e)}"
        )

@app.get("/api/chatbot/akilli-arama")
async def akilli_arama(
    query: str,
    kullanici_id: int,
    db: Session = Depends(get_db)
):
    try:
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arama sorgusu boş olamaz"
            )

        search_message = f"Bana {query} öner"
        response = chatbot_service.process_message(search_message, kullanici_id, db)

        results = []
        if response["recommended_content"]:
            results.append(response["recommended_content"])
            main_content = response["recommended_content"]
            
            similar_content = db.query(Icerik).filter(
                Icerik.tur == main_content["tur"],
                Icerik.id != main_content["id"]
            )
            
            if main_content["kategoriler"]:
                categories = main_content["kategoriler"].split(", ")
                for category in categories[:2]:  
                    similar_content = similar_content.filter(
                        Icerik.kategoriler.like(f'%{category}%')
                    )
            
            similar_results = similar_content.order_by(
                Icerik.imdb_puani.desc()
            ).limit(4).all()

            for content in similar_results:
                results.append({
                    "id": content.id,
                    "baslik": content.baslik,
                    "tur": content.tur,
                    "kategoriler": content.kategoriler,
                    "ozet": content.ozet,
                    "yil": content.yil,
                    "imdb_puani": content.imdb_puani,
                    "poster_url": content.poster_url
                })

        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "explanation": response["explanation"] or f"'{query}' araması için bulunan sonuçlar"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Akıllı arama servisi şu anda kullanılamıyor"
        )

@app.get("/api/chatbot/oneri-kategorileri")
async def oneri_kategorileri():
    return {
        "mood_based": {
            "title": "Ruh Haline Göre",
            "categories": [
                "Eğlenceli & Komik",
                "Gerilim & Heyecan",
                "Duygusal & Dramatik",
            ]
        },
        "genre_based": {
            "title": "Türe Göre",
            "categories": [
                "Bilim Kurgu & Fantastik",
                "Aksiyon & Macera", 
                "Korku & Gizem",
            ]
        },
        "similarity_based": {
            "title": "Benzerlik Bazlı",
            "categories": [
                "İzlediklerime Benzer",
                "Son Beğendiklerime Göre",
                "Popüler İçerikler",
            ]
        },
        "time_based": {
            "title": "Zaman Bazlı",
            "categories": [
                "Yeni Çıkanlar",
                "Klasikler",
                "90'lar",
            ]
        },
        "quick_suggestions": [
            "Bana film öner",
            "Bana dizi öner",
            "Bana kitap öner",
        ]
    }

@app.post("/api/watchlist", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(request: dict, db: Session = Depends(get_db)):
    kullanici_id = request.get("kullanici_id")
    icerik_id = request.get("icerik_id")
    
    if not kullanici_id or not icerik_id:
        raise HTTPException(status_code=400, detail="kullanici_id ve icerik_id gerekli")
    
    # Check if already in watchlist
    existing = db.query(Watchlist).filter(
        Watchlist.kullanici_id == kullanici_id,
        Watchlist.icerik_id == icerik_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Bu içerik zaten listenizde")
    
    watchlist_item = Watchlist(kullanici_id=kullanici_id, icerik_id=icerik_id)
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    return {"message": "İzlenecekler listesine eklendi", "id": watchlist_item.id}

@app.delete("/api/watchlist/{watchlist_id}")
async def remove_from_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    watchlist_item = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Öğe bulunamadı")
    
    db.delete(watchlist_item)
    db.commit()
    
    return {"message": "Listeden çıkarıldı"}

@app.get("/api/kullanicilar/{kullanici_id}/watchlist")
async def get_user_watchlist(kullanici_id: int, db: Session = Depends(get_db)):
    watchlist_items = db.query(Watchlist).filter(
        Watchlist.kullanici_id == kullanici_id
    ).order_by(Watchlist.eklenme_tarihi.desc()).all()
    
    result = []
    for item in watchlist_items:
        result.append({
            "watchlist_id": item.id,
            "id": item.icerik.id,
            "baslik": item.icerik.baslik,
            "tur": item.icerik.tur,
            "poster_url": item.icerik.poster_url,
            "imdb_puani": item.icerik.imdb_puani,
            "eklenme_tarihi": item.eklenme_tarihi
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)