from database import SessionLocal, Icerik, init_db
from sqlalchemy.orm import Session
def create_large_dataset(db: Session):
    filmler = [
        {
            : "The Matrix",
            : "Film",
            : "Bilim Kurgu, Aksiyon",
            : "Bir bilgisayar programcısı, gerçek dünyanın aslında bir simülasyon olduğunu keşfeder. Neo adlı karakter, Morpheus'un rehberliğinde Matrix'in gerçek doğasını öğrenir ve insanlığın kurtuluşu için savaşır. Zihin-beden ayrımı, gerçeklik algısı ve özgür irade gibi derin felsefi temaları işleyen bir başyapıt.",
            : 1999,
            : 8.7,
            : "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
        },
        {
            : "Inception",
            : "Film",
            : "Bilim Kurgu, Aksiyon, Gerilim",
            : "Bir hırsız, insanların bilinçaltına girip fikir çalma yeteneğine sahiptir. En zor görevi: bir insanın zihnine bir fikir eklemek. Rüya içinde rüya konseptiyle gerçeklik algısını sorgulayan, zihin-bükücü bir bilim kurgu başyapıtı. Her seyirde yeni detaylar keşfedilen, katmanlı bir anlatı.",
            : 2010,
            : 8.8,
            : "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
        },
        {
            : "The Dark Knight",
            : "Film",
            : "Aksiyon, Gerilim, Dram",
            : "Batman, Joker ile savaşırken kendisini ve Gotham şehrini kurtarmaya çalışır. Ahlak, adalet ve kaos arasındaki çizgiyi sorgulayan, karanlık ve derin bir süper kahraman hikayesi. Heath Ledger'ın unutulmaz Joker performansıyla sinema tarihine geçen bir yapım.",
            : 2008,
            : 9.0,
            : "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
        },
        {
            : "Pulp Fiction",
            : "Film",
            : "Suç, Dram",
            : "Los Angeles'ta birbirine bağlı birkaç suç hikayesi. Non-linear anlatımıyla sinema tarihini değiştiren, kült bir başyapıt. Tarantino'nun imza stilini yansıtan diyaloglar, şiddet ve mizahın mükemmel dengesi.",
            : 1994,
            : 8.9,
            : "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"
        },
        {
            : "Interstellar",
            : "Film",
            : "Bilim Kurgu, Dram, Macera",
            : "Dünya artık yaşanabilir değildir. Bir grup astronot insanlığı kurtarmak için yeni bir gezegen arar. Zaman, uzay ve sevgi arasındaki ilişkiyi sorgulayan, görsel olarak nefes kesen bir bilim kurgu destanı. Nolan'ın en iddialı projelerinden biri.",
            : 2014,
            : 8.6,
            : "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
        },
        {
            : "The Shawshank Redemption",
            : "Film",
            : "Dram",
            : "Haksız yere hapse düşen bir bankacının umut ve dostluk hikayesi. İnsan ruhunun dayanıklılığını, umudun gücünü ve gerçek özgürlüğün ne olduğunu anlatan zamansız bir başyapıt. IMDB'nin en yüksek puanlı filmi.",
            : 1994,
            : 9.3,
            : "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
        },
        {
            : "Fight Club",
            : "Film",
            : "Dram, Gerilim",
            : "Uykusuzluk çeken bir ofis çalışanı, bir sabun satıcısıyla tanışır ve yeraltı dövüş kulübü kurar. Tüketim toplumu, kimlik ve isyan üzerine sert bir eleştiri. Sonu şok edici bir twist ile biten, kült bir film.",
            : 1999,
            : 8.8,
            : "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
        },
        {
            : "Forrest Gump",
            : "Film",
            : "Dram, Romantik",
            : "Düşük IQ'lu bir adamın hayatı, Amerikan tarihinin önemli olaylarıyla kesişir. Umut, sevgi ve hayatın güzelliklerini anlatan dokunaklı bir hikaye. Tom Hanks'in unutulmaz performansı.",
            : 1994,
            : 8.8,
            : "https://image.tmdb.org/t/p/w500/arw2vcBve0OVzpa1n3Rmr4xqTOx.jpg"
        },
        {
            : "The Godfather",
            : "Film",
            : "Suç, Dram",
            : "Mafya ailesinin patriği, en küçük oğlunu işe dahil eder. Güç, aile ve sadakat arasındaki ilişkiyi anlatan sinema tarihinin en büyük başyapıtlarından biri. Brando ve Pacino'nun efsanevi performansları.",
            : 1972,
            : 9.2,
            : "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"
        },
        {
            : "The Lord of the Rings: The Return of the King",
            : "Film",
            : "Fantastik, Macera, Dram",
            : "Frodo ve Sam, Yüzük'ü yok etmek için Mordor'a doğru yolculuğa devam eder. Orta Dünya'nın kaderi tehlikededir. Görsel efektler, hikaye anlatımı ve karakter gelişimi açısından mükemmel bir epik.",
            : 2003,
            : 9.0,
            : "https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg"
        },
    ]
    diziler = [
        {
            : "Breaking Bad",
            : "Dizi",
            : "Dram, Gerilim, Aksiyon",
            : "Lise kimya öğretmeni kanser olduğunu öğrenir ve ailesi için para kazanmak amacıyla uyuşturucu üretmeye başlar. İyi bir adamın kötüye dönüşümünü anlatan, karakter gelişimi açısından mükemmel bir dizi. Her bölümü sinema kalitesinde.",
            : 2008,
            : 9.5,
            : "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg"
        },
        {
            : "Game of Thrones",
            : "Dizi",
            : "Fantastik, Dram, Aksiyon",
            : "Westeros'ta taht için savaşan soylu ailelerin hikayesi. Güç, entrika ve savaşın iç içe geçtiği, karakterlerin beklenmedik şekilde öldüğü cesur bir anlatı. Dünya çapında fenomen olmuş bir dizi.",
            : 2011,
            : 9.3,
            : "https://image.tmdb.org/t/p/w500/u3bZgnGQ9T01sWNhyveQz0wH0Hl.jpg"
        },
        {
            : "The Office",
            : "Dizi",
            : "Komedi",
            : "Dunder Mifflin kağıt şirketinde çalışanların günlük hayatları ve komik anları. Mockumentary tarzında çekilmiş, karakterlerin gerçekçi ve komik etkileşimlerini gösteren bir komedi başyapıtı.",
            : 2005,
            : 8.9,
            : "https://image.tmdb.org/t/p/w500/7DJKqjGxqH7xOPzVHyXhKz1FfUS.jpg"
        },
        {
            : "Stranger Things",
            : "Dizi",
            : "Bilim Kurgu, Korku, Dram",
            : "1980'lerde küçük bir kasabada kaybolan bir çocuk ve gizemli olaylar. Nostalji, bilim kurgu ve korku öğelerini harmanlayan, karakter odaklı bir hikaye. 80'ler pop kültürüne saygı duruşu.",
            : 2016,
            : 8.7,
            : "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg"
        },
        {
            : "Friends",
            : "Dizi",
            : "Komedi, Romantik",
            : "New York'ta yaşayan altı arkadaşın komik maceraları ve hayatları. 90'ların en ikonik dizisi, dostluk ve aşk temalarını işleyen zamansız bir komedi. Herkesin kendinden bir şeyler bulabileceği karakterler.",
            : 1994,
            : 8.9,
            : "https://image.tmdb.org/t/p/w500/f496cm9enuEsZkSPzCwnTESEK5s.jpg"
        },
    ]
    kitaplar = [
        {
            : "1984",
            : "Kitap",
            : "Bilim Kurgu, Gerilim, Dram",
            : "George Orwell'in distopik gelecek tasviri. Büyük Birader her yeri izliyor. Totaliter rejim, düşünce kontrolü ve özgürlük kavramlarını sorgulayan, güncelliğini hiç yitirmeyen bir başyapıt. 'Big Brother is watching you' ifadesi buradan gelir.",
            : 1949,
            : None,
            : "https://covers.openlibrary.org/b/id/7222241-L.jpg"
        },
        {
            : "The Lord of the Rings",
            : "Kitap",
            : "Fantastik, Macera, Dram",
            : "Orta Dünya'da Yüzük Savaşı ve Frodo'nun yolculuğu. Modern fantastik edebiyatın temelini atan, zengin dünya yapısı ve derin karakterlerle dolu bir epik. Tolkien'in yarattığı evren hala en detaylı fantastik dünyalardan biri.",
            : 1954,
            : None,
            : "https://covers.openlibrary.org/b/id/6979861-L.jpg"
        },
        {
            : "Pride and Prejudice",
            : "Kitap",
            : "Romantik, Dram",
            : "Jane Austen'in 19. yüzyıl İngiltere'sinde geçen klasik aşk hikayesi. Elizabeth Bennet ve Mr. Darcy'nin önyargılarını aşarak buluşan hikayesi. Toplumsal sınıf, evlilik ve kadın hakları üzerine keskin gözlemler.",
            : 1813,
            : None,
            : "https://covers.openlibrary.org/b/id/8304531-L.jpg"
        },
    ]
    all_contents = filmler + diziler + kitaplar
    imported = 0
    skipped = 0
    for content_data in all_contents:
        mevcut = db.query(Icerik).filter(Icerik.baslik == content_data["baslik"]).first()
        if mevcut:
            skipped += 1
            continue
        icerik = Icerik(**content_data)
        db.add(icerik)
        imported += 1
    db.commit()
    print(f"[OK] {imported} içerik eklendi, {skipped} atlandı")
    return imported
if __name__ == "__main__":
    print("Geniş veri seti oluşturuluyor...")
    init_db()
    db = SessionLocal()
    try:
        create_large_dataset(db)
        total = db.query(Icerik).count()
        print(f"\n[OK] Toplam {total} içerik veritabanında!")
    except Exception as e:
        print(f"[ERR] Hata: {e}")
        db.rollback()
    finally:
        db.close()