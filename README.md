
# TIGRAI - Yapay Zeka Destekli Kişiselleştirilmiş İçerik Öneri Sistemi
TIGRAI, dijital içerik tüketicilerinin hızla artan veri yığınları arasında kaybolmasını önlemek ve kişiselleştirilmiş bir keşif deneyimi sunmak amacıyla geliştirilmiş bütünleşik bir öneri sistemidir[span_1](start_span)[span_1](end_span). Geleneksel sistemlerin aksine sadece "bunu izledin, şunu da izle" demez; kullanıcının doğal dilde sorduğu soruları veritabanındaki yapısal verilerle analiz ederek anlamlı yanıtlar verir[span_2](start_span)[span_2](end_span).

Bu proje, Fırat Üniversitesi Teknoloji Fakültesi Yapay Zeka ve Veri Mühendisliği Bölümü "Veritabanı Yönetim Sistemleri" dersi kapsamında geliştirilmiştir[span_3](start_span)[span_3](end_span).

##  Temel Özellikler

* **Dinamik Kütüphane:** Kullanıcıların izledikleri veya okudukları içerikleri puanlayıp arşivleyebilmesi[span_4](start_span)[span_4](end_span).
* **Akıllı Arama:** Doğal dil sorgularını anlayarak içerik arayabilme (Örn: "Hafta sonu izlenecek kısa komedi dizisi")[span_5](start_span)[span_5](end_span).
* **Kişiselleştirilmiş Öneri:** Kullanıcı zevklerini analiz eden hibrit algoritma ile anasayfada özel listeler oluşturulması[span_6](start_span)[span_6](end_span).
* **Chatbot Asistan:** İçerikler hakkında sohbet edilebilen, RAG mimarisi ile desteklenmiş yapay zeka modülü[span_7](start_span)[span_7](end_span).

## Kullanılan Teknolojiler ve Mimari

Proje, Katmanlı Mimari (Layered Architecture) prensibi ile geliştirilmiş olup modüler bir yapıya sahiptir[span_8](start_span)[span_8](end_span).

* **Frontend (Sunum Katmanı):** Android ve iOS destekli mobil arayüz için Flutter kullanılmıştır[span_9](start_span)[span_9](end_span). Ekranlar arası geçişlerde "Hero Animation" ile sinematik bir deneyim sağlanmış ve durum yönetimi için "Provider" paketi tercih edilmiştir[span_10](start_span)[span_10](end_span).
* **Backend (Servis Katmanı):** Yüksek performanslı asenkron işlemleri destekleyen Python tabanlı FastAPI framework'ü kullanılmıştır[span_11](start_span)[span_11](end_span).
* **Veritabanı (Veri Katmanı):** Veri saklamak için SQLite ilişkisel veritabanı, vektör aramaları için ise FAISS (Facebook AI Similarity Search) vektör veritabanı entegre edilmiştir[span_12](start_span)[span_12](end_span). Veri erişim işlemleri SQLAlchemy ORM ile soyutlanmıştır[span_13](start_span)[span_13](end_span).
* **Yapay Zeka (İş Katmanı):** 
  * Kosinüs Benzerliği (Cosine Similarity) mantığı ile çalışan TensorFlow/Scikit-learn tabanlı hibrit bir öneri motoru (İşbirlikçi ve İçerik Bazlı Filtreleme) geliştirilmiştir[span_14](start_span)[span_14](end_span).
  * NLP işlemleri için `sentence-transformers` kullanılarak vektörel dönüşüm yapılmıştır[span_15](start_span)[span_15](end_span).
  * RAG (Retrieval-Augmented Generation) mimarisi kurularak Groq API üzerinden Llama-3 modeliyle entegrasyon sağlanmıştır[span_16](start_span)[span_16](end_span).

## Veritabanı ve Veri Seti

Veri bütünlüğünü sağlamak ve sorgu performansını artırmak amacıyla veritabanı 3. Normal Form (3NF) kurallarına göre normalize edilmiştir[span_17](start_span)[span_17](end_span).

* **Veri Kaynağı:** The Movies Dataset, Netflix Shows ve Goodreads Books veri setleri birleştirilmiştir[span_18](start_span)[span_18](end_span).
* **Kapasite:** Sistemde 42.330 film (%76), 10.692 kitap (%19) ve 2.867 dizi (%5) verisi bulunmaktadır[span_19](start_span)[span_19](end_span).
* **Optimizasyon:** Sorgu maliyetlerini düşürmek için Full-Text Search, ilişkisel bütünlük (JOIN) ve istatistiksel hesaplamalar üzerine B-Tree indeksleme stratejileri uygulanmıştır[span_20](start_span)[span_20](end_span).
* **Tablolar:** Sistem 6 temel tablodan oluşur: `kullanicilar`, `icerikler`, `puanlar`, `yorumlar`, `chat_history` ve `password_reset_tokens`[span_21](start_span)[span_21](end_span).

## Geliştirici Bilgileri

* **Geliştirici:** Aleyna DEMİR
* **Kurum:** Fırat Üniversitesi, Yapay Zeka ve Veri Mühendisliği
