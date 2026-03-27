def check_urls():
    conn = sqlite3.connect('recommendation_system.db')
    cursor = conn.cursor()
    types = ['Film', 'Dizi', 'Kitap']
    with open('poster_log.txt', 'w', encoding='utf-8') as f:
        f.write("--- POSTER URL KONTROLU ---\n\n")
        for t in types:
            f.write(f"[{t} Örnekleri]\n")
            cursor.execute("SELECT COUNT(*) FROM icerikler WHERE tur=? AND poster_url IS NOT NULL", (t,))
            count = cursor.fetchone()[0]
            cursor.execute("SELECT baslik, poster_url FROM icerikler WHERE tur=? AND poster_url IS NOT NULL LIMIT 5", (t,))
            samples = cursor.fetchall()
            f.write(f"Toplam {t} sayısı: {count}\n")
            if samples:
                for title, url in samples:
                    f.write(f"  - {title}: {url}\n")
            else:
                f.write("  (Örnek bulunamadı)\n")
            f.write("-" * 30 + "\n")
    conn.close()
    print("Log dosyası oluşturuldu.")
if __name__ == "__main__":
    check_urls()