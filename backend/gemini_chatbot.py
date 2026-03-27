import os
import json
import random
import requests
from typing import Dict, Optional
from sqlalchemy.orm import Session
from database import Icerik, Kullanici, Puan
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class GeminiChatbot:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.conversation_history = {}
        self.system_prompt = """Sen WATCH AI adında yardımsever bir film, dizi ve kitap öneri asistanısın. 
Kullanıcılara Türkçe cevap veriyorsun. Samimi, arkadaş canlısı ve eğlenceli bir tarzın var.
Film, dizi ve kitap önerileri yapabilir, kullanıcının ruh haline göre içerik önerebilirsin."""

    def _call_gemini_api(self, prompt: str, user_id: int) -> str:
        if not self.api_key:
            return self._fallback_response(prompt)
        
        try:
            history = self.conversation_history.get(user_id, [])
            messages = []
            
            # System prompt
            messages.append({
                "role": "user",
                "parts": [{"text": f"[SİSTEM TALİMATI]: {self.system_prompt}"}]
            })
            messages.append({
                "role": "model",
                "parts": [{"text": "Anladım! Ben WATCH AI, film, dizi ve kitap önerileri konusunda uzman asistanınım. Size nasıl yardımcı olabilirim? 🎬📚"}]
            })
            
            # Add conversation history
            for msg in history[-10:]:
                messages.append(msg)
            
            # Add current message
            messages.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": messages,
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 500,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Save to history
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []
                
                self.conversation_history[user_id].append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })
                self.conversation_history[user_id].append({
                    "role": "model",
                    "parts": [{"text": ai_response}]
                })
                
                return ai_response
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Gemini API exception: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if any(x in prompt_lower for x in ['merhaba', 'selam', 'hey', 'nasılsın']):
            return random.choice([
                "Merhaba! 👋 Size nasıl yardımcı olabilirim?",
                "Selam! Film, dizi veya kitap önerisi ister misin? 🎬📚",
                "Hey! Bugün ne izlemek/okumak istersin?"
            ])
        
        if any(x in prompt_lower for x in ['film öner', 'dizi öner', 'kitap öner', 'ne izle', 'ne oku']):
            return "Tabii! 🎯 Hangi türde bir şey istersin? Komedi, aksiyon, romantik, korku... Ruh haline göre de önerebilirim!"
        
        if any(x in prompt_lower for x in ['üzgün', 'mutsuz', 'kötü', 'moral']):
            return "Üzgün olduğunu duyduğuma üzüldüm 😔 Ama endişelenme, seni neşelendirecek harika komediler var! Bir tane önereyim mi?"
        
        if any(x in prompt_lower for x in ['teşekkür', 'sağol', 'eyvallah']):
            return random.choice([
                "Rica ederim! 😊 Başka bir şey ister misin?",
                "Ne demek! Yardımcı olabildiysem ne mutlu bana! 🎉"
            ])
        
        return "Hmm, tam anlayamadım ama yardımcı olmaya çalışayım! 🤔 Film, dizi veya kitap önerisi istersen söyle, ya da başka bir sorun varsa onu da konuşabiliriz."

    def process_message(self, message: str, kullanici_id: int, db: Session) -> Dict:
        try:
            kullanici = db.query(Kullanici).filter(Kullanici.id == kullanici_id).first()
            if not kullanici:
                return self._create_response("Kullanıcı bulunamadı.", "error")
            
            message_lower = message.lower()
            is_recommendation_request = any(x in message_lower for x in [
                'öner', 'tavsiye', 'izle', 'oku', 'film', 'dizi', 'kitap',
                'ne izleyeyim', 'ne okuyayım', 'sıkıldım', 'bir şey bul'
            ])
            
            # Get AI response
            ai_response = self._call_gemini_api(message, kullanici_id)
            
            # Get recommendation if needed
            recommended_content = None
            if is_recommendation_request:
                content = self._get_smart_recommendation(message_lower, kullanici_id, db)
                if content:
                    recommended_content = {
                        "id": content.id,
                        "baslik": content.baslik,
                        "tur": content.tur,
                        "kategoriler": content.kategoriler,
                        "ozet": content.ozet,
                        "yil": content.yil,
                        "imdb_puani": content.imdb_puani,
                        "poster_url": content.poster_url
                    }
            
            return {
                "bot_response": ai_response,
                "response_type": "recommendation" if recommended_content else "general",
                "recommended_content": recommended_content,
                "explanation": None
            }
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return self._create_response("Bir hata oluştu, tekrar dener misin? 😅", "error")

    def _get_smart_recommendation(self, message: str, kullanici_id: int, db: Session) -> Optional[Icerik]:
        try:
            # Determine content type
            tur = None
            if 'film' in message:
                tur = 'Film'
            elif 'dizi' in message:
                tur = 'Dizi'
            elif 'kitap' in message:
                tur = 'Kitap'
            
            # Determine category
            kategori = None
            kategori_map = {
                'komedi': 'Comedy', 'aksiyon': 'Action', 'romantik': 'Romance',
                'korku': 'Horror', 'bilim kurgu': 'Science Fiction', 'dram': 'Drama',
                'gerilim': 'Thriller', 'animasyon': 'Animation', 'macera': 'Adventure'
            }
            
            for tr_kat, en_kat in kategori_map.items():
                if tr_kat in message:
                    kategori = en_kat
                    break
            
            # Mood-based category
            if any(x in message for x in ['üzgün', 'mutsuz', 'kötü', 'moral']):
                kategori = 'Comedy'
            elif any(x in message for x in ['heyecan', 'aksiyon', 'adrenalin']):
                kategori = 'Action'
            elif any(x in message for x in ['romantik', 'aşk', 'sevgi']):
                kategori = 'Romance'
            
            # Build query
            query = db.query(Icerik).filter(Icerik.imdb_puani >= 6.5)
            
            if tur:
                query = query.filter(Icerik.tur == tur)
            
            if kategori:
                query = query.filter(Icerik.kategoriler.like(f'%{kategori}%'))
            
            # Exclude already rated content
            rated_ids = [p.icerik_id for p in db.query(Puan).filter(Puan.kullanici_id == kullanici_id).all()]
            if rated_ids:
                query = query.filter(~Icerik.id.in_(rated_ids))
            
            # Get candidates
            candidates = query.order_by(Icerik.imdb_puani.desc()).limit(20).all()
            
            if candidates:
                return random.choice(candidates)
            
            # Fallback to top rated
            return db.query(Icerik).filter(Icerik.imdb_puani >= 7.0).order_by(Icerik.imdb_puani.desc()).first()
            
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return None

    def _create_response(self, text: str, response_type: str) -> Dict:
        return {
            "bot_response": text,
            "response_type": response_type,
            "recommended_content": None,
            "explanation": None
        }

    def clear_history(self, user_id: int):
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

gemini_chatbot = GeminiChatbot()