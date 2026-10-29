# 🏗️ Modül 06: Otonom Yazılım Evi & Uygulama Stüdyosu (AI Software Studio)

Bu modül, 01–05 eğitim modüllerinden tamamen bağımsız çalışan; **ne uygulaması yapılacağının, hangi amaçla ve hangi teknoloji yığınıyla geliştirileceğinin tartışıldığı** ve ardından döngüsel LangGraph yazılım fabrikasıyla **gerçek, çok dosyalı, çalışan uygulamaların** inşa edildiği üretim kokpitidir.

---

## 📁 Dizin Mimarisi

* `yonetici_masasi.py`: 5 sekmeli Kurucu & Yönetici Uygulama Geliştirme Kokpiti (Streamlit).
* `sirket_motoru.py`: Döngüsel LangGraph Yazılım Fabrikası (`Studio_Director` ↔ `Product_Lead` / `System_Architect` / `Lead_Developer` ↔ `QA_Security_Lead` → `Deployment_Gate`).
* `studio_apps.db`: Geliştirilen uygulamaların PRD, mimari, kod dosyaları ve döngü izlerini saklayan bağımsız SQLite veritabanı.
* `output_uygulamalar/`: Onaylanan her uygulamanın fiziksel kaynak kodlarının ve tek tıkla çalıştırılabilir `baslat.bat` dosyasının üretildiği dizin.
* `meta_katman/`: CPO (Ürün Keşfi), CTO (Altyapı & Tech Stack Mimarı) ve Teknik PM şartname köprüsü.
* `meta_bellek/`: Ürün keşif notları, ADR (Mimari Karar Kayıtları) ve Stüdyo Manifestosu.
* `pages/`: Harici sekmede açılan Sistem Dokümantasyonu ve LangGraph Başucu Kitabı.

---

## 🚀 Başlatma

Kök dizindeki `baslat_yonetici_masasi.bat` (veya masaüstü kısayolu) ile ya da terminalden:
```bash
.\.venv\Scripts\streamlit run 06_yonetici_sirket/yonetici_masasi.py
```
