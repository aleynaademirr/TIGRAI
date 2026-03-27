import os
import pickle
import numpy as np
from tqdm import tqdm
from database import SessionLocal, Icerik
from rag_service import create_content_text, get_sentence_transformer
def build_rag_index():
    print("=" * 60)
    print("RAG INDEX OLUŞTURULUYOR")
    print("=" * 60)
    print("\n[1/4] Embedding model yükleniyor...")
    model = get_sentence_transformer()
    if model is None:
        print("❌ Model yüklenemedi!")
        return False
    print("\n[2/4] Veritabanından içerikler okunuyor...")
    db = SessionLocal()
    icerikler = db.query(Icerik).all()
    print(f"✅ {len(icerikler)} içerik bulundu")
    print("\n[3/4] Metinler hazırlanıyor...")
    texts = []
    metadata = []
    for icerik in tqdm(icerikler, desc="İçerikler işleniyor"):
        text = create_content_text(icerik)
        texts.append(text)
        metadata.append({
            "icerik_id": icerik.id,
            "baslik": icerik.baslik,
            "tur": icerik.tur,
            "kategoriler": icerik.kategoriler,
            "yil": icerik.yil,
            "imdb_puani": icerik.imdb_puani
        })
    db.close()
    print("\n[4/4] Embeddings oluşturuluyor (bu biraz zaman alabilir)...")
    batch_size = 32
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Batch processing"):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        all_embeddings.append(batch_embeddings)
    embeddings = np.vstack(all_embeddings).astype('float32')
    print(f"✅ {embeddings.shape[0]} embedding oluşturuldu (Boyut: {embeddings.shape[1]})")
    print("\n[5/5] FAISS index oluşturuluyor...")
    try:
        import faiss
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        faiss.write_index(index, "rag_index.faiss")
        print(f"✅ Index kaydedildi: rag_index.faiss ({index.ntotal} vektör)")
        with open("rag_metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✅ Metadata kaydedildi: rag_metadata.pkl")
        index_size = os.path.getsize("rag_index.faiss") / (1024 * 1024)
        meta_size = os.path.getsize("rag_metadata.pkl") / (1024 * 1024)
        print(f"\n📊 Dosya Boyutları:")
        print(f"   Index: {index_size:.2f} MB")
        print(f"   Metadata: {meta_size:.2f} MB")
        print(f"   Toplam: {index_size + meta_size:.2f} MB")
        print("\n" + "=" * 60)
        print("✅ RAG INDEX BAŞARIYLA OLUŞTURULDU!")
        print("=" * 60)
        print("\nArtık chatbot semantik arama yapabilir! 🚀")
        return True
    except Exception as e:
        print(f"❌ FAISS index oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
if __name__ == "__main__":
    success = build_rag_index()
    if success:
        print("\n🧪 Hızlı test yapılıyor...")
        from rag_service import search_similar_content
        test_query = "bilim kurgu uzay filmi"
        results = search_similar_content(test_query, top_k=3)
        print(f"\nTest Sorgusu: '{test_query}'")
        print("Sonuçlar:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['baslik']} ({r['tur']}) - Score: {r['score']:.3f}")