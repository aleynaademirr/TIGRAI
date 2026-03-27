from rag_service import search_similar_content, is_rag_available
def test_rag_system():
    print("=" * 60)
    print("RAG CHATBOT TEST")
    print("=" * 60)
    if not is_rag_available():
        print("\n❌ RAG sistemi hazır değil!")
        print("Lütfen önce build_rag_index.py çalıştırın.")
        return
    print("\n✅ RAG sistemi hazır!\n")
    test_queries = [
        ("uzay temalı bilim kurgu", "Film"),
        ("romantik komedi", None),
        ("Christopher Nolan filmi", "Film"),
        ("üzücü drama kitap", "Kitap"),
        ("Breaking Bad gibi dizi", "Dizi"),
        ("aksiyon filmi", "Film")
    ]
    for query, tur_filter in test_queries:
        print(f"\n🔍 Sorgu: '{query}'")
        if tur_filter:
            print(f"   Filtre: {tur_filter}")
        results = search_similar_content(query, top_k=3, tur_filter=tur_filter)
        if results:
            print(f"   ✅ {len(results)} sonuç bulundu:")
            for i, r in enumerate(results, 1):
                score_emoji = "🔥" if r['score'] > 0.7 else "✅" if r['score'] > 0.5 else "⚠️"
                print(f"      {i}. {score_emoji} {r['baslik']} ({r['tur']}) - Score: {r['score']:.3f}")
                if r.get('kategoriler'):
                    print(f"         Kategori: {r['kategoriler']}")
        else:
            print("   ❌ Sonuç bulunamadı")
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)
    print("\nChatbot artık bu içerikleri kullanarak akıllı önerilerde bulunabilir! 🚀")
if __name__ == "__main__":
    test_rag_system()