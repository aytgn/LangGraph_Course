# LangGraph ile Otonom Ajan Şirketi: Birebir Eğitim ve Canlı Proje Alanı

Bu repo, dış kurslara gerek kalmadan Antigravity asistanının rehberliğinde sıfırdan ileri seviyeye kadar LangGraph öğrenmek ve canlı bir **Otonom Ajan Şirketi** inşa etmek için hazırlanmıştır.

## Klasör Yapısı

```
LangGraph_Course/
├── .agents/
│   └── skills/                             # Antigravity'ye yüklenen uzmanlık becerileri
│       ├── langgraph-curriculum-mentor/    # Baş eğitmenlik ve koçluk motoru
│       ├── langgraph-fundamentals/         # 1. Aşama: State, Node, Edge mantığı
│       ├── langgraph-advanced-runtime/     # 2. Aşama: Persistence, Time-travel, HITL
│       ├── langgraph-multi-agent-architectures/ # 3. Aşama: Supervisor ve Ekipler
│       └── langsmith-observability/        # 4. Aşama: Maliyet, Log ve Akış takibi
├── 01_temel_egitim/                        # Modül 1 pratik dosyaları
├── 02_derinlesme_runtime/                  # Modül 2 pratik dosyaları
├── 03_ekip_mimarisi/                       # Modül 3 pratik dosyaları
├── 04_gozlemlenebilirlik/                  # Modül 4 pratik dosyaları & Atölye
├── 05_otonom_ajan_sirketi/                 # Büyük final şirketi projesi
├── yonetici_masasi.py                      # 👑 Kurumsal Yönetici Kokpiti (Streamlit)
├── pages/
│   ├── 1_📖_Sistem_Dokumantasyonu.py       # 📖 Teknik Sistem Dokümantasyonu (Harici Sekme)
│   └── 2_📚_LangGraph_Basucu_Kitabi.py     # 📚 Tam Ekran İnteraktif E-Kitap Sayfası (Harici Sekme)
├── LANGGRAPH_E_KITAP.html                  # 📖 Sunucusuz (Zero-Daemon) Tek Dosya Web E-Kitap
├── kitap_okuyucu.py                        # 🛠️ Statik E-Kitap Derleyicisi (--build)
├── LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.md   # 📚 12 Bölümlük Uçtan Uca Başucu Kitabı (Markdown)
├── LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.pdf  # 📥 Başucu Kitabı (Yayın Kalitesinde PDF)
├── model_factory.py                        # Dinamik API Key Rotasyon Motoru
├── .env.example                            # API anahtarları şablonu
├── requirements.txt                        # Gerekli Python kütüphaneleri
└── README.md
```

## Model Mimarisi
- **Eğitim & Prototipleme**: Google Gemini (`langchain-google-genai`).
- **Üretim & Canlıya Alma (Build)**: Google Argon / Google Cloud kurumsal altyapısı.
