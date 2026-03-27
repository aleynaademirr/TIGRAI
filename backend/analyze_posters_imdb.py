import sqlite3
import random
def detailed_analysis():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    print("=" * 80)
    print("DETAYLI POSTER VE IMDB ANALİZİ")
    print("=" * 80)
    print("\n📽️  RASTGELE 20 FİLM ÖRNEĞİ:")
    print("-" * 80)
    cursor.execute()
    for i, row in enumerate(cursor.fetchall(), 1):
        baslik, imdb, poster, yil = row
        print(f"\n{i}. {baslik} ({yil})")
        print(f"   IMDB: {imdb}")
        if poster:
            if 'placeholder' in poster.lower():
                print(f"   Poster: ❌ PLACEHOLDER")
            elif 'tmdb' in poster or 'media-amazon' in poster or 'covers.openlibrary' in poster:
                print(f"   Poster: ✅ Gerçek ({poster[:50]}...)")
            else:
                print(f"   Poster: ⚠️  Bilinmeyen ({poster[:50]}...)")
        else:
            print(f"   Poster: ❌ YOK")
    print("\n\n📺 RASTGELE 10 DİZİ ÖRNEĞİ:")
    print("-" * 80)
    cursor.execute()
    for i, row in enumerate(cursor.fetchall(), 1):
        baslik, imdb, poster, yil = row
        print(f"\n{i}. {baslik} ({yil})")
        print(f"   IMDB: {imdb}")
        if poster:
            if 'placeholder' in poster.lower():
                print(f"   Poster: ❌ PLACEHOLDER")
            elif 'tmdb' in poster or 'media-amazon' in poster or 'm.media' in poster:
                print(f"   Poster: ✅ Gerçek ({poster[:50]}...)")
            else:
                print(f"   Poster: ⚠️  Bilinmeyen ({poster[:50]}...)")
        else:
            print(f"   Poster: ❌ YOK")
    print("\n\n⭐ IMDB PUAN DAĞILIMI:")
    print("-" * 80)
    cursor.execute()
    print("Film IMDB Dağılımı:")
    for row in cursor.fetchall():
        range_val, count = row
        print(f"  {range_val}: {count} film")
    print("\n\n⚠️  ŞÜPHELİ IMDB PUANLARI:")
    print("-" * 80)
    cursor.execute()
    suspicious = cursor.fetchall()
    if suspicious:
        print("Geçersiz IMDB puanları bulundu:")
        for baslik, imdb, tur in suspicious:
            print(f"  {baslik} ({tur}): {imdb}")
    else:
        print("✅ Geçersiz IMDB puanı bulunamadı (1-10 arası)")
    conn.close()
if __name__ == "__main__":
    detailed_analysis()