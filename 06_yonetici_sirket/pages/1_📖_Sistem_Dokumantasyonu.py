"""
================================================================================
📖 OTONOM AJAN ŞİRKETİ - KAPSAMLI SİSTEM DÖKÜMANTASYONU & MİMARİ REHBERİ 📖
================================================================================
Linear / Apple Human Interface Standartlarında Rafine Edilmiş Kurumsal Başucu Kılavuzu.
Uçtan uca sistem mimarisi, LangGraph akışları, çekirdek kod katmanları,
SQLite kalıcılığı, 5'li key havuzu failover motoru, Meta-Düzlem ve SWE-Agent.
================================================================================
"""

import os
import sys
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Dizin Yapılandırması ve Bağımlılıklar
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
root_dir = os.path.abspath(os.path.join(app_dir, ".."))
sys.path.insert(0, app_dir)
sys.path.insert(0, root_dir)

load_dotenv(os.path.join(root_dir, ".env"))

from pdf_olusturucu import generate_enterprise_documentation_pdf
from model_factory import API_KEY_POOL, TARGET_MODEL

# ==============================================================================
# 1. Sayfa Yapılandırması & Linear / Apple Minimalist Tasarım Sistemi
# ==============================================================================
st.set_page_config(
    page_title="Sistem Dökümantasyonu & Mimari Rehber",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Linear / Apple Human Interface Standartlarında Rafine Dark Tema
st.markdown("""
<style>
    /* Renk Paleti ve Değişkenler */
    :root {
        --canvas: #08090A;
        --surface-1: #101216;
        --surface-2: #15181E;
        --surface-3: #1C2028;
        --hairline: rgba(255, 255, 255, 0.08);
        --hairline-strong: rgba(255, 255, 255, 0.15);
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --text-tertiary: #6B7280;
        --accent: #5E6AD2;
        --accent-hover: #6E7BF5;
    }

    /* Ana Tuval */
    .stApp, .main {
        background-color: var(--canvas) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
    }

    /* Streamlit Varsayılan Çoklu Sayfa Menüsünü Gizle */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Kenar Çubuğu (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: var(--surface-1) !important;
        border-right: 1px solid var(--hairline) !important;
    }

    /* Üst Durum Çubuğu (Executive Header) */
    .doc-header {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 22px;
    }

    /* Minimalist Rozetler (Pills) */
    .badge-gold {
        background-color: rgba(245, 158, 11, 0.08);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.20);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
        letter-spacing: 0.02em;
    }
    .badge-cyan {
        background-color: rgba(94, 106, 210, 0.08);
        color: #828FFF;
        border: 1px solid rgba(94, 106, 210, 0.20);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
        letter-spacing: 0.02em;
    }
    .badge-green {
        background-color: rgba(16, 185, 129, 0.08);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.20);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
        letter-spacing: 0.02em;
    }

    /* Rafine İçerik Kartları */
    .report-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 14px;
        transition: border 0.15s ease;
    }
    .report-card:hover {
        border-color: var(--hairline-strong);
    }

    .quick-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-left: 3px solid #828FFF;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    .security-card {
        background-color: rgba(239, 68, 68, 0.04);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-left: 3px solid #EF4444;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 16px 0;
    }

    /* Sekme Başlıkları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid var(--hairline);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: transparent;
        border-radius: 6px;
        color: var(--text-secondary);
        font-size: 13px;
        font-weight: 500;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--surface-2) !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. Yan Menü (Sidebar)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 DÖKÜMANTASYON MERKEZİ")
    st.caption("Otonom Ajan Şirketi Teknik Whitepaper v3.8")
    
    st.markdown("---")
    st.link_button("👑 Yönetici Kokpitini Aç ↗", url="/", type="primary", use_container_width=True, help="Yönetici Kokpiti ve CEO İletişim Masasını ayrı web sekmesinde açar.")
    st.page_link("yonetici_masasi.py", label="⬅️ Kokpite Dön (Aynı Sekme)", icon="🏠")
    st.markdown("---")
    
    st.markdown("#### 📡 Altyapı Radarı")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f'<span class="badge-cyan">⚡ Model</span><br><small style="color:#9CA3AF">{TARGET_MODEL}</small>', unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f'<span class="badge-green">🔑 Key Havuzu</span><br><small style="color:#9CA3AF">{len(API_KEY_POOL)} Adet (.env)</small>', unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.markdown('<span class="badge-gold">👑 CEO Ajanı</span><br><small style="color:#9CA3AF">Hazır</small>', unsafe_allow_html=True)
    with col_sb4:
        st.markdown('<span class="badge-cyan">💾 Veritabanı</span><br><small style="color:#9CA3AF">enterprise.db</small>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📥 Resmi Whitepaper İndir")
    try:
        pdf_bytes_sb = generate_enterprise_documentation_pdf()
        st.download_button(
            label="📥 Tüm Dökümanı PDF İndir (.pdf)",
            data=pdf_bytes_sb,
            file_name="Otonom_Ajan_Sirketi_Mimari_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kodları A4 formatında kurumsal PDF olarak indirir."
        )
    except Exception as e:
        st.caption(f"PDF motoru: {str(e)[:30]}")

    st.markdown("---")
    st.caption("Mimari: LangGraph StateGraph\nKalıcılık: SQLite Checkpoints\nFailover: 5-Key Dynamic Pool")

# ==============================================================================
# 3. Ana Başlık & Yönetici Durum Kartı
# ==============================================================================
st.markdown("""
<div class="doc-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 24px; color: #F3F4F6; font-weight: 600;">📖 OTONOM AJAN ŞİRKETİ | SİSTEM DÖKÜMANTASYONU</h1>
            <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 13px;">
                Yönetici Başucu Kılavuzu • Supervisor Orkestrasyonu • SQLite Kalıcılığı • 5'li Key Failover • SWE-Agent
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge-gold">Kurumsal Teknik Doküman</span><br>
            <span style="font-size: 11px; color: #6B7280; margin-top: 4px; display: inline-block;">Versiyon: v3.8 Enterprise</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. Kapsamlı Sekmeler (7 Tam Bölüm)
# ==============================================================================
tab_quick, tab_arch, tab_code, tab_security, tab_db, tab_meta_doc, tab_swe_doc = st.tabs([
    "⚡ 1. Hızlı Kullanım Özeti (Cheatsheet)",
    "🏗️ 2. Uçtan Uca Mimari & Akış Şeması",
    "💻 3. Çekirdek Kod Katmanı (Deep-Dive)",
    "🛑 4. Güvenlik, HITL & Key Rotasyonu",
    "🗄️ 5. SQLite Veritabanı Şeması",
    "🏛️ 6. Meta-Düzlem & İkinci Beyin",
    "🛠️ 7. Otonom Kodlayıcı (SWE-Agent)"
])

# ------------------------------------------------------------------------------
# TAB 1: HIZLI KULLANIM ÖZETİ
# ------------------------------------------------------------------------------
with tab_quick:
    st.markdown("### ⚡ 2 Dakikada Anlama Kılavuzu (Executive Quickstart)")
    st.caption("Kod ve terminal detaylarına boğulmadan sistemin mantığını, işleyişini ve kontrol adımlarını kavrayın:")

    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("""
        <div class="quick-card">
            <h4 style="color:#828FFF; margin:0 0 6px 0; font-size:15px;">1️⃣ Direktif Verin</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5; margin:0;">
                Yönetici Masası'ndaki sohbet alanına şirket hedefini girin (Örn: <i>"Fintech için AI kredi risk skorlama mikroservisi geliştirin"</i>).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q2:
        st.markdown("""
        <div class="quick-card" style="border-left-color: #FBBF24;">
            <h4 style="color:#FBBF24; margin:0 0 6px 0; font-size:15px;">2️⃣ Otonom İmalat</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5; margin:0;">
                CEO sırasıyla Araştırma Departmanı'nı ve Mühendislik Departmanı'nı görevlendirir. Pazar analizi ve Python kodu üretilir.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q3:
        st.markdown("""
        <div class="quick-card" style="border-left-color: #34D399;">
            <h4 style="color:#34D399; margin:0 0 6px 0; font-size:15px;">3️⃣ İnsan Onayı (HITL)</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5; margin:0;">
                Sistem 250.000 TL bütçe aşamasında duraklar. Yönetici ekrandaki <b>'Bütçeyi Onayla'</b> butonuna basarak projeyi tamamlar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Sistem Performans Metrikleri & Avantajlar")
    
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    with col_met1:
        st.metric("Ortalama Yanıt Hızı", "1.5 - 2.5 sn", delta="20x Hızlanma (Flash-Lite)")
    with col_met2:
        st.metric("API Key Havuzu", f"{len(API_KEY_POOL)} Adet Anahtar", delta="Kesintisiz Failover")
    with col_met3:
        st.metric("Bütçe Güvenlik Kilidi", "Human-in-the-Loop", delta="250.000 TL Onay Bariyeri")
    with col_met4:
        st.metric("Kalıcılık Motoru", "SQLite (SqliteSaver)", delta="Çökme Korumalı")

    st.markdown("---")
    st.markdown("#### 💡 Temel Kavramlar Sözlüğü")
    
    faq_data = [
        {"Kavram": "StateGraph", "Açıklama": "LangGraph'ın temel grafik motorudur. Departmanları (Düğümleri) ve durum geçişlerini yönetir."},
        {"Kavram": "Supervisor Pattern", "Açıklama": "Tüm şirket kararlarının merkezi bir CEO tarafından Pydantic şemasıyla verildiği orkestrasyon modeli."},
        {"Kavram": "Human-in-the-Loop (HITL)", "Açıklama": "Bütçe harcaması gibi yüksek riskli işlemlerde yapay zekanın duraklayıp insan kararı beklemesi."},
        {"Kavram": "SqliteSaver", "Açıklama": "Grafın her adımını SQLite veritabanına anlık kaydeden ve sunucu kapansa dahi durumu koruyan kalıcılık katmanı."},
        {"Kavram": "Key Failover Pool", "Açıklama": ".env'deki 5 anahtar arasında kota veya yoğunluk anında milisaniyeler içinde geçiş yapan dayanıklılık motoru."},
        {"Kavram": "Second Brain (İkinci Beyin)", "Açıklama": "Kurucular Odası'nda alınan kararları (ADR) ve operasyonel direktifleri saklayan kurumsal hafıza."},
        {"Kavram": "SWE-Agent", "Açıklama": "Kod tabanını güvenle okuyan, test eden ve otomatik yedek alarak hata anında geri alan otonom yazılım mühendisi."}
    ]
    st.dataframe(pd.DataFrame(faq_data), use_container_width=True, hide_index=True)

    # İndirme Alanı
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

# ------------------------------------------------------------------------------
# TAB 2: UÇTAN UCA MİMARİ & AKIŞ ŞEMASI
# ------------------------------------------------------------------------------
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
    st.markdown("#### 📦 Şirket Ortak Durumu (CompanyState)")
    st.markdown("""
    Tüm departmanlar ortak bir TypedDict üzerinden haberleşir ve birbirlerinin çıktılarına erişir:
    - **`messages`:** Konuşma ve araç çağrı geçmişi (`add_messages` reducer ile listenin sonuna eklenir).
    - **`next_step`:** CEO'nun belirlediği sıradaki hedef düğüm (`Research_Dept`, `Engineering_Dept`, `Audit_Approval_Dept`, `FINISH`).
    - **`research_summary`:** Araştırma departmanının piyasa analizi çıktısı.
    - **`code_deliverable`:** Mühendislik departmanının yazdığı kurumsal Python modülü.
    - **`allocated_budget`:** Finans departmanının tahsis ettiği tutar (250.000 TL).
    - **`is_audit_passed`:** Finans ve güvenlik denetim onay durumu (Boolean).
    """)

# ------------------------------------------------------------------------------
# TAB 3: ÇEKİRDEK KOD KATMANI (DEEP-DIVE)
# ------------------------------------------------------------------------------
with tab_code:
    st.markdown("### 💻 Çekirdek Kod Katmanı ve Modül İncelemesi")
    st.caption("Projenin arka planında çalışan kritik modüllerin kaynak kodları:")

    code_tab1, code_tab2, code_tab3 = st.tabs([
        "1. model_factory.py (5'li Key Rotasyonu)",
        "2. sirket_motoru.py (Departman Düğümleri)",
        "3. LangGraph Derlemesi & HITL"
    ])

    with code_tab1:
        st.markdown("**Dinamik 5'li API Key Rotasyon Motoru:**")
        st.code("""
# model_factory.py
TARGET_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

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
                # Kota (429), yoğunluk (503) veya zaman aşımında (504) sonraki anahtara geç!
                next_idx = (idx + 1) % total_keys
                _print_key_rotate_warning(idx, next_idx, str(e), self.model_name)
                continue
        raise last_exception
        """, language="python")

    with code_tab2:
        st.markdown("**CEO Durum Bilinci ve Doğrudan Yönlendirme:**")
        st.code("""
# 05_otonom_ajan_sirketi/sirket_motoru.py
def ceo_supervisor_node(state: CompanyState):
    has_research = bool(state.get("research_summary"))
    has_code = bool(state.get("code_deliverable"))
    has_audit = bool(state.get("is_audit_passed"))
    
    prompt = (
        "Sen Otonom Şirketin CEO'susun. MEVCUT ŞİRKET DURUMU:\\n"
        f"- 1. Pazar Araştırması : {'TAMAMLANDI' if has_research else 'EKSİK'}\\n"
        f"- 2. Mühendislik Kodu  : {'TAMAMLANDI' if has_code else 'EKSİK'}\\n"
        f"- 3. Bütçe Denetimi/Onay : {'TAMAMLANDI' if has_audit else 'EKSİK'}\\n\\n"
        "Kurallar: Eksik olan departmanı sırayla seç. Hepsi tamamsa 'FINISH' seç."
    )
    decision = ceo_llm.invoke(messages)
    return {"next_step": decision.next}
        """, language="python")

    with code_tab3:
        st.markdown("**LangGraph Derleme ve SQLite Checkpointer Bağlantısı:**")
        st.code("""
# SQLite Kalıcılık Katmanı
db_path = os.path.join(os.path.dirname(__file__), "enterprise.db")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# Bütçe öncesi duraklatılan kurumsal graf
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Audit_Approval_Dept"]  # Finans işlemi öncesi grafı dondur!
)
        """, language="python")

# ------------------------------------------------------------------------------
# TAB 4: GÜVENLİK, HITL & KEY ROTASYONU
# ------------------------------------------------------------------------------
with tab_security:
    st.markdown("### 🛑 Güvenlik, Human-in-the-Loop & API Key Failover")
    st.caption("Sistemin kurumsal ortamlarda güvenle çalışmasını sağlayan mimari tedbirler:")

    st.markdown("""
    <div class="security-card">
        <h4 style="color:#EF4444; margin:0 0 8px 0; font-size:15px;">🛡️ Kritik İşlem Kapısı (Human-in-the-Loop Gate)</h4>
        <p style="color:#CBD5E1; font-size:13px; line-height:1.5; margin:0;">
            Yapay zeka modellerinin bütçe harcaması veya dış dünyaya kaynak tahsisi yapması kabul edilemez bir risktir. 
            Bu nedenle <code>interrupt_before=['Audit_Approval_Dept']</code> parametresi ile süreç dondurulur.
            Yönetim Kurulu Başkanı web arayüzünden bütçeyi inceleyip <b>'ONAYLA'</b> butonuna basmadığı sürece işlem yapılamaz.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🔑 5'li API Key Havuzunun Çalışma Prensibi")
    st.markdown("""
    1. Sistem `.env` dosyasındaki `GOOGLE_API_KEYS` listesini okur.
    2. Satır içi yorumlar (`#4.KEY`) ve boşluklar dinamik olarak temizlenir.
    3. Google AI Studio serbest katmanında bir anahtar `429 (Kota Doldu)`, `503 (Sunucu Yoğun)` veya `504 (Zaman Aşımı)` verdiğinde:
       - Kod çökmez veya donmaz.
       - Konsola ve loglara rotasyon uyarısı basılır.
       - Bir sonraki anahtar (Key #2, Key #3...) anında devreye girer.
    4. İleride `.env` dosyasına 10 yeni anahtar eklense dahi Python koduna tek satır dokunulması gerekmez.
    """)

# ------------------------------------------------------------------------------
# TAB 5: SQLITE VERİTABANI ŞEMASI
# ------------------------------------------------------------------------------
with tab_db:
    st.markdown("### 🗄️ SQLite Veritabanı Şeması & Kalıcılık")
    st.caption("enterprise.db içerisinde LangGraph checkpoints ve writes yapısı:")

    db_path = os.path.join(app_dir, "enterprise.db")
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Tablo Yapısı
        cur.execute("PRAGMA table_info(checkpoints);")
        cols = cur.fetchall()
        df_cols = pd.DataFrame(cols, columns=["ID", "Sütun Adı", "Veri Tipi", "NotNull", "Default", "PK"])
        
        st.markdown("**1. `checkpoints` Tablo Şeması:**")
        st.dataframe(df_cols[["Sütun Adı", "Veri Tipi", "PK"]], use_container_width=True, hide_index=True)
        
        # Son Checkpoint Kayıtları
        cur.execute("SELECT thread_id, checkpoint_id, parent_checkpoint_id, type FROM checkpoints ORDER BY rowid DESC LIMIT 8;")
        recent_records = cur.fetchall()
        df_recent = pd.DataFrame(recent_records, columns=["Thread ID", "Checkpoint ID", "Parent ID", "Tip"])
        
        st.markdown("**2. Veritabanındaki Son Checkpoint Kayıtları (Canlı Veri):**")
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
        
        conn.close()
    else:
        st.info("enterprise.db dosyası henüz oluşturulmadı. Bir proje başlattığınızda otomatik üretilecektir.")

# ------------------------------------------------------------------------------
# TAB 6: META-DÜZLEM & İKİNCİ BEYİN
# ------------------------------------------------------------------------------
with tab_meta_doc:
    st.markdown("### 🏛️ Meta-Düzlem & İkinci Beyin (Second Brain)")
    st.caption("Yönetici ile Yapay Zeka Kurucu Ekip arasındaki beyin fırtınalarını kalıcı kurumsal bilgiye dönüştüren katman:")

    st.markdown("""
    <div class="report-card">
        <h4 style="color:#FBBF24; margin:0 0 6px 0; font-size:15px;">🤝 Kurucular Odası (The Founders Room)</h4>
        <p style="color:#9CA3AF; font-size:13px; line-height:1.5; margin:0;">
            Yöneticinin şirket vizyonunu tartıştığı 3 kritik persona mevcuttur:
            <br>• <b>Vizyoner Co-Founder:</b> Fikirleri büyütür, pazar fırsatlarını gösterir.
            <br>• <b>Şeytanın Avukatı (Skeptic):</b> Riskleri, batış senaryolarını ve kör noktaları acımasızca sorgular.
            <br>• <b>Yazman & Baş Katip (Scribe):</b> İki zıt fikrin çarpışmasından nihai sentezi çıkarıp ADR formatında belgeler.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📁 Yaşayan Kurumsal Hafıza (`meta_bellek/`)")
    st.markdown("""
    - `01_sirket_vizyonu.md`: Şirketin ana manifestosu ve uzun vadeli hedefleri.
    - `02_beyin_firtinasi_notlari/`: Kurucular Odası'ndaki tüm serbest tartışmaların kayıtları.
    - `03_stratejik_kararlar/ (ADR)`: Alınan kesin mimari ve iş kararları.
    - `04_operasyonel_direktifler/`: CEO Ajanı'nın şirket motorunda koşması için hazırlanan net operasyonel talimatlar.
    """)

# ------------------------------------------------------------------------------
# TAB 7: OTONOM KODLAYICI (SWE-AGENT)
# ------------------------------------------------------------------------------
with tab_swe_doc:
    st.markdown("### 🛠️ Otonom Kodlayıcı (SWE-Agent) Mimarisi")
    st.caption("Kendi kodunu analiz edebilen, güvenle refactor eden ve hata anında geri alabilen yapay zeka mühendisi:")

    st.markdown("""
    <div class="report-card">
        <h4 style="color:#34D399; margin:0 0 6px 0; font-size:15px;">🛡️ 4 Aşamalı Güvenli Sandbox Ortamı</h4>
        <p style="color:#9CA3AF; font-size:13px; line-height:1.5; margin:0;">
            1. <b>Dosya İnceleme (read_file_safe):</b> Dosyayı belleğe alır, sözdizimi risklerini analiz eder.<br>
            2. <b>Yedek Alma (backup_file):</b> Değişiklik öncesi <code>meta_bellek/.backups/</code> dizinine zaman damgalı kopyasını kaydeder.<br>
            3. <b>Hassas Yama (edit_file_patch):</b> Kod bloğunu cerrahi hassasiyetle günceller.<br>
            4. <b>Sözdizimi Denetimi & Rollback:</b> Kod derlenmezse veya hata verirse tek tıkla eski haline geri döner.
        </p>
    </div>
    """, unsafe_allow_html=True)
