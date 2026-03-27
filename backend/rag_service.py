import os
import json
import pickle
from typing import List, Dict, Tuple
import numpy as np
from sqlalchemy.orm import Session
from database import SessionLocal, Icerik
_sentence_transformer = None
_faiss_index = None
_metadata = None
def get_sentence_transformer():
    global _sentence_transformer
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            print("[RAG] Embedding model yüklendi: all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[RAG] Model yükleme hatası: {e}")
            return None
    return _sentence_transformer
def get_faiss_index():
    global _faiss_index, _metadata
    if _faiss_index is None:
        try:
            import faiss
            index_path = "rag_index.faiss"
            metadata_path = "rag_metadata.pkl"
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                _faiss_index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    _metadata = pickle.load(f)
                print(f"[RAG] Index yüklendi: {_faiss_index.ntotal} içerik")
            else:
                print("[RAG] Index bulunamadı. build_rag_index.py çalıştırın.")
                return None, None
        except Exception as e:
            print(f"[RAG] Index yükleme hatası: {e}")
            return None, None
    return _faiss_index, _metadata
def create_content_text(icerik: Icerik) -> str:
    parts = [
        f"Başlık: {icerik.baslik}",
        f"Tür: {icerik.tur}",
    ]
    if icerik.kategoriler:
        parts.append(f"Kategoriler: {icerik.kategoriler}")
    if icerik.ozet:
        ozet = icerik.ozet[:500] if len(icerik.ozet) > 500 else icerik.ozet
        parts.append(f"Özet: {ozet}")
    if icerik.yil:
        parts.append(f"Yıl: {icerik.yil}")
    if icerik.imdb_puani:
        parts.append(f"IMDB: {icerik.imdb_puani}")
    return " | ".join(parts)
def search_similar_content(
    query: str, 
    top_k: int = 5,
    tur_filter: str = None
) -> List[Dict]:
    model = get_sentence_transformer()
    index, metadata = get_faiss_index()
    if model is None or index is None or metadata is None:
        print("[RAG] Sistem hazır değil")
        return []
    try:
        query_vector = model.encode([query])[0].astype('float32')
        query_vector = np.expand_dims(query_vector, axis=0)
        distances, indices = index.search(query_vector, top_k * 3)  
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= len(metadata):
                continue
            meta = metadata[idx]
            if tur_filter and meta['tur'] != tur_filter:
                continue
            score = 1 / (1 + dist)  
            results.append({
                "icerik_id": meta['icerik_id'],
                "baslik": meta['baslik'],
                "tur": meta['tur'],
                "kategoriler": meta.get('kategoriler', ''),
                "yil": meta.get('yil'),
                "imdb_puani": meta.get('imdb_puani'),
                "score": float(score)
            })
            if len(results) >= top_k:
                break
        return results
    except Exception as e:
        print(f"[RAG] Arama hatası: {e}")
        return []
def get_rag_context_for_llm(query: str, top_k: int = 5) -> str:
    results = search_similar_content(query, top_k=top_k)
    if not results:
        return ""
    context_parts = ["İlgili İçerikler (Veritabanından):"]
    for i, item in enumerate(results, 1):
        parts = [f"{i}. {item['baslik']} ({item['tur']})"]
        if item.get('kategoriler'):
            parts.append(f"Kategori: {item['kategoriler']}")
        if item.get('yil'):
            parts.append(f"Yıl: {item['yil']}")
        if item.get('imdb_puani'):
            parts.append(f"IMDB: {item['imdb_puani']}")
        parts.append(f"Alakalılık: {item['score']:.2f}")
        context_parts.append(" | ".join(parts))
    return "\n".join(context_parts)
def is_rag_available() -> bool:
    try:
        model = get_sentence_transformer()
        index, metadata = get_faiss_index()
        return model is not None and index is not None and metadata is not None
    except:
        return False
if __name__ == "__main__":
    print("RAG Sistemi Test Ediliyor...")
    if not is_rag_available():
        print("❌ RAG sistemi hazır değil. build_rag_index.py çalıştırın.")
    else:
        print("✅ RAG sistemi hazır!")
        test_queries = [



        ]
        for query in test_queries:
            print(f"\n🔍 Sorgu: '{query}'")
            results = search_similar_content(query, top_k=3)
            for r in results:
                print(f"  - {r['baslik']} ({r['tur']}) - Score: {r['score']:.3f}")