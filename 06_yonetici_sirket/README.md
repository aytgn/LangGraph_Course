# 🏗️ Modül 06: Otonom Yazılım Evi & Uygulama Stüdyosu (AI Software Studio)

Bu modül; büyük yazılım firmalarının (Big Tech / Enterprise Architecture) kabul görmüş yazılım standartlarına (**Clean Architecture**, **SOLID**, **Repository Pattern ile CRUD**, **Dynamic Tool Registry**, **Modular Presentation/UI Layer**) tam uyumlu, ölçeklenebilir bir Yapay Zeka Yazılım Evi ve Uygulama Stüdyosudur.

---

## 🏛️ Kurumsal Katmanlı Mimari (Clean Architecture)

```
06_yonetici_sirket/
├── config/                           # Merkezi Konfigürasyon Katmanı
│   ├── settings.py                   # Filesystem yolları, SQLite ve timeout ayarları
│   └── __init__.py
├── data/                             # Veri Erişim Katmanı (Repository Pattern / CRUD)
│   ├── database.py                   # Thread-safe SQLite bağlantı yöneticisi (WAL mode)
│   ├── models.py                     # AppProject, CheckpointRecord, DatabaseStats modelleri
│   ├── repositories/
│   │   ├── app_repository.py         # studio_apps.db üzerinde tam CRUD işlemleri
│   │   └── vault_repository.py       # meta_bellek (ADR, Markdown) dosya CRUD işlemleri
│   └── __init__.py
├── domain/                           # İş Alanı ve LangGraph Çekirdek Motoru
│   ├── state.py                      # CompanyState durum sözleşmesi ve reducers
│   ├── schemas.py                    # PRDSpec, ArchitectureSpec, CodeBundle şemaları
│   ├── workflow.py                   # StateGraph kurucu ve SqliteSaver derleyicisi
│   ├── utils.py                      # Telemetri ve loglama yardımcıları
│   └── nodes/                        # Tek Sorumluluk İlkeli Ajan Düğümleri
│       ├── director.py               # Studio_Director döngü ve rota yöneticisi
│       ├── product_lead.py           # CPO PRD üretici
│       ├── system_architect.py       # CTO Mimari ve teknoloji stack tasarımcısı
│       ├── lead_developer.py         # Kıdemli mühendis çok dosyalı kodlayıcı
│       ├── qa_security.py            # QA & AST denetim düğümü
│       └── deployment.py             # HITL paketleme ve disk kurulum düğümü
├── tools/                            # Dinamik Tool Registry ve Modüler Araç Setleri
│   ├── base.py                       # StudioTool kontratı ve soyut sınıfı
│   ├── registry.py                   # ToolRegistry (Kayıt, departman bazlı keşif ve liste)
│   ├── code_verification.py          # AST sözdizimi ve çapraz modül import doğrulayıcı araçlar
│   ├── disk_operations.py            # Fiziksel klasör, requirements, baslat.bat ve ZIP üretici araçlar
│   └── vault_operations.py           # İkinci beyin ADR ve beyin fırtınası araçları
├── services/                         # Uygulama Orkestrasyon Servisleri
│   ├── studio_service.py             # Graf çalıştırma, streaming, onay ve revizyon yönetimi
│   └── discovery_service.py          # CPO & CTO beyin fırtınası ve ADR köprüsü
├── ui/                               # Streamlit Sunum Katmanı (Modüler Görünümler)
│   ├── styles.py                     # Merkezi CSS, kurumsal koyu tema ve rozetler
│   ├── state.py                      # Session state başlatma ve senkronizasyon
│   ├── components/
│   │   ├── sidebar.py                # Proje seçici, sağlık metrikleri ve hızlı aksiyonlar
│   │   ├── cyclical_matrix.py        # Canlı döngü izi ve grafik görselleştirici widget
│   │   └── code_explorer.py          # Çok dosyalı kod sekmeleri ve indirme araçları
│   └── views/
│       ├── tab_ideation.py           # Sekme 0: CPO & CTO ile Ürün ve Tech Stack Tartışması
│       ├── tab_factory.py            # Sekme 1: Döngüsel Fabrika, Canlı Loglar ve HITL Kapısı
│       ├── tab_workspace.py          # Sekme 2: Kod Gezgini, Tek Tıkla baslat.bat ve ZIP İndirme
│       ├── tab_portfolio.py          # Sekme 3: Portföy CRUD Tablosu, Filtreler, Silme ve Time-Travel
│       └── tab_architecture.py       # Sekme 4: Sistem Mimarisi, Kayıtlı Araç Listesi ve PDF
├── yonetici_masasi.py                 # Temiz UI Orkestratörü (~88 satır)
├── sirket_motoru.py                   # Geriye dönük uyumlu cephe (facade)
├── pdf_olusturucu.py                  # Kurumsal PDF dokümantasyon üreticisi
├── output_uygulamalar/                # Üretilen fiziksel yazılım paketleri
└── meta_bellek/                       # İkinci beyin, vizyon ve mimari kararlar (ADR)
```

---

## 🚀 Başlatma

Kök dizindeki `baslat_yonetici_masasi.bat` (veya masaüstü kısayolu) ile ya da terminalden:
```bash
.\.venv\Scripts\streamlit run 06_yonetici_sirket/yonetici_masasi.py
```
