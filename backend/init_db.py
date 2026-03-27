from database import SessionLocal, Icerik, Kullanici, init_db
from sqlalchemy.orm import Session
def init_sample_data(db: Session):
    ornek_icerikler = [
        {
            : "Inception",
            : "Film",
            : "Bilim Kurgu, Aksiyon, Gerilim",
            : "Bir hırsız, insanların bilinçaltına girip fikir çalma yeteneğine sahiptir. En zor görevi: bir insanın zihnine bir fikir eklemek.",
            : 2010,
            : 8.8,
            : "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
        },
        {
            : "The Dark Knight",
            : "Film",
            : "Aksiyon, Gerilim, Dram",
            : "Batman, Joker ile savaşırken kendisini ve Gotham şehrini kurtarmaya çalışır.",
            : 2008,
            : 9.0,
            : "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
        },
        {
            : "The Shawshank Redemption",
            : "Film",
            : "Dram",
            : "Haksız yere hapse düşen bir bankacının umut ve dostluk hikayesi.",
            : 1994,
            : 9.3,
            : "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "La La Land",
            : "Film",
            : "Romantik, Komedi, Dram",
            : "Los Angeles'ta bir oyuncu ve bir müzisyen arasındaki romantik hikaye.",
            : 2016,
            : 8.0,
            : "https://m.media-amazon.com/images/M/MV5BMzUzNDM2NzM2MV5BMl5BanBnXkFtZTgwNTM3NTg4OTE@._V1_.jpg"
        },
        {
            : "Interstellar",
            : "Film",
            : "Bilim Kurgu, Dram, Macera",
            : "Dünya artık yaşanabilir değildir. Bir grup astronot insanlığı kurtarmak için yeni bir gezegen arar.",
            : 2014,
            : 8.6,
            : "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg"
        },
        {
            : "Breaking Bad",
            : "Dizi",
            : "Dram, Gerilim, Aksiyon",
            : "Lise kimya öğretmeni kanser olduğunu öğrenir ve ailesi için para kazanmak amacıyla uyuşturucu üretmeye başlar.",
            : 2008,
            : 9.5,
            : "https://m.media-amazon.com/images/M/MV5BYmQ4YWMxYjksZmJiZC00ZMjI2LWJjOTUtZDFiM2NhM2NzMmZgXkEyXkFqcGdeQXVyMTEyMjM2NDc2._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "Game of Thrones",
            : "Dizi",
            : "Fantastik, Dram, Aksiyon",
            : "Westeros'ta taht için savaşan soylu ailelerin hikayesi.",
            : 2011,
            : 9.3,
            : "https://m.media-amazon.com/images/M/MV5BN2IzYzBiOTQtNGZmMi00NDI5LTgxMzMtN2EzZjA1NjhlOGMxXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "The Office",
            : "Dizi",
            : "Komedi",
            : "Dunder Mifflin kağıt şirketinde çalışanların günlük hayatları ve komik anları.",
            : 2005,
            : 8.9,
            : "https://m.media-amazon.com/images/M/MV5BMDMzM2YwZmQtNTY0Mi00ZjczLWI5NDUtZDQ5MTcyMDI3MTg5XkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "Stranger Things",
            : "Dizi",
            : "Bilim Kurgu, Korku, Dram",
            : "1980'lerde küçük bir kasabada kaybolan bir çocuk ve gizemli olaylar.",
            : 2016,
            : 8.7,
            : "https://m.media-amazon.com/images/M/MV5BMjQxNzAwNjg5N15BMl5BanBnXkFtZTcwODQ4MzE4MQ@@._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "Friends",
            : "Dizi",
            : "Komedi, Romantik",
            : "New York'ta yaşayan altı arkadaşın komik maceraları ve hayatları.",
            : 1994,
            : 8.9,
            : "https://m.media-amazon.com/images/M/MV5BNDVkYjU0MzctMzg1YS00NzQ3LWE2Y2YtN2YxYWNmNTBmMGI3XkEyXkFqcGdeQXVyNzQ1ODk3MTQ@._V1_FMjpg_UX1000_.jpg"
        },
        {
            : "1984",
            : "Kitap",
            : "Bilim Kurgu, Gerilim, Dram",
            : "George Orwell'in distopik gelecek tasviri. Büyük Birader her yeri izliyor.",
            : 1949,
            : None,
            : "https://upload.wikimedia.org/wikipedia/commons/c/c3/1984_first_edition_cover.jpg"
        },
        {
            : "The Lord of the Rings",
            : "Kitap",
            : "Fantastik, Macera, Dram",
            : "Orta Dünya'da Yüzük Savaşı ve Frodo'nun yolculuğu.",
            : 1954,
            : None,
            : "https://upload.wikimedia.org/wikipedia/en/8/8e/The_Fellowship_of_the_Ring_cover.gif"
        },
        {
            : "Pride and Prejudice",
            : "Kitap",
            : "Romantik, Dram",
            : "Jane Austen'in 19. yüzyıl İngiltere'sinde geçen klasik aşk hikayesi.",
            : 1813,
            : None,
            : "https://m.media-amazon.com/images/I/71Q1tPupKjL._AC_UF1000,1000_QL80_.jpg"
        },
        {
            : "The Great Gatsby",
            : "Kitap",
            : "Dram, Romantik",
            : "1920'lerde zengin ve gizemli Jay Gatsby'nin hikayesi.",
            : 1925,
            : None,
            : "https://upload.wikimedia.org/wikipedia/commons/7/7a/The_Great_Gatsby_Cover_1925_Retouched.jpg"
        },
        {
            : "Harry Potter and the Philosopher's Stone",
            : "Kitap",
            : "Fantastik, Macera, Gençlik",
            : "Genç büyücü Harry Potter'ın Hogwarts'taki ilk yılı.",
            : 1997,
            : None,
            : "https://m.media-amazon.com/images/I/81q77Q39nEL._AC_UF1000,1000_QL80_.jpg"
        }
    ]
    for icerik_data in ornek_icerikler:
        mevcut_icerik = db.query(Icerik).filter(Icerik.baslik == icerik_data["baslik"]).first()
        if not mevcut_icerik:
            icerik = Icerik(**icerik_data)
            db.add(icerik)
            print(f"[+] Yeni içerik eklendi: {icerik_data['baslik']}")
        else:
            updated = False
            if icerik_data.get("poster_url") and mevcut_icerik.poster_url != icerik_data.get("poster_url"):
                mevcut_icerik.poster_url = icerik_data.get("poster_url")
                updated = True
            if icerik_data.get("imdb_puani") and not mevcut_icerik.imdb_puani:
                mevcut_icerik.imdb_puani = icerik_data.get("imdb_puani")
                updated = True
            if updated:
                print(f"[!] İçerik güncellendi: {icerik_data['baslik']}")
    db.commit()
    print(f"[OK] {len(ornek_icerikler)} örnek içerik eklendi")
def init_sample_users(db: Session):
    from auth import hash_password
    default_password_hash = hash_password("123456")
    ornek_kullanicilar = [
        {"kullanici_adi": "test_user", "email": "test@example.com", "password_hash": default_password_hash, "is_admin": 0},
        {"kullanici_adi": "demo_user", "email": "demo@example.com", "password_hash": default_password_hash, "is_admin": 0},
        {"kullanici_adi": "admin", "email": "admin@example.com", "password_hash": default_password_hash, "is_admin": 1}
    ]
    for kullanici_data in ornek_kullanicilar:
        mevcut_kullanici = db.query(Kullanici).filter(
            Kullanici.kullanici_adi == kullanici_data["kullanici_adi"]
        ).first()
        if not mevcut_kullanici:
            kullanici = Kullanici(**kullanici_data)
            db.add(kullanici)
            print(f"[+] Kullanıcı oluşturuldu: {kullanici_data['kullanici_adi']} (Şifre: 123456)")
        else:
            mevcut_kullanici.password_hash = default_password_hash
            mevcut_kullanici.is_admin = kullanici_data["is_admin"]
            print(f"[!] Kullanıcı güncellendi: {kullanici_data['kullanici_adi']} (Şifre: 123456)")
    db.commit()
    print("[OK] Örnek kullanıcılar eklendi/güncellendi")
if __name__ == "__main__":
    print("Veritabanı başlatılıyor...")
    init_db()
    db = SessionLocal()
    try:
        init_sample_data(db)
        init_sample_users(db)
        print("\n[OK] Veritabanı başarıyla hazırlandı!")
    except Exception as e:
        print(f"[ERR] Hata: {e}")
        db.rollback()
    finally:
        db.close()