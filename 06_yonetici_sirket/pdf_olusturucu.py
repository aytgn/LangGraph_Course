"""
================================================================================
📄 OTONOM AJAN ŞİRKETİ - KURUMSAL PDF RAPOR ÜRETİCİSİ (EXECUTIVE PDF ENGINE) 📄
================================================================================
Tüm sistem mimarisini, LangGraph akışlarını, SQLite şemasını, güvenlik katmanlarını
ve kod örneklerini profesyonel, Türkçe karakter destekli bir PDF dosyasına dönüştürür.
================================================================================
"""

import os
from fpdf import FPDF
from datetime import datetime

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
            self.set_text_color(100, 116, 139) # slate-500
            self.cell(100, 6, "OTONOM AJAN ŞİRKETİ | KURUMSAL TEKNİK WHITEPAPER", border=0, align="L")
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
        self.set_font("ArialCustom", "B", 13)
        self.set_text_color(15, 23, 42) # slate-900
        self.set_fill_color(241, 245, 249) # slate-100
        self.cell(0, 9, f"  {title}", border=0, align="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(2, 132, 199) # sky-600
        self.line(10, self.get_y(), 10, self.get_y() - 9)
        self.ln(3)

    def add_subsection_title(self, title: str):
        self.ln(2)
        self.set_font("ArialCustom", "B", 10.5)
        self.set_text_color(3, 105, 161) # sky-700
        self.cell(0, 7, title, border=0, align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def add_paragraph(self, text: str):
        self.set_font("ArialCustom", "", 9.5)
        self.set_text_color(51, 65, 85) # slate-700
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def add_code_block(self, code: str):
        self.set_font("ConsolasCustom", "", 8)
        self.set_text_color(30, 41, 59)
        self.set_fill_color(248, 250, 252) # slate-50
        self.set_draw_color(203, 213, 225) # slate-300
        
        # Kod bloğu kutusu
        lines = code.strip().split("\n")
        box_text = "\n".join(lines)
        self.multi_cell(0, 4.5, box_text, border=1, fill=True)
        self.ln(2)


def generate_enterprise_documentation_pdf() -> bytes:
    """Tüm sistem dökümantasyonunu içeren profesyonel bir PDF üretir ve bytes olarak döner."""
    pdf = ExecutiveDocPDF()
    pdf.add_page()

    # KAPAK & BAŞLIK ALANI
    pdf.set_fill_color(15, 23, 42) # Koyu lacivert kurumsal başlık kutusu
    pdf.rect(10, 20, 190, 40, "F")
    
    pdf.set_y(25)
    pdf.set_font("ArialCustom", "B", 18)
    pdf.set_text_color(248, 250, 252)
    pdf.cell(0, 10, "OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("ArialCustom", "", 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 7, "Döngüsel LangGraph Yazılım Fabrikası, AST/QA Denetimi ve Mimari Whitepaper", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("ArialCustom", "B", 8.5)
    pdf.set_text_color(245, 158, 11) # Gold
    pdf.cell(0, 6, "LangGraph Cyclical Studio * Gemini 5-Key Failover * SQLite App Registry * HITL", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(68)
    
    # 1. BÖLÜM: YÖNETİCİ HIZLI BAŞLANGIÇ ÖZETİ
    pdf.add_section_title("1. YÖNETİCİ HIZLI BAŞLANGIÇ ÖZETİ (SOFTWARE STUDIO CHEATSHEET)")
    pdf.add_paragraph(
        "Bu sistem; teorik danışmanlık raporları yerine doğrudan çalışan yazılım uygulamaları (Streamlit Web, FastAPI REST API, "
        "Python CLI) inşa eden tam otonom bir yapay zeka yazılım stüdyosudur. Kurucu Başkan, CPO ve CTO ajanlarla önce ne "
        "uygulaması yapılacağını ve teknoloji yığınını tartışır; ardından döngüsel fabrika gerçek çok dosyalı kodu üretir."
    )
    pdf.add_subsection_title("3 Adımda Uygulama İnşası:")
    pdf.add_paragraph(
        "1. Ürün & Tech Stack Tartışması: Tartışma Odasında CPO ve CTO ile uygulama amacını ve teknolojileri netleştirin.\n"
        "2. Döngüsel İmalat & AST/QA: PRD -> Sistem Mimarisi -> Çok Dosyalı Kodlama <-> Otomatik AST/QA düzeltme döngüsü çalışır.\n"
        "3. Kurucu Onayı veya Revizyon (HITL): Kodu inceleyip onaylayarak baslat.bat ile diske inşa edin veya revizyon döngüsü başlatın."
    )

    # 2. BÖLÜM: UÇTAN UCA MİMARİ VE LANGGRAPH AKIŞI
    pdf.add_section_title("2. DÖNGÜSEL YAZILIM FABRİKASI VE LANGGRAPH MİMARİSİ")
    pdf.add_paragraph(
        "Stüdyo mimarisi doğrusal bir hat değil, merkezi Studio_Director etrafında dönen canlı bir döngüdür. "
        "QA/AST hatası yakalandığında kod otomatik olarak Lead_Developer birimine geri döner; Kurucu geri bildirim verdiğinde "
        "System_Architect veya Lead_Developer düğümüne yeniden yönlendirilir."
    )
    pdf.add_code_block("""[Kurucu Talebi] -> START -> [Studio_Director (Dongu Merkezi)]
  |-- (PRD Eksikse)       -> [Product_Lead (CPO)]     -> [Studio_Director]
  |-- (Mimari Eksikse)    -> [System_Architect (CTO)] -> [Studio_Director]
  |-- (Kodlama / Duzeltme)-> [Lead_Developer]         -> [Studio_Director]
  |-- (AST & QA Kontrolu) -> [QA_Security_Lead]       -> (Hata Varsa Lead_Developer'a Doner!)
  `-- (QA Gectiyse)       -> [HITL Kurucu Kapisi]     -> [Deployment_Gate (baslat.bat)] -> FINISH""")

    pdf.add_subsection_title("CompanyState Yazılım Durum Şeması:")
    pdf.add_paragraph(
        "- app_name, app_slug, app_type: Uygulamanın kimliği ve arayüz tipi (Streamlit / FastAPI / CLI).\n"
        "- prd_spec & core_features: Ürün şartnamesi ve MVP fonksiyonel özellik listesi.\n"
        "- tech_stack & architecture_spec: Seçilen kütüphaneler, veritabanı katmanı ve modül sözleşmesi.\n"
        "- code_files & total_loc: Üretilen çoklu Python dosyaları haritası ve gerçek kod satır sayısı.\n"
        "- qa_passed, qa_issues & revision_count: Deterministik Python AST ve AI kalite denetim döngüsü verileri.\n"
        "- transition_log & cycle_count: Departmanlar arası tüm ileri/geri geçişlerin zaman damgalı izi."
    )

    # 3. BÖLÜM: ÇEKİRDEK KOD MİMARİSİ
    pdf.add_section_title("3. ÇEKİRDEK KOD MİMARİSİ VE MODÜLLER")
    pdf.add_paragraph(
        "Proje 3 temel katmandan oluşur: Dayanıklı LLM fabrikası (model_factory.py), kurumsal graf motoru (sirket_motoru.py) "
        "ve yönetici kontrol kokpiti (yonetici_masasi.py)."
    )
    pdf.add_subsection_title("A) KeyRotatingGeminiLLM (.env Tabanlı 5'li Key Havuzu):")
    pdf.add_paragraph(
        "Google AI Studio'nun serbest katman kotalarına (429) ve sunucu yoğunluklarına (503/504) karşı, "
        ".env içerisindeki 5 API anahtarı arasında milisaniyeler içinde rotasyon yapar. "
        "İleride .env dosyasına yeni anahtarlar eklense dahi Python koduna tek satır dokunulması gerekmez."
    )
    pdf.add_code_block("""class KeyRotatingGeminiLLM(Runnable):
    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs) -> Any:
        total_keys = len(self.api_keys)
        for attempt in range(total_keys):
            idx = (self.active_index + attempt) % total_keys
            try:
                return self._create_model_for_key(self.api_keys[idx]).invoke(input, ...)
            except Exception as e:
                # Kota veya sunucu hatasında bir sonraki anahtara geç!
                next_idx = (idx + 1) % total_keys
                continue
        raise last_exception""")

    # 4. BÖLÜM: GÜVENLİK VE HUMAN-IN-THE-LOOP
    pdf.add_section_title("4. GÜVENLİK VE HUMAN-IN-THE-LOOP (HITL) KAPISI")
    pdf.add_paragraph(
        "Otonom yapay zeka sistemlerinde en büyük operasyonel risk, ajanların denetimsiz bütçe harcaması veya dış dünyaya kaynak tahsisi yapmasıdır. "
        "LangGraph'ın 'interrupt_before' özelliği ile 250.000 TL bütçe tahsisi öncesinde graf dondurulur."
    )
    pdf.add_code_block("""# Audit_Approval_Dept (Bütçe Tahsisi) öncesinde İNSAN ONAYI için duraklatılır!
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Audit_Approval_Dept"]
)""")
    pdf.add_paragraph(
        "Yönetici arayüzdeki '250.000 TL Bütçeyi Onayla' butonuna bastığında 'app.invoke(None, config=config)' çağrılarak "
        "oturum SQLite veritabanındaki dondurulmuş durumdan uyandırılır ve başarıyla sonlandırılır."
    )

    # 5. BÖLÜM: SQLITE VERİTABANI VE KALICILIK
    pdf.add_section_title("5. SQLITE VERİTABANI ŞEMASI VE KALICILIK MODELİ")
    pdf.add_paragraph(
        "Tüm şirket operasyonları yerel 'enterprise.db' veritabanına SqliteSaver aracılığıyla işlenir. "
        "Sunucu çökse veya elektrik kesilse dahi sistem hangi adımda kaldığını unutmaz."
    )
    pdf.add_paragraph(
        "- checkpoints Tablosu: thread_id, checkpoint_id, parent_checkpoint_id, checkpoint (durum verisi), metadata.\n"
        "- writes Tablosu: Düğümlerin birbirine aktardığı mesajlar ve durum güncellemeleri.\n"
        "- Thread İzolasyonu: Her proje (Örn: 'holding-proje-alpha-2026') bağımsız bir oturumda saklanır; diğer projeleri etkilemez.\n"
        "- Time-Travel: 'app.get_state_history(config)' metodu ile geçmiş projelerin her bir anına geri dönülebilir."
    )

    # 6. BÖLÜM: META-DÜZLEM VE İKİNCİ BEYİN
    pdf.add_section_title("6. META-DÜZLEM VE İKİNCİ BEYİN (SECOND BRAIN) MİMARİSİ")
    pdf.add_paragraph(
        "Şirketin kurumsal hafızası 'meta_bellek/' dizini altında Markdown dosyaları ve ADR (Mimari Karar Kayıtları) formatında saklanır. "
        "Yönetici ile CEO arasındaki stratejik konuşmalar, alınan kararlar ve operasyonel direktifler kalıcı bilgi tabanına dönüştürülür. "
        "Böylece şirket zaman geçtikçe unutmayan, kurumsal tecrübe biriktiren yaşayan bir holdinge evrilir."
    )

    # PDF Bytes Çıktısı
    return bytes(pdf.output())


if __name__ == "__main__":
    pdf_bytes = generate_enterprise_documentation_pdf()
    with open("test_doku.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF OK! Boyut:", len(pdf_bytes))
