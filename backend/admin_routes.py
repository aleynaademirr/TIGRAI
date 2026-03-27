from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Kullanici, Icerik, Puan, Yorum
from typing import Optional
import logging

logger = logging.getLogger(__name__)
admin_router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

def verify_admin(admin_id: int, db: Session):
    user = db.query(Kullanici).filter(Kullanici.id == admin_id).first()
    if not user or user.is_admin != 1:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    return user

# JSON API Endpoints for Flutter
@admin_router.get("/api/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Admin dashboard istatistikleri"""
    total_content = db.query(Icerik).count()
    total_users = db.query(Kullanici).count()
    total_ratings = db.query(Puan).count()
    total_comments = db.query(Yorum).count()
    
    # Kategorilere göre içerik sayısı
    movies = db.query(Icerik).filter(Icerik.tur == 'Film').count()
    series = db.query(Icerik).filter(Icerik.tur == 'Dizi').count()
    books = db.query(Icerik).filter(Icerik.tur == 'Kitap').count()
    
    return {
        "total_content": total_content,
        "total_users": total_users,
        "total_ratings": total_ratings,
        "total_comments": total_comments,
        "content_by_type": {
            "movies": movies,
            "series": series,
            "books": books
        }
    }

@admin_router.get("/api/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Tüm kullanıcıları getir"""
    users = db.query(Kullanici).all()
    result = []
    for user in users:
        rating_count = db.query(Puan).filter(Puan.kullanici_id == user.id).count()
        comment_count = db.query(Yorum).filter(Yorum.kullanici_id == user.id).count()
        result.append({
            "id": user.id,
            "kullanici_adi": user.kullanici_adi,
            "email": user.email,
            "is_admin": user.is_admin == 1,
            "olusturma_tarihi": user.olusturma_tarihi.isoformat() if user.olusturma_tarihi else None,
            "rating_count": rating_count,
            "comment_count": comment_count
        })
    return result

@admin_router.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Kullanıcıyı sil"""
    user = db.query(Kullanici).filter(Kullanici.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Admin kendini silemez
    if user.is_admin == 1:
        raise HTTPException(status_code=403, detail="Admin kullanıcılar silinemez")
    
    # Kullanıcının puanlarını ve yorumlarını sil
    db.query(Puan).filter(Puan.kullanici_id == user_id).delete()
    db.query(Yorum).filter(Yorum.kullanici_id == user_id).delete()
    
    db.delete(user)
    db.commit()
    return {"success": True, "message": "Kullanıcı silindi"}

@admin_router.post("/api/users/{user_id}/toggle-admin")
async def toggle_admin_status(user_id: int, db: Session = Depends(get_db)):
    """Kullanıcının admin yetkisini değiştir"""
    user = db.query(Kullanici).filter(Kullanici.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    user.is_admin = 0 if user.is_admin == 1 else 1
    db.commit()
    return {
        "success": True,
        "is_admin": user.is_admin == 1,
        "message": f"Kullanıcı {'admin yapıldı' if user.is_admin == 1 else 'admin yetkisi kaldırıldı'}"
    }

@admin_router.get("/api/recent-activity")
async def get_recent_activity(limit: int = 20, db: Session = Depends(get_db)):
    """Son aktiviteleri getir - yorumlar ve puanlar ile gerçek posterler"""
    try:
        recent_comments = db.query(Yorum).order_by(Yorum.olusturma_tarihi.desc()).limit(limit).all()
        recent_ratings = db.query(Puan).order_by(Puan.puanlama_tarihi.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Aktivite sorgusu hatası: {e}")
        return []
    
    activities = []
    
    # Yorumları ekle
    for comment in recent_comments:
        try:
            # Null kontrolü - ilişkili veriler yoksa atla
            if not comment.kullanici or not comment.icerik:
                logger.warning(f"Yorum {comment.id} için eksik ilişki verisi")
                continue
                
            activities.append({
                "type": "comment",
                "user": comment.kullanici.kullanici_adi,
                "content": comment.icerik.baslik,
                "text": comment.yorum_metni,  # Tam metin, kısaltma yok
                "poster_url": comment.icerik.poster_url or "",  # Gerçek poster URL
                "timestamp": comment.olusturma_tarihi.isoformat() if comment.olusturma_tarihi else None
            })
        except Exception as e:
            logger.warning(f"Yorum {comment.id} işlenirken hata: {e}")
            continue
    
    # Puanları ekle
    for rating in recent_ratings:
        try:
            # Null kontrolü - ilişkili veriler yoksa atla
            if not rating.kullanici or not rating.icerik:
                logger.warning(f"Puan {rating.id} için eksik ilişki verisi")
                continue
                
            activities.append({
                "type": "rating",
                "user": rating.kullanici.kullanici_adi,
                "content": rating.icerik.baslik,
                "rating": rating.puan,
                "poster_url": rating.icerik.poster_url or "",  # Gerçek poster URL
                "timestamp": rating.puanlama_tarihi.isoformat() if rating.puanlama_tarihi else None
            })
        except Exception as e:
            logger.warning(f"Puan {rating.id} işlenirken hata: {e}")
            continue
    
    # Zamana göre sırala
    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return activities[:limit]

# HTML Endpoints (mevcut)
@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    total_content = db.query(Icerik).count()
    total_users = db.query(Kullanici).count()
    total_ratings = db.query(Puan).count()
    total_comments = db.query(Yorum).count()
    popular_content = db.query(Icerik).order_by(Icerik.imdb_puani.desc()).limit(10).all()
    recent_content = db.query(Icerik).order_by(Icerik.olusturma_tarihi.desc()).limit(10).all()
    recent_comments = db.query(Yorum).order_by(Yorum.olusturma_tarihi.desc()).limit(20).all()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_content": total_content,
        "total_users": total_users,
        "total_ratings": total_ratings,
        "total_comments": total_comments,
        "popular_content": popular_content,
        "recent_content": recent_content,
        "recent_comments": recent_comments, 
    })

@admin_router.get("/kullanicilar", response_class=HTMLResponse)
async def list_users_html(request: Request, db: Session = Depends(get_db)):
    users = db.query(Kullanici).all()
    for user in users:
        user.rating_count = db.query(Puan).filter(Puan.kullanici_id == user.id).count()
        user.comment_count = db.query(Yorum).filter(Yorum.kullanici_id == user.id).count()
    total_ratings = db.query(Puan).count()
    total_comments = db.query(Yorum).count()
    
    return templates.TemplateResponse("admin/kullanicilar.html", {
        "request": request,
        "users": users,
        "total_ratings": total_ratings,
        "total_comments": total_comments,
    })

@admin_router.get("/icerikler", response_class=HTMLResponse)
async def list_content(
    request: Request,
    page: int = 1,
    search: Optional[str] = None,
    tur: Optional[str] = None,
    db: Session = Depends(get_db)
):
    per_page = 20
    query = db.query(Icerik)
    
    if search:
        query = query.filter(Icerik.baslik.like(f"%{search}%"))
    if tur:
        query = query.filter(Icerik.tur == tur)
    
    total = query.count()
    icerikler = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("admin/icerikler.html", {
        "request": request,
        "icerikler": icerikler,
        "current_page": page,
        "total_pages": total_pages,
        "search": search or "",
        "tur": tur or "",
    })

@admin_router.get("/icerikler/yeni", response_class=HTMLResponse)
async def new_content_form(request: Request):
    return templates.TemplateResponse("admin/icerik_form.html", {
        "request": request,
        "icerik": None,
        "action": "create"
    })

@admin_router.post("/icerikler/yeni")
async def create_content(
    baslik: str = Form(...),
    tur: str = Form(...),
    kategoriler: str = Form(...),
    ozet: str = Form(""),
    yil: int = Form(None),
    imdb_puani: float = Form(0),
    poster_url: str = Form(""),
    db: Session = Depends(get_db)
):
    icerik = Icerik(
        baslik=baslik,
        tur=tur,
        kategoriler=kategoriler,
        ozet=ozet,
        yil=yil,
        imdb_puani=imdb_puani,
        poster_url=poster_url
    )
    db.add(icerik)
    db.commit()
    return RedirectResponse(url="/admin/icerikler", status_code=303)

@admin_router.get("/icerikler/{icerik_id}/duzenle", response_class=HTMLResponse)
async def edit_content_form(request: Request, icerik_id: int, db: Session = Depends(get_db)):
    icerik = db.query(Icerik).filter(Icerik.id == icerik_id).first()
    if not icerik:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    return templates.TemplateResponse("admin/icerik_form.html", {
        "request": request,
        "icerik": icerik,
        "action": "edit"
    })

@admin_router.post("/icerikler/{icerik_id}/duzenle")
async def update_content(
    icerik_id: int,
    baslik: str = Form(...),
    tur: str = Form(...),
    kategoriler: str = Form(...),
    ozet: str = Form(""),
    yil: int = Form(None),
    imdb_puani: float = Form(0),
    poster_url: str = Form(""),
    db: Session = Depends(get_db)
):
    icerik = db.query(Icerik).filter(Icerik.id == icerik_id).first()
    if not icerik:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    icerik.baslik = baslik
    icerik.tur = tur
    icerik.kategoriler = kategoriler
    icerik.ozet = ozet
    icerik.yil = yil
    icerik.imdb_puani = imdb_puani
    icerik.poster_url = poster_url
    db.commit()
    return RedirectResponse(url="/admin/icerikler", status_code=303)

@admin_router.post("/icerikler/{icerik_id}/sil")
async def delete_content(icerik_id: int, db: Session = Depends(get_db)):
    icerik = db.query(Icerik).filter(Icerik.id == icerik_id).first()
    if not icerik:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    db.delete(icerik)
    db.commit()
    return RedirectResponse(url="/admin/icerikler", status_code=303)