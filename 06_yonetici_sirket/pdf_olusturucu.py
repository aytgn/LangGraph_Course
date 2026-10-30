"""
================================================================================
📄 OTONOM YAZILIM EVİ - KURUMSAL PDF TEKNİK WHITEPAPER ÜRETİCİSİ 📄
================================================================================
Clean Architecture, Döngüsel LangGraph Fabrikası, Deterministik AST/QA,
Kurucu Karar Kapısı (HITL Onay/Revizyon/Red), SQLite CRUD ve Dinamik ToolRegistry
bilgilerini içeren A4 boyutunda kurumsal Türkçe PDF rapor üretir.
================================================================================
"""

import os
from datetime import datetime
from fpdf import FPDF


class ExecutiveDocPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)

        # Windows sistem fontlarını UTF-8 destekli kaydet
        font_dir = "C:/Windows/Fonts"
        arial_reg = os.path.join(font_dir, "arial.ttf")
        arial_bold = os.path.join(font_dir, "arialbd.ttf")
        consola = os.path.join(font_dir, "consola.ttf")

        if os.path.exists(arial_reg):
            self.add_font("ArialCustom", "", arial_reg)
            if os.path.exists(arial_bold):
                self.add_font("ArialCustom", "B", arial_bold)
            else:
                self.add_font("ArialCustom", "B", arial_reg)
        else:
            self.add_font("ArialCustom", "", "helvetica")
            self.add_font("ArialCustom", "B", "helvetica")

        if os.path.exists(consola):
            self.add_font("ConsolasCustom", "", consola)
        else:
            self.add_font("ConsolasCustom", "", "courier")

    def header(self):
        if self.page_no() > 1:
            self.set_font("ArialCustom", "B", 8)
            self.set_text_color(100, 116, 139)  # slate-500
            self.cell(100, 6, "OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU | KURUMSAL TEKNİK WHITEPAPER", border=0, align="L")
            self.set_font("ArialCustom", "", 8)
            self.cell(90, 6, datetime.now().strftime("%d.%m.%Y"), border=0, align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(226, 232, 240)
            self.line(10, 15, 200, 15)
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font("ArialCustom", "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Sayfa {self.page_no()}", align="C")

    def add_section_title(self, title: str):
        self.ln(4)
        self.set_font("ArialCustom", "B", 12.5)
        self.set_text_color(15, 23, 42)  # slate-900
        self.set_fill_color(241, 245, 249)  # slate-100
        self.cell(0, 9, f"  {title}", border=0, align="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(2, 132, 199)  # sky-600
        self.line(10, self.get_y(), 10, self.get_y() - 9)
        self.ln(3)

    def add_subsection_title(self, title: str):
        self.ln(2)
        self.set_font("ArialCustom", "B", 10.5)
        self.set_text_color(3, 105, 161)  # sky-700
        self.cell(0, 7, title, border=0, align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def add_paragraph(self, text: str):
        self.set_font("ArialCustom", "", 9.5)
        self.set_text_color(51, 65, 85)  # slate-700
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def add_code_block(self, code: str):
        self.set_font("ConsolasCustom", "", 8)
        self.set_text_color(30, 41, 59)
        self.set_fill_color(248, 250, 252)  # slate-50
        self.set_draw_color(203, 213, 225)  # slate-300
        lines = code.strip().split("\n")
        box_text = "\n".join(lines)
        self.multi_cell(0, 4.5, box_text, border=1, fill=True)
        self.ln(2)


def generate_enterprise_documentation_pdf() -> bytes:
    """Tüm sistem mimarisini içeren güncel kurumsal PDF üretir ve bytes olarak döner."""
    pdf = ExecutiveDocPDF()
    pdf.add_page()

    # KAPAK & BAŞLIK ALANI
    pdf.set_fill_color(15, 23, 42)  # Koyu lacivert
    pdf.rect(10, 20, 190, 42, "F")

    pdf.set_y(25)
    pdf.set_font("ArialCustom", "B", 17)
    pdf.set_text_color(248, 250, 252)
    pdf.cell(0, 10, "OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("ArialCustom", "", 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 7, "Clean Architecture • Döngüsel LangGraph Fabrikası • Deterministik AST/QA • SQLite CRUD", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("ArialCustom", "B", 8.5)
    pdf.set_text_color(245, 158, 11)  # Gold
    pdf.cell(0, 6, "LangGraph v0.2+ * Gemini 5-Key Failover * ToolRegistry * HITL Onay/Revizyon/Red * studio_apps.db", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(70)

    # 1. BÖLÜM: YÖNETİCİ HIZLI BAŞLANGIÇ
    pdf.add_section_title("1. YÖNETİCİ HIZLI BAŞLANGIÇ ÖZETİ (SOFTWARE STUDIO CHEATSHEET)")
    pdf.add_paragraph(
        "Bu sistem; soyut danışmanlık raporları yerine doğrudan çalıştırılabilir tam teşekküllü yazılım ürünleri "
        "(Streamlit Web App, FastAPI REST Service, Python CLI & Automation) imal eden otonom bir yapay zeka yazılım stüdyosudur. "
        "Büyük teknoloji şirketlerinin Clean Architecture, SOLID ve Repository Pattern standartlarına göre 6 bağımsız katmanda yapılandırılmıştır."
    )
    pdf.add_subsection_title("Döngüsel İmalatın 4 Temel Aşaması:")
    pdf.add_paragraph(
        "1. Ürün & Mimari Tartışması (Tab 0): CPO (Ürün Lideri) ve CTO (Baş Sistem Mimarı) ile uygulamanın amacı, "
        "kullanıcı akışı, arayüz tipi ve veritabanı tercihi tartışılır; tek tıkla mühendislik şartnamesine dönüştürülür.\n"
        "2. Döngüsel Yazılım Fabrikası (Tab 1): PRD -> Sistem Mimarisi -> Çok Dosyalı Kodlama <-> Deterministik AST/QA "
        "öz-iyileştirme döngüsü otonom olarak çalışır.\n"
        "3. Kurucu Karar Kapısı (HITL Gate): Üretilen kodlar önizlenir; Onayla & Diske Kur, Departmana Revizyon Gönder veya "
        "Kodu Reddet (Sıfırdan Yazdır / İptal Et) kararı verilir.\n"
        "4. Çalıştırma & Portföy CRUD (Tab 2 & 3): Port çakışması önlenmiş baslat.bat (Streamlit port 8505, FastAPI port 8005) "
        "ile tek tıkla başlatılır; studio_apps.db üzerinde tam SQLite CRUD yönetimi sağlanır."
    )

    # 2. BÖLÜM: KURUMSAL CLEAN ARCHITECTURE
    pdf.add_section_title("2. KURUMSAL CLEAN ARCHITECTURE VE 6 KATMANLI YAPI")
    pdf.add_paragraph(
        "Proje kodları monolitik tek bir dosyada değil; sorumlulukları kesin çizgilerle ayrılmış 6 kurumsal katmanda yaşar:\n"
        "- config/ (Settings & Defaults): Kök .env yükleyici, dizin hazırlığı, öz-iyileştirme sınırları (MAX_QA_SELF_HEAL_RETRIES=2).\n"
        "- data/ (Persistence & Models): studio_projects ve checkpoints SQLite tabloları, AppRepository ve VaultRepository CRUD katmanı.\n"
        "- tools/ (Dynamic Tool Registry): StudioTool soyut sınıfı, ToolRegistry (9 kayıtlı araç: AST denetimi, paketleme, kasa).\n"
        "- domain/ (Core Logic & Nodes): CompanyState, Pydantic çıktı şemaları, StudioWorkflowBuilder ve 6 uzman departman düğümü.\n"
        "- services/ (Orchestration): StudioService (fabrika sohbeti, derleme, onay, revizyon, red) ve DiscoveryService (konsey köprüsü).\n"
        "- ui/ (Presentation Layer): Streamlit modüler görünümleri (views/tab_*.py), bileşenler (components/), stiller ve session state."
    )
    pdf.add_code_block("""06_yonetici_sirket/
|-- config/     -> settings.py (Ortam degiskenleri, limitler ve dizinler)
|-- data/       -> database.py, models.py, repositories/ (app_repository, vault_repository)
|-- tools/      -> base.py, registry.py, code_verification.py, disk_operations.py, vault_operations.py
|-- domain/     -> state.py, schemas.py, workflow.py, utils.py, nodes/ (6 Departman Dugumu)
|-- services/   -> studio_service.py, discovery_service.py
`-- ui/         -> styles.py, state.py, components/ (sidebar, matrix, explorer, runner), views/ (tab 0..4)""")

    # 3. BÖLÜM: DÖNGÜSEL LANGGRAPH FABRİKASI
    pdf.add_section_title("3. DÖNGÜSEL LANGGRAPH YAZILIM FABRİKASI VE ÇALIŞMA ŞEMASI")
    pdf.add_paragraph(
        "Geleneksel düz akışların aksine, sistem merkezi 'Studio_Director' etrafında dönen döngüsel (cyclic) bir durum makinesidir. "
        "Ajanlar birbirini doğrudan çağırmaz; her düğüm işini bitirince durumu günceller ve denetim direktöre döner."
    )
    pdf.add_code_block("""[Kurucu Direktifi] -> START -> [Studio_Director (Merkezi Orkestrator)]
  |-- (PRD Eksikse)          -> [Product_Lead (CPO)]        -> [Studio_Director]
  |-- (Mimari Eksikse)       -> [System_Architect (CTO)]    -> [Studio_Director]
  |-- (Kodlama / Revizyon)   -> [Lead_Developer]            -> [Studio_Director]
  |-- (AST & QA Denetimi)    -> [QA_Security_Lead]          -> (Hata Varsa Lead_Developer'a Doner!)
  |-- (QA Gecti & Onay Vakti)-> [Deployment_Gate (HITL)]    -> (Kurucu Onay / Revizyon / Red Bekler!)
  `-- (Kurucu Onayladiysa)   -> Diske Paketle + baslat.bat   -> FINISH""")

    pdf.add_subsection_title("CompanyState Durum Şeması:")
    pdf.add_paragraph(
        "- app_name, app_slug, app_type: Uygulama adı, slug ve mimari türü (Streamlit / FastAPI / CLI).\n"
        "- prd_spec, core_features: MVP ürün şartnamesi ve hedeflenen özellik maddeleri.\n"
        "- architecture_spec, tech_stack, entrypoint_file: Sistem mimarisi, kütüphane listesi ve ana giriş dosyası.\n"
        "- code_files & total_loc: {dosya_adi: kod} sözlüğü ve toplam satır sayısı.\n"
        "- qa_passed, qa_issues, revision_count: AST ve çapraz import test sonuçları, döngü öz-iyileştirme sayacı.\n"
        "- is_rejected, rejection_reason: Kurucu kod reddi durum bayrakları ve gerekçesi.\n"
        "- is_deployed, app_folder, run_command_hint: Fiziksel kurulum dizini ve çalıştırma komutu.\n"
        "- messages & transition_log: Konuşma geçmişi ve zaman damgalı departman geçiş telemetrisi."
    )

    # 4. BÖLÜM: GÜVENLİK VE HITL KARAR KAPISI
    pdf.add_section_title("4. KURUCU KARAR KAPISI (HITL GATE) VE GÜVENLİK KONTROLLERİ")
    pdf.add_paragraph(
        "Sistemde kontrol tamamen insandadır. LangGraph'ın 'interrupt_before=[\"Deployment_Gate\"]' mekanizmasıyla kod diske "
        "yazılmadan önce graf duraklatılır ve Kurucuya 3 net seçenek sunulur:\n"
        "1. [ONAYLA] Kodu Onayla ve Diske İnşa Et: Fiziksel output_uygulamalar/ dizinine kaynak kodlar, requirements.txt, "
        "MIMARI_VE_PRD.md ve baslat.bat dosyalarını inşa eder.\n"
        "2. [REVİZYON] Departmana Revizyon Gönder: İstenen düzeltme talimatıyla fabrikayı hedef departmana (Mühendis, CTO veya CPO) geri yönlendirir.\n"
        "3. [REDDET] Kodu Reddet: 'Sıfırdan Yeniden Yazdır' (kodu silip baştan başlatır) veya 'İnşayı İptal Et' (fiziksel kurulumu iptal edip "
        "SQLite'a 'Kod Reddedildi' statüsünü işler)."
    )
    pdf.add_subsection_title("Sonsuz Döngü ve Çökme Korumaları:")
    pdf.add_paragraph(
        "- MAX_QA_SELF_HEAL_RETRIES = 2: QA hatalarında mühendis en fazla 2 kez otomatik düzeltme döngüsüne girebilir; aşılırsa "
        "sistem sonsuz döngüye girmeden Kurucu Karar Kapısına eskalasyon yapar.\n"
        "- RobustConsole & UTF-8 Koruması: Windows ANSI (cp1252) charmap kodlama uyuşmazlıkları RobustConsole ile yakalanarak "
        "konsola basılan Türkçe karakter ve emojilerin Streamlit'i çökertmesi %100 engellenir.\n"
        "- 5'li API Key Failover Havuzu: .env içerisindeki anahtarlar arasında kota (429) veya yoğunluk (503) anında kesintisiz rotasyon yapılır."
    )

    # 5. BÖLÜM: SQLITE CRUD VE PORTFÖY
    pdf.add_section_title("5. SQLITE VERİTABANI ŞEMASI VE TAM CRUD PORTFÖY YÖNETİMİ")
    pdf.add_paragraph(
        "Tüm projeler 'studio_apps.db' SQLite veritabanında thread izolasyonunda tutulur. Sayfa yenilendiğinde projeler kaybolmaz:\n"
        "- studio_projects Tablosu: thread_id (PK), display_name, custom_notes, tags, created_at, updated_at.\n"
        "- checkpoints & writes Tabloları: LangGraph SqliteSaver durum kayıtları ve düğüm çıktıları.\n"
        "- CREATE: Yeni proje oluşturma anında SQLite'a yazılır; seçimler sıfırlanmaz.\n"
        "- READ: Portföy sekmesinde anlık arama (search_query) ve duruma göre filtreleme (Onay Bekliyor, Reddedildi, Kurulu vb.).\n"
        "- UPDATE: Proje adı, etiket ve yönetici notlarının SQLite UPDATE ile kaydedilmesi.\n"
        "- DELETE: İlgili projenin checkpoints, writes ve disk çıktılarının kalıcı olarak temizlenmesi.\n"
        "- Time-Travel Audit: get_state_history ile projenin her bir geçmiş döngü anına adım adım denetim."
    )

    # 6. BÖLÜM: İKİNCİ BEYİN VE KEŞİF
    pdf.add_section_title("6. İKİNCİ BEYİN (SECOND BRAIN) VE ÜRÜN-MİMARİ KONSEYİ")
    pdf.add_paragraph(
        "Kurumsal hafıza 'meta_bellek/' dizininde kalıcı Markdown ve ADR formatında saklanır:\n"
        "- 01_sirket_vizyonu.md: Şirketin kurucu manifestosu ve temel mühendislik ilkeleri.\n"
        "- 02_beyin_firtinasi_notlari/: Ürün fikirleri ve pazar keşif notları.\n"
        "- 03_stratejik_kararlar/: Mimari Karar Kayıtları (Architecture Decision Records - ADR).\n"
        "- 04_operasyonel_direktifler/: Üretilen doğrulanmış mühendislik şartnameleri.\n"
        "- VaultRepository CRUD: Belgeleri tarayıcı üzerinden okuma, düzenleme ve silme imkânı.\n"
        "- Konsey Köprüsü: CPO + CTO tartışmasını tek tıkla operasyonel şartnameye dönüştürerek doğrudan Yazılım Fabrikası'na aktarır."
    )

    return bytes(pdf.output())


if __name__ == "__main__":
    pdf_bytes = generate_enterprise_documentation_pdf()
    with open("test_studio_whitepaper.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF OK! Boyut:", len(pdf_bytes), "bytes")
