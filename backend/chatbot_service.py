import re
import random
from typing import Dict
from sqlalchemy.orm import Session
from database import Icerik, Kullanici, Puan, ChatHistory
from ml_model import recommendation_engine
import logging
import os

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = None
        self.ai_available = False
        
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                self.ai_available = True
                logger.info("Groq AI aktif")
            except Exception as e:
                logger.error(f"Groq AI hatası: {e}")
        
    def process_message(self, message: str, kullanici_id: int, db: Session) -> Dict:
        try:
            try:
                history_entry = ChatHistory(
                    kullanici_id=kullanici_id,
                    message=message,
                    is_user=1
                )
                db.add(history_entry)
                db.commit()
            except Exception as e:
                logger.error(f"History save error: {e}")
            
            if self.ai_available:
                bot_response = self._handle_with_ai(message, kullanici_id, db)
            else:
                bot_response = self._handle_basic(message, kullanici_id, db)
            
            try:
                if bot_response and bot_response.get('bot_response'):
                    history_entry = ChatHistory(
                        kullanici_id=kullanici_id,
                        message=bot_response['bot_response'],
                        is_user=0
                    )
                    db.add(history_entry)
                    db.commit()
            except Exception as e:
                logger.error(f"Bot response save error: {e}")
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return self._create_response("Üzgünüm, bir hata oluştu.", "error")
    
    def _handle_with_ai(self, message: str, kullanici_id: int, db: Session) -> Dict:
        try:
            chat_history = db.query(ChatHistory).filter(
                ChatHistory.kullanici_id == kullanici_id
            ).order_by(ChatHistory.timestamp.desc()).limit(10).all()
            chat_history.reverse()
            
            # RAG Context (Veritabanından bilgi çek)
            from rag_service import get_rag_context_for_llm, is_rag_available
            rag_context = ""
            if is_rag_available():
                rag_context = get_rag_context_for_llm(message)
            
            # System prompt: RAG bilgisini ve [Başlık] formatını ekle
            system_content = "Sen yardımsever bir film, dizi ve kitap öneri asistanısın. Kullanıcıya Türkçe cevap ver. EĞER BİR İÇERİK ÖNERİRSEN, içeriğin tam adını köşeli parantez içinde yaz. Örnek: 'Sana [Inception] filmini öneririm.' veya '[Suç ve Ceza] kitabını sevebilirsin.' Bu formatı sadece net bir öneri yaparken kullan."
            
            # KULLANICI ZEVKLERİNİ EKLE (Son verdiği yüksek puanlar)
            try:
                user_favorites = db.query(Icerik.baslik).join(Puan).filter(
                    Puan.kullanici_id == kullanici_id,
                    Puan.puan >= 7
                ).order_by(Puan.puanlama_tarihi.desc()).limit(5).all()
                
                favorite_titles = [f[0] for f in user_favorites]
                if favorite_titles:
                    system_content += f"\n\nKULLANICININ SEVDİKLERİ (Bunlara benzer şeyler öner): {', '.join(favorite_titles)}"
            except Exception as e:
                logger.error(f"Error fetching user favorites for prompt: {e}")

            if rag_context:
                system_content += f"\n\nVERİTABANINDAN BİLGİLER (Bunu kullanarak cevap ver):\n{rag_context}"
            
            messages = [{
                "role": "system",
                "content": system_content
            }]
            
            for h in chat_history:
                role = "user" if h.is_user else "assistant"
                messages.append({"role": role, "content": h.message})
            
            messages.append({"role": "user", "content": message})
            
            completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=300
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # [Başlık] formatını ara ve kart oluştur
            import re
            recommended_content = None
            explanation = None
            
            match = re.search(r'\[(.*?)\]', response_text)
            if match:
                baslik = match.group(1)
                # Veritabanında ara (Case insensitive)
                icerik = db.query(Icerik).filter(Icerik.baslik.ilike(f"%{baslik}%")).first()
                
                if icerik:
                    recommended_content = {
                        "id": icerik.id,
                        "baslik": icerik.baslik,
                        "tur": icerik.tur,
                        "kategoriler": icerik.kategoriler,
                        "ozet": icerik.ozet,
                        "yil": icerik.yil,
                        "imdb_puani": icerik.imdb_puani,
                        "poster_url": icerik.poster_url
                    }
                    response_text = response_text.replace(f"[{baslik}]", baslik) # Köşeli parantezleri temizle
                    explanation = "Yapay zeka önerisi"

            return {
                "bot_response": response_text,
                "response_type": "recommendation" if recommended_content else "chat",
                "recommended_content": recommended_content,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return self._handle_basic(message, kullanici_id, db)
    
    def _handle_basic(self, message: str, kullanici_id: int, db: Session) -> Dict:
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['merhaba', 'selam', 'hey']):
            return self._create_response("Merhaba! Size nasıl yardımcı olabilirim?", "greeting")
        
        if any(word in message_lower for word in ['film', 'dizi', 'kitap', 'öner']):
            user_ratings = db.query(Puan).filter(Puan.kullanici_id == kullanici_id).all()
            
            if user_ratings:
                high_rated = [p for p in user_ratings if p.puan >= 7]
                if high_rated:
                    target = random.choice(high_rated)
                    try:
                        recs, _, _ = recommendation_engine.get_recommendations(
                            target.icerik_id, target.puan, kullanici_id, db, top_n=1
                        )
                        if recs:
                            content = recs[0]
                            return {
                                "bot_response": f"Size {content.baslik} önerebilirim!",
                                "response_type": "recommendation",
                                "recommended_content": {
                                    "id": content.id,
                                    "baslik": content.baslik,
                                    "tur": content.tur,
                                    "kategoriler": content.kategoriler,
                                    "ozet": content.ozet,
                                    "yil": content.yil,
                                    "imdb_puani": content.imdb_puani,
                                    "poster_url": content.poster_url
                                },
                                "explanation": "Beğendiğiniz içeriklere göre seçtim"
                            }
                    except Exception as e:
                        logger.error(f"Recommendation error: {e}")
            
            popular = db.query(Icerik).filter(Icerik.imdb_puani > 0).all()
            if popular:
                content = random.choice(popular)
                return {
                    "bot_response": f"Size {content.baslik} önerebilirim!",
                    "response_type": "recommendation",
                    "recommended_content": {
                        "id": content.id,
                        "baslik": content.baslik,
                        "tur": content.tur,
                        "kategoriler": content.kategoriler,
                        "ozet": content.ozet,
                        "yil": content.yil,
                        "imdb_puani": content.imdb_puani,
                        "poster_url": content.poster_url
                    },
                    "explanation": "Popüler içeriklerden seçtim"
                }
        
        return self._create_response(
            "Anlayamadım. Film, dizi veya kitap önerisi isteyebilirsiniz.",
            "info"
        )
    
    def _create_response(self, text: str, response_type: str) -> Dict:
        return {
            "bot_response": text,
            "response_type": response_type,
            "recommended_content": None,
            "explanation": None
        }

chatbot_service = ChatbotService()