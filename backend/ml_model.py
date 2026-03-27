from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from database import Icerik, Puan, Kullanici
import warnings
warnings.filterwarnings('ignore')
import joblib
import os
class AIRecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.content_vectors = None
        self.content_ids = None
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.user_ids = None
        self.item_ids = None
        self.svd_model = None
        self.nmf_model = None
        self.svd_factors = None
        self.factorization_trained = False
        self.content_weight = 0.4
        self.collab_weight = 0.4
        self.factorization_weight = 0.2
        self.trained = False
        self.model_path = "model_dump.pkl"
        self.load_model()
    def _prepare_content_text(self, icerik: Icerik) -> str:
        text_parts = []
        if icerik.kategoriler:
            text_parts.append(icerik.kategoriler)
        if icerik.ozet:
            text_parts.append(icerik.ozet)
        if icerik.tur:
            text_parts.append(icerik.tur)
        return " ".join(text_parts)
    def _build_user_item_matrix(self, db: Session) -> Tuple[pd.DataFrame, List, List]:
        puanlar = db.query(Puan).all()
        if not puanlar:
            return None, [], []
        data = {
            "kullanici_id": [p.kullanici_id for p in puanlar],
            "icerik_id": [p.icerik_id for p in puanlar],
            "puan": [p.puan for p in puanlar]
        }
        df = pd.DataFrame(data)
        user_item_matrix = df.pivot_table(
            index='kullanici_id',
            columns='icerik_id',
            values='puan',
            fill_value=0
        )
        user_ids = user_item_matrix.index.tolist()
        item_ids = user_item_matrix.columns.tolist()
        return user_item_matrix, user_ids, item_ids
    def train(self, db: Session):
        print("[AI] Yapay zeka modelleri eğitiliyor...")
        icerikler = db.query(Icerik).all()
        if not icerikler:
            self.trained = False
            return
        content_texts = [self._prepare_content_text(icerik) for icerik in icerikler]
        self.content_vectors = self.vectorizer.fit_transform(content_texts)
        self.content_ids = [icerik.id for icerik in icerikler]
        print(f"[AI] Content-Based model eğitildi: {len(icerikler)} içerik")
        user_item_matrix, user_ids, item_ids = self._build_user_item_matrix(db)
        if user_item_matrix is not None and len(user_item_matrix) > 1:
            self.user_item_matrix = user_item_matrix
            self.user_ids = user_ids
            self.item_ids = item_ids
            self.user_similarity_matrix = cosine_similarity(user_item_matrix.values)
            matrix_normalized = user_item_matrix.values - user_item_matrix.values.mean(axis=1, keepdims=True)
            matrix_normalized = np.nan_to_num(matrix_normalized)
            n_components = min(50, min(len(user_ids), len(item_ids)) - 1)
            if n_components > 0:
                self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
                self.svd_factors = self.svd_model.fit_transform(matrix_normalized)
                matrix_positive = user_item_matrix.values - user_item_matrix.values.min()
                matrix_positive = np.maximum(matrix_positive, 0)  
                if matrix_positive.sum() > 0:
                    self.nmf_model = NMF(n_components=n_components, random_state=42, max_iter=200)
                    self.nmf_model.fit(matrix_positive)
            self.factorization_trained = True
            print(f"[AI] Collaborative Filtering eğitildi: {len(user_ids)} kullanıcı, {len(item_ids)} içerik")
        else:
            print("[AI] Yeterli puan verisi yok, sadece Content-Based model kullanılacak")
            self.factorization_trained = False
        self.trained = True
        self.save_model()
        print("[AI] Tüm modeller başarıyla eğitildi ve kaydedildi!")
    def save_model(self):
        try:
            data = {
                "vectorizer": self.vectorizer,
                "content_vectors": self.content_vectors,
                "content_ids": self.content_ids,
                "user_item_matrix": self.user_item_matrix,
                "user_similarity_matrix": self.user_similarity_matrix,
                "user_ids": self.user_ids,
                "item_ids": self.item_ids,
                "svd_model": self.svd_model,
                "nmf_model": self.nmf_model,
                "svd_factors": self.svd_factors,
                "factorization_trained": self.factorization_trained,
                "trained": self.trained
            }
            joblib.dump(data, self.model_path)
            print(f"[AI] Model kaydedildi: {self.model_path}")
        except Exception as e:
            print(f"[AI] Model kaydetme hatası: {e}")
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.vectorizer = data['vectorizer']
                self.content_vectors = data['content_vectors']
                self.content_ids = data['content_ids']
                self.user_item_matrix = data['user_item_matrix']
                self.user_similarity_matrix = data['user_similarity_matrix']
                self.user_ids = data['user_ids']
                self.item_ids = data['item_ids']
                self.svd_model = data['svd_model']
                self.nmf_model = data['nmf_model']
                self.svd_factors = data['svd_factors']
                self.factorization_trained = data['factorization_trained']
                self.trained = data.get('trained', True)
                print(f"[AI] Model diskten yüklendi: {self.model_path}")
                return True
            except Exception as e:
                print(f"[AI] Model yükleme hatası: {e}")
                return False
        return False
    def _content_based_recommendations(
        self, 
        icerik_id: int, 
        db: Session, 
        top_n: int = 10
    ) -> List[Tuple[int, float]]:
        if icerik_id not in self.content_ids:
            return []
        target_idx = self.content_ids.index(icerik_id)
        target_vector = self.content_vectors[target_idx]
        similarities = cosine_similarity(target_vector, self.content_vectors)[0]
        scores = [
            (self.content_ids[idx], float(sim))
            for idx, sim in enumerate(similarities)
            if self.content_ids[idx] != icerik_id
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    def _collaborative_filtering_recommendations(
        self,
        kullanici_id: int,
        db: Session,
        top_n: int = 10
    ) -> List[Tuple[int, float]]:
        if not self.factorization_trained or kullanici_id not in self.user_ids:
            return []
        try:
            user_idx = self.user_ids.index(kullanici_id)
            user_similarities = self.user_similarity_matrix[user_idx]
            kullanici_puanlari = db.query(Puan).filter(Puan.kullanici_id == kullanici_id).all()
            puanlanan_icerik_ids = {p.icerik_id for p in kullanici_puanlari}
            predictions = {}
            user_ratings = self.user_item_matrix.iloc[user_idx]
            for item_idx, item_id in enumerate(self.item_ids):
                if item_id not in puanlanan_icerik_ids:
                    similar_users_ratings = self.user_item_matrix.iloc[:, item_idx]
                    weighted_sum = 0
                    similarity_sum = 0
                    for other_user_idx, similarity in enumerate(user_similarities):
                        if other_user_idx != user_idx and similarity > 0:
                            rating = similar_users_ratings.iloc[other_user_idx]
                            if rating > 0:
                                weighted_sum += similarity * rating
                                similarity_sum += abs(similarity)
                    if similarity_sum > 0:
                        predicted_rating = weighted_sum / similarity_sum
                        predicted_rating = max(1, min(10, predicted_rating))
                        predictions[item_id] = predicted_rating
            sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            return sorted_predictions[:top_n]
        except Exception as e:
            print(f"[AI] Collaborative Filtering hatası: {e}")
            return []
    def _matrix_factorization_recommendations(
        self,
        kullanici_id: int,
        db: Session,
        top_n: int = 10
    ) -> List[Tuple[int, float]]:
        if not self.factorization_trained or kullanici_id not in self.user_ids:
            return []
        try:
            user_idx = self.user_ids.index(kullanici_id)
            kullanici_puanlari = db.query(Puan).filter(Puan.kullanici_id == kullanici_id).all()
            puanlanan_icerik_ids = {p.icerik_id for p in kullanici_puanlari}
            if self.svd_model is not None and self.svd_factors is not None:
                user_factors = self.svd_factors[user_idx]
                item_factors = self.svd_model.components_.T
                predictions = {}
                for item_idx, item_id in enumerate(self.item_ids):
                    if item_id not in puanlanan_icerik_ids:
                        predicted_rating = np.dot(user_factors, item_factors[item_idx])
                        mean_rating = self.user_item_matrix.values[user_idx].mean()
                        predicted_rating = mean_rating + predicted_rating
                        predicted_rating = max(1, min(10, predicted_rating))
                        predictions[item_id] = predicted_rating
                sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
                return sorted_predictions[:top_n]
            else:
                return []
        except Exception as e:
            print(f"[AI] Matrix Factorization hatası: {e}")
            return []
    def _hybrid_recommendations(
        self,
        icerik_id: int,
        kullanici_id: int,
        puan: int,
        db: Session,
        top_n: int = 10
    ) -> List[Tuple[int, float]]:
        all_scores = {}
        content_scores = self._content_based_recommendations(icerik_id, db, top_n * 2)
        for ic_id, score in content_scores:
            if ic_id not in all_scores:
                all_scores[ic_id] = 0.0
            all_scores[ic_id] += score * self.content_weight
        if self.factorization_trained:
            collab_scores = self._collaborative_filtering_recommendations(kullanici_id, db, top_n * 2)
            for ic_id, score in collab_scores:
                if ic_id not in all_scores:
                    all_scores[ic_id] = 0.0
                normalized_score = (score - 1) / 9.0
                all_scores[ic_id] += normalized_score * self.collab_weight
            mf_scores = self._matrix_factorization_recommendations(kullanici_id, db, top_n * 2)
            for ic_id, score in mf_scores:
                if ic_id not in all_scores:
                    all_scores[ic_id] = 0.0
                normalized_score = (score - 1) / 9.0
                all_scores[ic_id] += normalized_score * self.factorization_weight
        puan_weight = puan / 10.0
        for ic_id in all_scores:
            all_scores[ic_id] *= (0.5 + puan_weight * 0.5)
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]
    def get_recommendations(
        self,
        icerik_id: int,
        puan: int,
        kullanici_id: int,
        db: Session,
        top_n: int = 5
    ) -> Tuple[List[Icerik], str, str]:
        if not self.trained:
            self.train(db)
        if puan >= 7:
            prev_content_weight = self.content_weight
            self.content_weight = 0.8 # Temporary boost
            recommendations = self._hybrid_recommendations(
                icerik_id, kullanici_id, puan, db, top_n * 4 # Fetch more candidates
            )
            self.content_weight = prev_content_weight # Restore
        else:
             prev_collab_weight = self.collab_weight
             self.collab_weight = 0.8
             recommendations = self._hybrid_recommendations(
                icerik_id, kullanici_id, puan, db, top_n * 4
            )
             self.collab_weight = prev_collab_weight
        if not recommendations:
            content_recs = self._content_based_recommendations(icerik_id, db, top_n)
            recommendations = content_recs
        
        # En alakalı önerileri al (shuffle KALDIRILDI - alakalılığı korumak için)
        recommended_ids = [ic_id for ic_id, score in recommendations[:top_n]]
        oneriler = db.query(Icerik).filter(Icerik.id.in_(recommended_ids)).all()
        oneri_dict = {icerik.id: icerik for icerik in oneriler}
        ordered_oneriler = [oneri_dict[ic_id] for ic_id in recommended_ids if ic_id in oneri_dict]
        if recommendations:
            avg_score = np.mean([score for _, score in recommendations[:top_n]])
            if avg_score > 0.6:
                oneri_tipi = "ai_hybrid"
                aciklama = f"Seçiminize ve zevkinize göre {len(ordered_oneriler)} özel öneri"
            else:
                oneri_tipi = "ai_content"
                aciklama = "Benzer içerikler (Keşfet)"
        else:
            oneri_tipi = "fallback"
            aciklama = "Popüler içerikler"
        return ordered_oneriler[:top_n], oneri_tipi, aciklama
    def get_user_based_recommendations(
        self,
        kullanici_id: int,
        db: Session,
        top_n: int = 10
    ) -> List[Icerik]:
        if not self.factorization_trained:
            return db.query(Icerik).order_by(Icerik.imdb_puani.desc().nullslast()).limit(top_n).all()
        collab_recs = self._collaborative_filtering_recommendations(kullanici_id, db, top_n)
        mf_recs = self._matrix_factorization_recommendations(kullanici_id, db, top_n)
        combined_scores = {}
        for ic_id, score in collab_recs:
            combined_scores[ic_id] = score * 0.6
        for ic_id, score in mf_recs:
            if ic_id in combined_scores:
                combined_scores[ic_id] += score * 0.4
            else:
                combined_scores[ic_id] = score * 0.4
        sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_ids = [ic_id for ic_id, _ in sorted_recs[:top_n]]
        oneriler = db.query(Icerik).filter(Icerik.id.in_(recommended_ids)).all()
        oneri_dict = {icerik.id: icerik for icerik in oneriler}
        return [oneri_dict[ic_id] for ic_id in recommended_ids if ic_id in oneri_dict]
recommendation_engine = AIRecommendationEngine()