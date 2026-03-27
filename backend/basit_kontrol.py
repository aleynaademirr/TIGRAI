conn = sqlite3.connect('recommendation_system.db')
cursor = conn.cursor()
print("=" * 50)
print("VERİTABANI DURUMU")
print("=" * 50)
cursor.execute("SELECT COUNT(*) FROM icerikler")
toplam = cursor.fetchone()[0]
print(f"\nToplam İçerik: {toplam}")
cursor.execute("SELECT tur, COUNT(*) FROM icerikler GROUP BY tur")
for tur, sayi in cursor.fetchall():
    print(f"  - {tur}: {sayi}")
cursor.execute("SELECT COUNT(*) FROM kullanicilar")
kullanici = cursor.fetchone()[0]
print(f"\nToplam Kullanıcı: {kullanici}")
cursor.execute("SELECT COUNT(*) FROM puanlar")
puan = cursor.fetchone()[0]
print(f"Toplam Puan: {puan}")
print("\n" + "=" * 50)
print("ÖRNEK İÇERİKLER (İlk 10)")
print("=" * 50)
cursor.execute("SELECT id, baslik, tur FROM icerikler LIMIT 10")
for id, baslik, tur in cursor.fetchall():
    print(f"{id}. [{tur}] {baslik}")
conn.close()
print("\n" + "=" * 50)
input("Devam etmek için Enter'a basın...")