# 🏢 Modül 06: Otonom Ajan Şirketi - Yönetici Masası (Executive Cockpit)

Bu modül, LangGraph tabanlı otonom yapay zeka holdingi için geliştirilmiş bağımsız ve modüler kurumsal yönetim kokpitidir. 01'den 05'e kadar olan eğitim modüllerinden izole, tam teşekküllü bir üretim katmanıdır.

---

## 📁 Dizin Mimarisi

* `yonetici_masasi.py`: Streamlit tabanlı Yönetici Masası ve Operasyon Kokpiti.
* `sirket_motoru.py`: LangGraph StateGraph, CEO Orkestratörü, Departman Ajanları ve HITL güvenlik kapısı.
* `enterprise.db`: Projelerin, durumların ve time-travel checkpoint kayıtlarının saklandığı bağımsız SQLite veritabanı.
* `meta_katman/`: Yapay Zeka Kurucu Ortak (Co-Founder), Şeytanın Avukatı (The Skeptic) ve Kurucular Konseyi strateji motoru.
* `meta_bellek/`: Yaşayan Markdown Bilgi Kasası (Second Brain Knowledge Vault).
* `pages/`:
  * `1_📖_Sistem_Dokumantasyonu.py`: Kurumsal mimari ve teknik başvuru kılavuzu.
  * `2_📚_LangGraph_Basucu_Kitabi.py`: Tam ekran e-kitap okuyucu.
* `pdf_olusturucu.py`: Mimari dökümantasyon ve kurumsal whitepaper PDF motoru.
* `kitap_okuyucu.py`: E-kitap ayrıştırma ve statik HTML okuma köprüsü.

---

## 🚀 Başlatma
Kök dizinden tek komutla:
```bash
streamlit run 06_yonetici_sirket/yonetici_masasi.py
```
Veya kök dizindeki `baslat_yonetici_masasi.bat` dosyasını çalıştırarak.
