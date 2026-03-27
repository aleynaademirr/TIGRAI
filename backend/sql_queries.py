from sqlalchemy import text, func, case, and_, or_, desc, asc
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import Icerik, Kullanici, Puan, engine
class AdvancedSQLQueries:
    def __init__(self, db: Session):
        self.db = db
    def get_top_rated_contents_raw_sql(self, limit: int = 10) -> List[Dict]:
        sql = text()
        result = self.db.execute(sql, {"limit": limit})
        return [dict(row) for row in result]
    def get_user_statistics_raw_sql(self, kullanici_id: int) -> Dict:
        sql = text()
        result = self.db.execute(sql, {"kullanici_id": kullanici_id})
        row = result.first()
        return dict(row) if row else {}
    def get_content_recommendations_raw_sql(self, icerik_id: int, min_similarity: float = 0.5) -> List[Dict]:
        sql = text()
        result = self.db.execute(sql, {"icerik_id": icerik_id, "min_similarity": min_similarity})
        return [dict(row) for row in result]
    def get_popular_contents_by_category_raw_sql(self, kategori: str = None) -> List[Dict]:
        if kategori:
            sql = text()
            result = self.db.execute(sql, {"kategori_pattern": f"%{kategori}%"})
        else:
            sql = text()
            result = self.db.execute(sql)
        return [dict(row) for row in result]
    def get_yearly_statistics_raw_sql(self) -> List[Dict]:
        sql = text()
        result = self.db.execute(sql)
        return [dict(row) for row in result]
    def get_user_similarity_raw_sql(self, kullanici_id1: int, kullanici_id2: int) -> Dict:
        sql = text()
        result = self.db.execute(sql, {"k1": kullanici_id1, "k2": kullanici_id2})
        row = result.first()
        return dict(row) if row else {}
    def get_trending_contents_raw_sql(self, days: int = 30) -> List[Dict]:
        sql = text()
        result = self.db.execute(sql, {"days": days})
        return [dict(row) for row in result]
    def get_category_statistics_raw_sql(self) -> List[Dict]:
        sql = text()
        result = self.db.execute(sql)
        return [dict(row) for row in result]
    def get_contents_with_rating_stats(self):
        return self.db.query(
            Icerik.id,
            Icerik.baslik,
            Icerik.tur,
            Icerik.kategoriler,
            Icerik.ozet,
            Icerik.yil,
            Icerik.imdb_puani,
            Icerik.poster_url,
            func.count(Puan.id).label('puan_sayisi'),
            func.avg(Puan.puan).label('ortalama_puan'),
            func.min(Puan.puan).label('min_puan'),
            func.max(Puan.puan).label('max_puan')
        ).outerjoin(
            Puan, Icerik.id == Puan.icerik_id
        ).group_by(
            Icerik.id
        ).having(
            func.count(Puan.id) > 0
        ).order_by(
            desc(func.avg(Puan.puan))
        ).all()
    def get_user_favorite_categories(self, kullanici_id: int):
        return self.db.query(
            Icerik.kategoriler,
            func.count(Puan.id).label('puan_sayisi'),
            func.avg(Puan.puan).label('ortalama_puan')
        ).join(
            Puan, Icerik.id == Puan.icerik_id
        ).filter(
            Puan.kullanici_id == kullanici_id
        ).group_by(
            Icerik.kategoriler
        ).order_by(
            desc(func.avg(Puan.puan))
        ).all()
    def get_highly_rated_underrated_contents(self, min_imdb: float = 7.0):
        return self.db.query(
            Icerik.id,
            Icerik.baslik,
            Icerik.tur,
            Icerik.imdb_puani,
            func.avg(Puan.puan).label('kullanici_ortalama'),
            (Icerik.imdb_puani - func.avg(Puan.puan)).label('puan_farki')
        ).join(
            Puan, Icerik.id == Puan.icerik_id
        ).filter(
            Icerik.imdb_puani >= min_imdb
        ).group_by(
            Icerik.id
        ).having(
            func.avg(Puan.puan) < Icerik.imdb_puani - 1.0
        ).order_by(
            desc('puan_farki')
        ).all()
    def get_content_recommendation_by_similar_users(self, kullanici_id: int, limit: int = 10):
        similar_users = self.db.query(
            Puan.kullanici_id,
            func.count(Puan.icerik_id).label('ortak_icerik')
        ).join(
            Puan.alias('p2'), 
            and_(
                Puan.icerik_id == Puan.alias('p2').c.icerik_id,
                Puan.kullanici_id != Puan.alias('p2').c.kullanici_id,
                Puan.alias('p2').c.kullanici_id == kullanici_id
            )
        ).filter(
            Puan.kullanici_id != kullanici_id
        ).group_by(
            Puan.kullanici_id
        ).having(
            func.count(Puan.icerik_id) >= 3
        ).subquery()
        return self.db.query(
            Icerik
        ).join(
            Puan, Icerik.id == Puan.icerik_id
        ).join(
            similar_users, Puan.kullanici_id == similar_users.c.kullanici_id
        ).filter(
            ~Puan.icerik_id.in_(
                self.db.query(Puan.icerik_id).filter(Puan.kullanici_id == kullanici_id)
            )
        ).filter(
            Puan.puan >= 7
        ).group_by(
            Icerik.id
        ).order_by(
            desc(func.count(Puan.id))
        ).limit(limit).all()