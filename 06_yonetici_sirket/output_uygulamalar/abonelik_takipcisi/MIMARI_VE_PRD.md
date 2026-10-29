# 📌 Abonelik ve Gider Takipçisi — Ürün & Mimari Şartnamesi

**Uygulama Tipi:** Streamlit Web App
**Teknoloji Yığını:** Python 3.12, Streamlit, SQLite3, Pandas, Plotly
**Veritabanı:** SQLite3 yerel veritabanı, basitliği ve kurulum gerektirmemesi nedeniyle tercih edilmiştir.

---

## 1. Ürün Şartnamesi (PRD)
# Abonelik Takipçisi PRD

## Kullanıcı Hikayeleri
- Bir kullanıcı olarak, yeni bir aboneliğimi (ad, fiyat, kategori, yenilenme tarihi) sisteme kaydedebilmeliyim.
- Bir kullanıcı olarak, tüm aboneliklerimi listeleyebilmeli ve artık kullanmadığım abonelikleri silebilmeliyim.
- Bir kullanıcı olarak, aylık toplam ne kadar ödediğimi tek bir özet kutusunda görmeliyim.

## Veri Modeli (SQLite3)
- Table: subscriptions (id, name, amount, category, renewal_date)

## Başlangıç Verileri (Seed Data)
- ('Netflix', 150.0, 'Eğlence', '2023-11-15')
- ('Spotify', 40.0, 'Eğlence', '2023-11-20')
- ('Google One', 30.0, 'Bulut', '2023-12-01')
- ('GitHub Pro', 120.0, 'Yazılım', '2023-11-25')

## Kabul Kriterleri
- Uygulama başlatıldığında veritabanı yoksa otomatik oluşturulmalı ve seed data eklenmelidir.
- Streamlit arayüzünde 'Toplam Aylık Gider' kartı her işlemden sonra güncellenmelidir.
- Kategori bazlı grafik, Plotly kütüphanesi kullanılarak interaktif olarak sunulmalıdır.

---

## 2. Sistem Mimarisi
### Sistem Mimarisi ve Modül Sözleşmesi | 1. database.py: Veritabanı bağlantısını ve CRUD işlemlerini yönetir. Export: init_db(), add_subscription(data), get_all_subscriptions(), delete_subscription(id). | 2. services.py: İş mantığı ve hesaplamaları içerir. Export: calculate_monthly_total(df), get_category_distribution(df), get_upcoming_payments(df). | 3. app.py: Streamlit arayüzü ve kullanıcı etkileşimi. | Hata Yönetimi: Tüm veritabanı işlemleri try-except blokları ile sarılmalı ve kullanıcıya st.error ile bildirilmelidir. | Veri Şeması: subscriptions tablosu (id INTEGER PRIMARY KEY, name TEXT, amount REAL, category TEXT, renewal_date DATE).

---

## 3. QA & Güvenlik Raporu
### QA ve Güvenlik Denetim Raporu

**Genel Değerlendirme:**
Kod tabanı, PRD'de belirtilen tüm temel gereksinimleri (CRUD, finansal hesaplamalar, görselleştirme ve ödeme takibi) başarıyla karşılamaktadır. Modüler yapı (database, services, app) temiz ve sürdürülebilir bir mimari sunmaktadır.

**Özellik Kapsamı:**
- **CRUD İşlemleri:** `database.py` içerisinde SQLite3 ile tam CRUD desteği sağlanmıştır. `app.py` üzerinde ekleme ve silme arayüzleri mevcuttur.
- **Finansal Hesaplamalar:** `services.py` içerisinde aylık ve yıllık toplamlar doğru mantıkla hesaplanmaktadır.
- **Görselleştirme:** `plotly` kullanılarak kategori bazlı pasta grafiği başarıyla entegre edilmiştir.
- **Ödeme Takibi:** `get_upcoming_payments` fonksiyonu ile tarihe göre sıralama ve filtreleme mantığı doğru kurulmuştur.

**Güvenlik ve Kod Kalitesi:**
- Veritabanı işlemleri `try-except` blokları ile korunmuştur.
- SQL Injection riskine karşı `sqlite3` parametreli sorgular (placeholder) kullanılmıştır.
- `st.rerun()` kullanımı, Streamlit'in state yönetimi için doğru bir yaklaşımdır.
- `requirements.txt` dosyası gerekli tüm bağımlılıkları içermektedir.

**Öneri:**
- İlerleyen aşamalarda `update_subscription` fonksiyonu için `app.py` üzerinde bir form arayüzü eklenebilir, şu an sadece silme işlemi için arayüz mevcuttur. Ancak bu durum temel gereksinimleri karşılamaya engel değildir.
