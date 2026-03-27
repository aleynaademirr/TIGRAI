
# TIGRAI - Yapay Zeka Destekli Kişiselleştirilmiş İçerik Öneri Sistemi
TIGRAI, dijital içerik tüketicilerinin hızla artan veri yığınları arasında kaybolmasını önlemek ve kişiselleştirilmiş bir keşif deneyimi sunmak amacıyla geliştirilmiş bütünleşik bir öneri sistemidir. Geleneksel sistemlerin aksine sadece "bunu izledin, şunu da izle" demez; kullanıcının doğal dilde sorduğu soruları veritabanındaki yapısal verilerle analiz ederek anlamlı yanıtlar verir.

Bu proje, Fırat Üniversitesi Teknoloji Fakültesi Yapay Zeka ve Veri Mühendisliği Bölümü "Veritabanı Yönetim Sistemleri" dersi kapsamında geliştirilmiştir.

##  Temel Özellikler

* **Dinamik Kütüphane:** Kullanıcıların izledikleri veya okudukları içerikleri puanlayıp arşivleyebilmesi.
* **Akıllı Arama:** Doğal dil sorgularını anlayarak içerik arayabilme (Örn: "Hafta sonu izlenecek kısa komedi dizisi").
* **Kişiselleştirilmiş Öneri:** Kullanıcı zevklerini analiz eden hibrit algoritma ile anasayfada özel listeler oluşturulması.
* **Chatbot Asistan:** İçerikler hakkında sohbet edilebilen, RAG mimarisi ile desteklenmiş yapay zeka modülü.

## Kullanılan Teknolojiler ve Mimari

Proje, Katmanlı Mimari (Layered Architecture) prensibi ile geliştirilmiş olup modüler bir yapıya sahiptir.

* **Frontend (Sunum Katmanı):** Android ve iOS destekli mobil arayüz için Flutter kullanılmıştır. Ekranlar arası geçişlerde "Hero Animation" ile sinematik bir deneyim sağlanmış ve durum yönetimi için "Provider" paketi tercih edilmiştir.
* **Backend (Servis Katmanı):** Yüksek performanslı asenkron işlemleri destekleyen Python tabanlı FastAPI framework'ü kullanılmıştır.
* **Veritabanı (Veri Katmanı):** Veri saklamak için SQLite ilişkisel veritabanı, vektör aramaları için ise FAISS (Facebook AI Similarity Search) vektör veritabanı entegre edilmiştir. Veri erişim işlemleri SQLAlchemy ORM ile soyutlanmıştır.
* **Yapay Zeka (İş Katmanı):** 
  * Kosinüs Benzerliği (Cosine Similarity) mantığı ile çalışan TensorFlow/Scikit-learn tabanlı hibrit bir öneri motoru (İşbirlikçi ve İçerik Bazlı Filtreleme) geliştirilmiştir.
  * NLP işlemleri için `sentence-transformers` kullanılarak vektörel dönüşüm yapılmıştır.
  * RAG (Retrieval-Augmented Generation) mimarisi kurularak Groq API üzerinden Llama-3 modeliyle entegrasyon sağlanmıştır.

## Veritabanı ve Veri Seti

Veri bütünlüğünü sağlamak ve sorgu performansını artırmak amacıyla veritabanı 3. Normal Form (3NF) kurallarına göre normalize edilmiştir.

* **Veri Kaynağı:** The Movies Dataset, Netflix Shows ve Goodreads Books veri setleri birleştirilmiştir.
* **Kapasite:** Sistemde 42.330 film (%76), 10.692 kitap (%19) ve 2.867 dizi (%5) verisi bulunmaktadır.
* **Optimizasyon:** Sorgu maliyetlerini düşürmek için Full-Text Search, ilişkisel bütünlük (JOIN) ve istatistiksel hesaplamalar üzerine B-Tree indeksleme stratejileri uygulanmıştır.
* **Tablolar:** Sistem 6 temel tablodan oluşur: `kullanicilar`, `icerikler`, `puanlar`, `yorumlar`, `chat_history` ve `password_reset_tokens`.

## Geliştirici Bilgileri

* **Geliştirici:** Aleyna DEMİR
* **Kurum:** Fırat Üniversitesi, Yapay Zeka ve Veri Mühendisliği
