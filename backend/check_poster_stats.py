from database import SessionLocal, Icerik

db = SessionLocal()

# Toplam içerikler
total_movies = db.query(Icerik).filter(Icerik.tur == 'Film').count()
total_series = db.query(Icerik).filter(Icerik.tur == 'Dizi').count()
total_books = db.query(Icerik).filter(Icerik.tur == 'Kitap').count()

# Gerçek posterli olanlar (placehold içermeyenler)
real_poster_movies = db.query(Icerik).filter(
    Icerik.tur == 'Film',
    Icerik.poster_url != None,
    Icerik.poster_url != '',
    ~Icerik.poster_url.like('%placehold%')
).count()

real_poster_series = db.query(Icerik).filter(
    Icerik.tur == 'Dizi',
    Icerik.poster_url != None,
    Icerik.poster_url != '',
    ~Icerik.poster_url.like('%placehold%')
).count()

real_poster_books = db.query(Icerik).filter(
    Icerik.tur == 'Kitap',
    Icerik.poster_url != None,
    Icerik.poster_url != '',
    ~Icerik.poster_url.like('%placehold%')
).count()

print("\n" + "="*60)
print("POSTER DURUMU")
print("="*60)
print(f"\n📽️  FİLMLER:")
print(f"   Toplam: {total_movies}")
print(f"   Gerçek Poster: {real_poster_movies} ({real_poster_movies/total_movies*100:.1f}%)")

print(f"\n📺 DİZİLER:")
print(f"   Toplam: {total_series}")
print(f"   Gerçek Poster: {real_poster_series} ({real_poster_series/total_series*100:.1f}%)")

print(f"\n📚 KİTAPLAR:")
print(f"   Toplam: {total_books}")
print(f"   Gerçek Poster: {real_poster_books} ({real_poster_books/total_books*100:.1f}%)")

print(f"\n📊 GENEL TOPLAM:")
print(f"   Toplam İçerik: {total_movies + total_series + total_books}")
print(f"   Gerçek Poster: {real_poster_movies + real_poster_series + real_poster_books}")
print("="*60 + "\n")

db.close()
