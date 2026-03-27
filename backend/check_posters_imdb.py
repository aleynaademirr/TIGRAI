import sqlite3
def check_posters_and_ratings():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    print("=" * 60)
    print("POSTER VE IMDB KONTROL RAPORU")
    print("=" * 60)
    cursor.execute("SELECT COUNT(*) FROM icerikler")
    total = cursor.fetchone()[0]
    print(f"\nToplam İçerik: {total}")
    cursor.execute()
    placeholder_count = cursor.fetchone()[0]
    print(f"Placeholder Poster: {placeholder_count} ({placeholder_count/total*100:.1f}%)")
    real_posters = total - placeholder_count
    print(f"Gerçek Poster: {real_posters} ({real_posters/total*100:.1f}%)")
    cursor.execute("SELECT COUNT(*) FROM icerikler WHERE imdb_puani IS NOT NULL")
    with_rating = cursor.fetchone()[0]
    print(f"\nIMDB Puanı Olan: {with_rating} ({with_rating/total*100:.1f}%)")
    cursor.execute("SELECT COUNT(*) FROM icerikler WHERE imdb_puani IS NULL")
    without_rating = cursor.fetchone()[0]
    print(f"IMDB Puanı Olmayan: {without_rating} ({without_rating/total*100:.1f}%)")
    print("\n" + "=" * 60)
    print("ÖRNEK POSTER URL'LERİ (İlk 10)")
    print("=" * 60)
    cursor.execute()
    for row in cursor.fetchall():
        baslik, tur, poster, imdb = row
        poster_status = "✅ Gerçek" if poster and "placeholder" not in poster.lower() else "❌ Placeholder"
        imdb_status = f"⭐ {imdb}" if imdb else "❌ Yok"
        print(f"\n{baslik[:40]} ({tur})")
        print(f"  Poster: {poster_status}")
        print(f"  IMDB: {imdb_status}")
        if poster:
            print(f"  URL: {poster[:60]}...")
    print("\n" + "=" * 60)
    print("TÜR BAZINDA İSTATİSTİK")
    print("=" * 60)
    for tur in ['Film', 'Dizi', 'Kitap']:
        cursor.execute(f"SELECT COUNT(*) FROM icerikler WHERE tur = '{tur}'")
        tur_total = cursor.fetchone()[0]
        cursor.execute(f)
        tur_placeholder = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM icerikler WHERE tur = '{tur}' AND imdb_puani IS NOT NULL")
        tur_with_rating = cursor.fetchone()[0]
        print(f"\n{tur}:")
        print(f"  Toplam: {tur_total}")
        print(f"  Gerçek Poster: {tur_total - tur_placeholder} ({(tur_total-tur_placeholder)/tur_total*100:.1f}%)")
        print(f"  IMDB Puanı: {tur_with_rating} ({tur_with_rating/tur_total*100:.1f}%)")
    conn.close()
if __name__ == "__main__":
    check_posters_and_ratings()