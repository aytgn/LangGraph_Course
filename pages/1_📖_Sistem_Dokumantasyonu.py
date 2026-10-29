"""
================================================================================
📖 OTONOM AJAN ŞİRKETİ - KAPSAMLI SİSTEM DÖKÜMANTASYONU & MİMARİ REHBERİ 📖
================================================================================
Bu sayfa, uygulamanın nasıl çalıştığını en ince detayına kadar açıklayan,
kod katmanlarını, LangGraph akış şemalarını, veritabanı yapısını ve hızlı kullanım
kılavuzunu sunan harici (external) referans dökümantasyon merkezidir.
================================================================================
"""

import os
import sys
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# PDF Üretici Modülü
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))
from pdf_olusturucu import generate_enterprise_documentation_pdf

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Sistem Dökümantasyonu & Mimari Rehber",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kurumsal Stil
st.markdown("""
<style>
    .main {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    .doc-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .quick-card {
        background-color: #1E293B;
        border-left: 4px solid #38BDF8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .security-card {
        background-color: #1E293B;
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .badge-gold {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid #F59E0B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    .badge-cyan {
        background-color: rgba(6, 182, 212, 0.15);
        color: #06B6D4;
        border: 1px solid #06B6D4;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Yan Menü Navigasyonu
with st.sidebar:
    st.markdown("### 🏢 DÖKÜMANTASYON MERKEZİ")
    st.caption("Otonom Ajan Şirketi Teknik Whitepaper")
    
    st.markdown("---")
    st.link_button("👑 Yönetici Kokpitini Aç ↗", url="/", type="primary", use_container_width=True, help="Yönetici Kokpiti ve CEO İletişim Masasını ayrı sekmede açar.")
    st.link_button("📚 LangGraph Başucu Kitabı ↗", url="/LangGraph_Basucu_Kitabi", use_container_width=True, help="12 bölümlük karanlık temalı interaktif LangGraph ve Ajan Mimarisi Başucu Kitabını yeni sekmede açar.")
    st.page_link("yonetici_masasi.py", label="👑 Kokpite Dön (Aynı Sekme)", icon="⬅️")
    st.markdown("---")
    
    st.markdown("#### 📑 İçindekiler")
    st.markdown("""
    - **1. Hızlı Yönetici Özeti** (2 Dk)
    - **2. Uçtan Uca Sistem Mimarisi**
    - **3. Çekirdek Kod İncelemesi**
    - **4. Güvenlik & HITL Bütçe Kilidi**
    - **5. SQLite Veritabanı Şeması**
    - **6. Meta-Düzlem & İkinci Beyin (Second Brain)**
    - **7. Otonom Kodlayıcı (SWE-Agent) Mimarisi**
    """)
    
    st.markdown("---")
    st.markdown("##### 📥 Resmi Rapor İndir")
    try:
        pdf_data_sb = generate_enterprise_documentation_pdf()
        st.download_button(
            label="📥 Tüm Dökümanı PDF İndir (.pdf)",
            data=pdf_data_sb,
            file_name="Otonom_Ajan_Sirketi_Mimari_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kodları A4 formatında kurumsal PDF olarak indirir."
        )
    except Exception as e:
        st.caption(f"PDF motoru: {str(e)[:30]}")
        
    st.caption("Versiyon: v3.8 Enterprise SWE\nMotor: LangGraph + SQLite + SWE-Agent")

# Ana Başlık
st.markdown("""
<div class="doc-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; font-size: 26px; color: #F8FAFC;">📖 OTONOM AJAN ŞİRKETİ | SİSTEM DÖKÜMANTASYONU</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
                Mühendislik Standartları • Supervisor Orkestrasyonu • SQLite Kalıcılığı • Otonom SWE-Agent
            </p>
        </div>
        <div>
            <span class="badge-gold">Kurumsal Dökümantasyon</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sekmeler
tab_quick, tab_arch, tab_code, tab_security, tab_db, tab_meta_doc, tab_swe_doc = st.tabs([
    "⚡ 1. Hızlı Kullanım Özeti (Executive Cheatsheet)",
    "🏗️ 2. Uçtan Uca Mimari & LangGraph Akışı",
    "💻 3. Çekirdek Kod Katmanı",
    "🛑 4. Güvenlik, HITL & API Key Rotasyonu",
    "🗄️ 5. SQLite Veritabanı Şeması",
    "🏛️ 6. Meta-Düzlem & İkinci Beyin (Second Brain)",
    "🛠️ 7. Otonom Kodlayıcı (SWE-Agent)"
])

# ==============================================================================
# TAB 1: HIZLI KULLANIM ÖZETİ
# ==============================================================================
with tab_quick:
    st.markdown("### ⚡ 2 Dakikada Anlama Kılavuzu (Executive Quickstart)")
    st.caption("Karmaşık kod yapılarına girmeden sistemin mantığını, işleyişini ve kullanımını kavrayın:")

    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("""
        <div class="quick-card">
            <h4 style="color:#38BDF8; margin-top:0;">1️⃣ Direktif Verin</h4>
            <p style="color:#CBD5E1; font-size:14px;">
                Yönetici Masası'ndaki sohbet çubuğuna şirket hedefi girilir. (Örn: <i>"Fintech için fraud tespit mikroservisi oluşturun"</i>).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q2:
        st.markdown("""
        <div class="quick-card">
            <h4 style="color:#F59E0B; margin-top:0;">2️⃣ Otonom İmalat</h4>
            <p style="color:#CBD5E1; font-size:14px;">
                CEO sırasıyla Araştırma Departmanı'nı ve Mühendislik Departmanı'nı koordine eder. Pazar analizi ve Python kodu üretilir.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q3:
        st.markdown("""
        <div class="quick-card">
            <h4 style="color:#10B981; margin-top:0;">3️⃣ İnsan Onayı (HITL)</h4>
            <p style="color:#CBD5E1; font-size:14px;">
                Sistem 250.000 TL bütçe tahsisi öncesinde donar. Yönetim Kurulu Başkanı (Siz) ekrandaki butona basarak onayı tamamlar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💡 Temel Kavramlar Sözlüğü")
    
    faq_data = [
        {"Kavram": "StateGraph", "Açıklama": "LangGraph'ın temel çizelge motorudur. Düğümleri (Ajanları) ve durum geçişlerini yönetir."},
        {"Kavram": "Supervisor Pattern", "Açıklama": "Tüm kararların merkezi bir CEO tarafından Pydantic şemasıyla verildiği orkestrasyon modeli."},
        {"Kavram": "Human-in-the-Loop (HITL)", "Açıklama": "Yüksek riskli (para, veri silme vb.) işlemlerde yapay zekanın duraklayıp insan kararı beklemesi."},
        {"Kavram": "SqliteSaver", "Açıklama": "Grafın her adımını SQLite veritabanına anlık kaydeden ve sunucu çökse bile kaldığı yeri unutmayan kalıcılık katmanı."},
        {"Kavram": "Key Failover Pool", "Açıklama": ".env'deki 5 anahtar arasında kota veya yoğunluk anında milisaniyeler içinde geçiş yapan dayanıklılık motoru."}
    ]
    st.dataframe(pd.DataFrame(faq_data), use_container_width=True, hide_index=True)

    # İndirme Butonları (PDF & Markdown)
    st.markdown("---")
    st.markdown("##### 📥 Kapsamlı Dokümanı Bilgisayarınıza İndirin:")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Tüm Dökümanı Kurumsal PDF Olarak İndir (.pdf)",
            data=generate_enterprise_documentation_pdf(),
            file_name="Otonom_Ajan_Sirketi_Mimari_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kodları A4 formatında kurumsal PDF olarak indirir."
        )
    with col_dl2:
        st.download_button(
            label="📄 Dökümanı Markdown Olarak İndir (.md)",
            data="""# Otonom Ajan Şirketi - Kapsamlı Yönetici Kılavuzu\nBu dosya projenin teknik mimarisini, kodlarını ve kullanım yönergelerini içerir.""",
            file_name="otonom_sirket_kilavuzu.md",
            mime="text/markdown",
            use_container_width=True
        )

# ==============================================================================
# TAB 2: UÇTAN UCA MİMARİ & LANGGRAPH AKIŞI
# ==============================================================================
with tab_arch:
    st.markdown("### 🏗️ Uçtan Uca Sistem Mimarisi & LangGraph Akışı")
    st.caption("Şirket organizasyonu, döngüsel (cyclic) ve koşullu (conditional) kenarlarla birbirine bağlanmış durum makinesidir.")

    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────────────────────────┐
    │                        YÖNETİM KURULU DİREKTİFİ                         │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │                        👑 CEO / EXECUTIVE BOARD                        │
    │             (Pydantic Yapılandırılmış Çıktı: CEORouteDecision)           │
    └──────┬────────────────────────────┬────────────────────────────┬───────┘
           │ (Araştırma Yoksa)          │ (Kod Eksikse)              │ (Bütçe Gerekiyorsa)
           ▼                            ▼                            ▼
    ┌──────────────┐             ┌──────────────┐             ┌─────────────────────┐
    │ 🔬 Research  │             │ 💻 Engineer  │             │ 🛑 GÜVENLİK KİLİDİ   │
    │  Pazar Raporu│             │  Python Kodu │             │ (interrupt_before)  │
    └──────┬───────┘             └──────┬───────┘             └──────────┬──────────┘
           │                            │                                │
           │                            │                        [İnsan Onayı Verildi]
           │                            │                                ▼
           │                            │                     ┌─────────────────────┐
           │                            │                     │ 🛡️ Audit & Finance  │
           │                            │                     │  250.000 TL Bütçe   │
           │                            │                     └──────────┬──────────┘
           ▼                            ▼                                ▼
    └───────────────────────────────────┴────────────────────────────────┴───────┐
                                        │ (Tüm Departmanlar CEO'ya Rapor Verir)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │                                👑 CEO                                  │
    │               (Tüm Çıktılar Hazırsa: 'FINISH' ➔ END)                  │
    └────────────────────────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("---")
    st.markdown("#### 📦 Şirket Durum Nesnesi (CompanyState)")
    st.markdown("""
    Her düğüm çalıştırıldığında bu merkezi sözlükten (State) beslenir ve çıktısını buraya yazar:
    - `messages`: Konuşma geçmişi ve araç çağrıları (`add_messages` reducer ile listenin sonuna eklenir).
    - `next_step`: CEO'nun belirlediği sıradaki hedef (`Research_Dept`, `Engineering_Dept`, `Audit_Approval_Dept`, `FINISH`).
    - `research_summary`: Araştırma departmanının piyasa analizi özeti.
    - `code_deliverable`: Mühendislik departmanının yazdığı kurumsal Python modülü.
    - `allocated_budget`: Finans departmanının tahsis ettiği tutar (250.000 TL).
    - `is_audit_passed`: Güvenlik ve denetim onayı (True / False).
    """)

# ==============================================================================
# TAB 3: ÇEKİRDEK KOD KATMANI
# ==============================================================================
with tab_code:
    st.markdown("### 💻 Çekirdek Kod Katmanı ve Modül İncelemesi")
    st.caption("Projede çalışan temel Python bileşenleri ve kod blokları:")

    code_tab1, code_tab2, code_tab3 = st.tabs([
        "1. model_factory.py (Key Rotasyonu)",
        "2. sirket_motoru.py (Departman Düğümleri)",
        "3. LangGraph Derlemesi & HITL"
    ])

    with code_tab1:
        st.markdown("**Dinamik 5'li API Key Rotasyon Motoru:**")
        st.code("""
class KeyRotatingGeminiLLM(Runnable):
    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs) -> Any:
        total_keys = len(self.api_keys)
        for attempt in range(total_keys):
            idx = (self.active_index + attempt) % total_keys
            key = self.api_keys[idx]
            model = self._create_model_for_key(key)
            try:
                response = model.invoke(input, config=config, **kwargs)
                self.active_index = idx
                return response
            except Exception as e:
                # Kota veya sunucu hatasında bir sonraki anahtara geç!
                next_idx = (idx + 1) % total_keys
                _print_key_rotate_warning(idx, next_idx, str(e), self.model_name)
                continue
        raise last_exception
        """, language="python")

    with code_tab2:
        st.markdown("**CEO Durum Bilinci ve Doğrudan Yönlendirme:**")
        st.code("""
def ceo_supervisor_node(state: CompanyState):
    has_research = bool(state.get("research_summary"))
    has_code = bool(state.get("code_deliverable"))
    has_audit = bool(state.get("is_audit_passed"))
    
    prompt = (
        "Sen CEO'sun. Şirket Durumu:\\n"
        f"- Pazar Araştırması: {'TAMAMLANDI' if has_research else 'EKSİK'}\\n"
        f"- Mühendislik Kodu : {'TAMAMLANDI' if has_code else 'EKSİK'}\\n"
        f"- Bütçe Denetimi   : {'TAMAMLANDI' if has_audit else 'EKSİK'}\\n"
        "Kurallar: Eksik olan departmanı sırayla seç. Hepsi tamamsa 'FINISH' seç."
    )
    decision = ceo_llm.invoke(messages)
    return {"next_step": decision.next}
        """, language="python")

    with code_tab3:
        st.markdown("**LangGraph Derleme ve SQLite Checkpointer Bağlantısı:**")
        st.code("""
conn = sqlite3.connect("enterprise.db", check_same_thread=False)
memory = SqliteSaver(conn)

app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Audit_Approval_Dept"]  # Finans işlemi öncesi grafı dondur!
)
        """, language="python")

# ==============================================================================
# TAB 4: GÜVENLİK, HITL & API KEY ROTASYONU
# ==============================================================================
with tab_security:
    st.markdown("### 🛑 Güvenlik, Human-in-the-Loop & API Key Failover")
    st.caption("Sistemin kurumsal ortamlarda güvenle çalışmasını sağlayan mimari tedbirler:")

    st.markdown("""
    <div class="security-card">
        <h4 style="color:#EF4444; margin-top:0;">🛡️ Kritik İşlem Kapısı (Human-in-the-Loop Gate)</h4>
        <p style="color:#CBD5E1; font-size:14px;">
            Yapay zeka modellerinin bütçe harcaması veya dış dünyaya kaynak tahsisi yapması kabul edilemez bir risktir. 
            Bu nedenle <code>interrupt_before=['Audit_Approval_Dept']</code> parametresi ile süreç dondurulur.
            Yönetim Kurulu Başkanı web arayüzünden bütçeyi inceleyip <b>'ONAYLA'</b> butonuna basmadığı sürece işlem yapılamaz.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🔑 5'li API Key Havuzunun Çalışma Prensibi")
    st.markdown("""
    1. Sistem `.env` dosyasındaki `GOOGLE_API_KEYS` listesini okur.
    2. Satır içi yorumlar (`#4.KEY`) ve boşluklar temizlenerek havuz belleğe alınır.
    3. Google AI Studio serbest katmanında bir anahtar `429 (Kota Doldu)`, `503 (Sunucu Yoğun)` veya `504 (Zaman Aşımı)` verdiğinde:
       - Kod hata vermez.
       - Konsola ve loglara rotasyon uyarısı basılır.
       - Bir sonraki anahtar (Key #2, Key #3...) anında devreye girer.
    4. İleride `.env` dosyasına 10 yeni anahtar eklense bile Python koduna tek satır dokunulması gerekmez.
    """)

# ==============================================================================
# TAB 5: SQLITE VERİTABANI ŞEMASI
# ==============================================================================
with tab_db:
    st.markdown("### 🗄️ SQLite Veritabanı Şeması & Kalıcılık")
    st.caption("enterprise.db içerisinde LangGraph checkpoints ve writes yapısı:")

    db_path = os.path.join(os.path.dirname(__file__), "..", "05_otonom_ajan_sirketi", "enterprise.db")
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Tablo Yapısı
        cur.execute("PRAGMA table_info(checkpoints);")
        cols = cur.fetchall()
        df_cols = pd.DataFrame(cols, columns=["ID", "Sütun Adı", "Veri Tipi", "NotNull", "Default", "PK"])
        
        st.markdown("**1. `checkpoints` Tablo Şeması:**")
        st.dataframe(df_cols[["Sütun Adı", "Veri Tipi", "PK"]], use_container_width=True, hide_index=True)
        
        # Son 5 Checkpoint Kaydı
        cur.execute("SELECT thread_id, checkpoint_id, parent_checkpoint_id, type FROM checkpoints ORDER BY rowid DESC LIMIT 5;")
        recent_records = cur.fetchall()
        df_recent = pd.DataFrame(recent_records, columns=["Thread ID", "Checkpoint ID", "Parent ID", "Tip"])
        
        st.markdown("**2. Veritabanındaki Son 5 Checkpoint Kaydı (Canlı Veri):**")
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
        
        conn.close()
    else:
        st.info("enterprise.db dosyası henüz oluşturulmadı. Bir proje başlattığınızda otomatik üretilecektir.")

# ==============================================================================
# TAB 6: META-DÜZLEM & İKİNCİ BEYİN MİMARİSİ
# ==============================================================================
with tab_meta_doc:
    st.markdown("### 🏛️ Çift Düzlemli Bilişsel Mimari (Dual-Plane Cognitive Architecture)")
    st.caption("Meta-Düzlem (Kurucular Odası & İkinci Beyin) ile Operasyonel Düzlem (LangGraph Ajan Şirketi) Arasındaki Ayrım")

    st.markdown("""
    Yapay zeka literatüründe ve kurumsal şirketlerde, yalnızca alt düzey işleri yürüten işçi ajanlar ile çalışıldığında
    şirketin vizyonu, felsefesi ve stratejik pivotları kaybolur. Bu nedenle sistemimiz **Çift Düzlemli (Dual-Plane)** olarak yapılandırılmıştır:
    """)

    st.markdown("""
    #### 1. Bilişsel Düzlemler Arasındaki Görev Dağılımı:
    - **🏛️ Düzlem 0: Meta-Düzlem (Think-Tank & Second Brain):**
      - **Rol:** Şirket yapısı, felsefe, vizyon, yeni ürün hipotezleri, büyük pivotlar ve şirket dışı serbest konular.
      - **Ajanlar:** 
        - `🤝 AI Co-Founder`: Vizyoner, ilham verici kurucu ortak.
        - `⚡ The Skeptic (Şeytanın Avukatı)`: Kör noktaları deşen, maliyet tuzaklarını gösteren red-team eleştirmeni.
        - `📜 Chief of Staff (Scribe)`: Tartışmaları yapılandırıp `meta_bellek/` bilgi kasasına kaydeden hafıza muhafızı.
      - **Hafıza:** Dosya tabanlı yaşayan Markdown Bilgi Kasası (`meta_bellek/`).

    - **⚙️ Düzlem 1: Operasyon Düzlemi (LangGraph Execution Engine):**
      - **Rol:** Meta düzlemde filtrelenip onaylanan somut direktifleri icra etmek.
      - **Ajanlar:** CEO Supervisor, Araştırma Departmanı, Mühendislik Departmanı, Denetim/Bütçe Departmanı.
      - **Hafıza:** Durum geçişli SQLite Checkpointer (`enterprise.db`).

    #### 2. Kalıcı İkinci Beyin Kasası (`meta_bellek/`):
    - `01_sirket_vizyonu.md`: Şirketin ana manifestosu ve temel ilkeleri.
    - `02_beyin_firtinasi_notlari/`: Tarihli, etiketli kurucu beyin fırtınaları.
    - `03_stratejik_kararlar/`: Mimari ve Stratejik Karar Kayıtları (ADR).
    - `04_operasyonel_direktifler/`: CEO ve operasyona aktarılan resmi görevler.

    #### 3. Stratejik Direktif Köprüsü (`direktif_koprusu.py`):
    Kurucular Odası'nda saatlerce süren serbest ve felsefi bir tartışma bittiğinde, tek bir tıkla (`🚀 Operasyona Aktar`)
    Chief of Staff tartışmayı operasyonel bir brife dönüştürür ve CEO masasına otomatik olarak enjekte eder.
    """)

# ==============================================================================
# TAB 7: OTONOM KODLAYICI (SWE-AGENT) MİMARİSİ
# ==============================================================================
with tab_swe_doc:
    st.markdown("### 🛠️ Otonom Yazılım Mühendisi (SWE-Agent) Mimarisi")
    st.caption("Devin, Aider ve Claude Engineer standartlarında; dosya okuyan, kod yazan, diff çıkaran ve diske atomik yazan motor")

    st.markdown("""
    Geleneksel chatbot'lar yalnızca havada uçuşan metinler üretirken; **SWE-Agent Motorumuz (`meta_katman/otonom_kodlayici.py`)** 
    proje dizinindeki gerçek Python, CSS, HTML ve Markdown dosyalarını okur, değişiklikleri üretir ve sözdizimi onaylandığında diske yazar.

    #### 1. Güvenlik ve AST Doğrulama Standartları (`meta_katman/kod_araclari.py`):
    - **🛡️ Sandbox Duvarı:** Ajan yalnızca `LangGraph_Course` kök dizininde çalışabilir. Dizin dışına çıkamaz (`../`), `.env` ve `.git` gibi hassas dosyaları değiştiremez.
    - **🧪 AST ve Derleme Denetimi:** Üretilen her kod parçası diske yazılmadan önce `ast.parse` ve `py_compile` ile denetlenir. 0 sözdizimi hatası garanti edilir.
    - **🔄 Kendi Kendini Onarma (Self-Healing Loop):** Bir derleme hatası olursa süreç durmaz; traceback hata detayları ajana geri beslenerek kodu kendi kendine düzeltir (3 iterasyona kadar).
    - **💾 Atomik Yazma & Snapshot:** Her dosya yazımından önce `meta_bellek/.backups/` altına zaman damgalı `.bak` yedeği alınır. İşlem `.tmp` dosyası üzerinden atomik gerçekleştirilir.
    - **↩️ Anında Rollback:** Beğenilmeyen veya geri alınmak istenen herhangi bir değişiklik tek tıkla eski yedeğine döndürülebilir.

    #### 2. SWE-Agent LangGraph Akışı:
    1. **`analyze_node`:** Hedef dosyayı okur (`yonetici_masasi.py`, vb.) ve mevcut içeriği belleğe alır.
    2. **`generate_patch_node`:** Kullanıcı direktifine (`instruction`) göre eksiksiz, çalışan tam yeni kodu üretir.
    3. **`verify_syntax_node`:** Kodun sözdizimini test eder ve satır satır renkli Unified Diff üretir.
    4. **`Human-in-the-Loop Onayı`:** Yönetici Masasında diff incelenir ve *"🚀 Onayla & Diske Yaz"* dendiğinde dosya canlı olarak güncellenir.

    #### 3. Tüm Kod Tabanı Otonom Modu (Codebase-Wide Auto-Refactor):
    Kullanıcının tek tek dosya seçmesine veya kodlama bilmesine gerek yoktur.
    Yönetici sadece *"Arayüzü AI Slop'tan kurtar, Linear tarzı yap"* gibi bir doğal dil emri verdiğinde:
    - **AI Mimar (`discover_relevant_files_for_task`)** tüm kod tabanını otonom tarar.
    - Etkilenecek tüm dosyaları (örn: `yonetici_masasi.py`, dokümantasyon sayfaları) kendi kendine tespit eder.
    - Her dosya için AST doğrulamalı kod üretir ve toplu snapshot alarak tek tıkla canlıya geçirir.
    """)
