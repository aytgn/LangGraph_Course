"""
================================================================================
👑 OTONOM AJAN ŞİRKETİ - YÖNETİCİ KOKPİTİ (EXECUTIVE MANAGEMENT DESK) 👑
================================================================================
Linear / Apple Minimalist Tasarım Sistemi & Çift Düzlemli Bilişsel Mimari.
Tüm zengin kurumsal fonksiyonlar (Meta-Düzlem, CEO Masası, Raporlar,
SQLite Kalıcılık, Departman Radarı) sade, göz yormayan ve gerektiğinde açılan
'Gelişmiş Seçenekler (Advanced)' mimarisiyle yapılandırılmıştır.
================================================================================
"""

import os
import sys
import time
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Çalışma dizini ve departman modüllerinin yüklenmesi
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "05_otonom_ajan_sirketi"))
sys.path.insert(0, current_dir)

load_dotenv()

import sirket_motoru
from langchain_core.messages import HumanMessage, AIMessage
from model_factory import API_KEY_POOL, TARGET_MODEL, get_gemini_llm

from meta_katman.meta_motoru import (
    chat_with_cofounder,
    chat_with_skeptic,
    run_boardroom_council_debate,
    save_session_as_brainstorm,
    save_session_as_adr
)
from meta_katman.ikinci_beyin import (
    get_company_vision,
    update_company_vision,
    list_vault_documents,
    read_document_content
)
from meta_katman.direktif_koprusu import bridge_meta_to_operational_directive

# ==============================================================================
# 1. Sayfa Yapılandırması ve Minimalist Linear/Apple Tasarım Sistemi
# ==============================================================================
st.set_page_config(
    page_title="Otonom Ajan Şirketi | Yönetici Masası",
    page_icon="👑",
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

    /* Streamlit Varsayılan Çoklu Sayfa Menüsünü (SidebarNav) Gizle */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Kenar Çubuğu (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: var(--surface-1) !important;
        border-right: 1px solid var(--hairline) !important;
    }

    /* Üst Durum Çubuğu (Executive Header) */
    .executive-header {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 20px;
    }

    /* Operasyon Takip Çizelgesi (Executive Stepper) */
    .stepper-panel {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .step-card {
        background-color: var(--surface-2);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 10px 12px;
        min-height: 85px;
        transition: all 0.2s ease;
    }
    .step-card:hover {
        border-color: var(--hairline-strong);
    }
    .step-card-done {
        border-color: rgba(16, 185, 129, 0.40) !important;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.01) 100%) !important;
    }
    .step-card-hitl {
        border-color: rgba(244, 63, 94, 0.65) !important;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.12) 0%, rgba(225, 29, 72, 0.04) 100%) !important;
    }
    .step-card-running {
        border-color: rgba(56, 189, 248, 0.60) !important;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.10) 0%, rgba(14, 165, 233, 0.03) 100%) !important;
    }
    .step-card-pending {
        border-color: rgba(255, 255, 255, 0.06) !important;
        opacity: 0.65;
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

    /* Rafine Kartlar */
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

    /* Human-in-the-Loop Onay Kutusu (Sakin Otoriter Tasarım) */
    .hitl-box {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.06) 0%, rgba(225, 29, 72, 0.03) 100%);
        border: 1px solid rgba(244, 63, 94, 0.35);
        border-left: 4px solid #F43F5E;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 18px 0;
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
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background-color: var(--surface-1);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--surface-2) !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Butonlar */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 13px;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border: none !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-hover) !important;
    }

    /* Expander / Akordiyon */
    .streamlit-expanderHeader {
        background-color: var(--surface-1) !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        color: var(--text-secondary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. Veritabanı Yardımcı Fonksiyonları (SQLite Görselleştirme)
# ==============================================================================
DB_PATH = os.path.join(current_dir, "05_otonom_ajan_sirketi", "enterprise.db")

def get_all_threads():
    """enterprise.db içerisindeki tüm proje oturumlarını listeler."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id DESC")
        threads = [r[0] for r in cur.fetchall()]
        conn.close()
        return threads
    except Exception:
        return []

def get_thread_checkpoint_count(thread_id: str) -> int:
    """Belirli bir thread'in kaç adımdan oluştuğunu sorgular."""
    if not os.path.exists(DB_PATH):
        return 0
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

def get_database_statistics():
    """Tüm SQLite veritabanı istatistiklerini hesaplar."""
    if not os.path.exists(DB_PATH):
        return {"total_threads": 0, "total_checkpoints": 0, "db_size_kb": 0}
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT count(DISTINCT thread_id), count(*) FROM checkpoints")
        t_count, c_count = cur.fetchone()
        conn.close()
        size_kb = round(os.path.getsize(DB_PATH) / 1024, 2)
        return {"total_threads": t_count, "total_checkpoints": c_count, "db_size_kb": size_kb}
    except Exception:
        return {"total_threads": 0, "total_checkpoints": 0, "db_size_kb": 0}

def get_clean_text(content) -> str:
    """Gemini mesaj bloklarını temiz okunabilir metne dönüştürür."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)

def get_pipeline_status(thread_id: str) -> dict:
    """Belirtilen proje için tüm departmanların anlık durum ve çıktı özetini döndürür."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snap = sirket_motoru.app.get_state(config)
    except Exception:
        snap = None
        
    values = snap.values if snap and snap.values else {}
    next_nodes = snap.next if snap and snap.next else ()
    
    has_messages = bool(values.get("messages"))
    has_research = bool(values.get("research_summary"))
    has_code = bool(values.get("code_deliverable"))
    is_audit_passed = bool(values.get("is_audit_passed"))
    allocated_budget = values.get("allocated_budget")
    is_waiting_hitl = bool("Audit_Approval_Dept" in next_nodes)
    
    # 1. CEO & Strateji
    if has_messages or has_research or has_code:
        s1 = {"status": "done", "label": "✅ TAMAMLANDI", "class": "step-card-done", "detail": "Direktif analiz edildi, strateji belirlendi."}
    else:
        s1 = {"status": "pending", "label": "⚪ BEKLEMEDE", "class": "step-card-pending", "detail": "Yönetim Kurulu direktifi bekleniyor."}
        
    # 2. Pazar Araştırması
    if has_research:
        s2 = {"status": "done", "label": "✅ TAMAMLANDI", "class": "step-card-done", "detail": "Sektör ve rakip pazar istihbaratı hazır."}
    elif has_messages and not has_code and not is_waiting_hitl and not is_audit_passed:
        s2 = {"status": "running", "label": "⏳ ANALİZ EDİLİYOR", "class": "step-card-running", "detail": "Pazar dinamikleri taranıyor..."}
    else:
        s2 = {"status": "pending", "label": "⚪ SIRADA", "class": "step-card-pending", "detail": "Pazar araştırması sırada bekliyor."}
        
    # 3. Yazılım Mühendisliği
    if has_code:
        s3 = {"status": "done", "label": "✅ TAMAMLANDI", "class": "step-card-done", "detail": "Kurumsal Python mikroservis kodu derlendi."}
    elif has_research and not is_waiting_hitl and not is_audit_passed:
        s3 = {"status": "running", "label": "⏳ KODLANIYOR", "class": "step-card-running", "detail": "FastAPI mimarisi inşa ediliyor..."}
    else:
        s3 = {"status": "pending", "label": "⚪ SIRADA", "class": "step-card-pending", "detail": "Pazar raporu sonrası kodlanacak."}
        
    # 4. Bütçe Denetimi (HITL)
    if is_audit_passed and allocated_budget:
        s4 = {"status": "done", "label": "✅ ONAYLANDI", "class": "step-card-done", "detail": f"{allocated_budget:,.0f} TL bütçe tahsis edildi (BGT-8842)."}
    elif is_waiting_hitl:
        s4 = {"status": "hitl", "label": "🛑 ONAY BEKLİYOR", "class": "step-card-hitl", "detail": "250.000 TL şirket bütçesi için Yönetim Kurulu onayı bekleniyor."}
    else:
        s4 = {"status": "pending", "label": "⚪ SIRADA", "class": "step-card-pending", "detail": "Mühendislik kodu onayına tabi."}
        
    # 5. Nihai Teslimat
    if is_audit_passed and not is_waiting_hitl:
        s5 = {"status": "done", "label": "🚀 TESLİM EDİLDİ", "class": "step-card-done", "detail": "Proje başarıyla tamamlandı, raporlar hazır."}
    else:
        s5 = {"status": "pending", "label": "⚪ SIRADA", "class": "step-card-pending", "detail": "Bütçe onayı sonrası teslim edilecek."}
        
    overall = "YENİ PROJE"
    overall_color = "#6B7280"
    if is_waiting_hitl:
        overall = "🛑 YÖNETİCİ ONAYI BEKLENİYOR (HITL)"
        overall_color = "#FB7185"
    elif is_audit_passed and not is_waiting_hitl:
        overall = "✅ PROJE TAMAMLANDI & TESLİM EDİLDİ"
        overall_color = "#34D399"
    elif has_messages:
        overall = "⚡ OPERASYON YÜRÜTÜLÜYOR"
        overall_color = "#38BDF8"

    return {
        "is_waiting_hitl": is_waiting_hitl,
        "is_completed": bool(is_audit_passed and not is_waiting_hitl),
        "overall_text": overall,
        "overall_color": overall_color,
        "steps": [
            {"num": "1", "name": "👑 CEO & Strateji", "dept": "Executive Board", **s1},
            {"num": "2", "name": "🔬 Pazar Araştırması", "dept": "Araştırma Dept", **s2},
            {"num": "3", "name": "💻 Mühendislik Kodu", "dept": "Yazılım Dept", **s3},
            {"num": "4", "name": "🛑 Bütçe Onayı (HITL)", "dept": "Finans & Denetim", **s4},
            {"num": "5", "name": "🚀 Nihai Teslimat", "dept": "Operasyon", **s5},
        ]
    }

def render_pipeline_stepper(thread_id: str):
    """Canlı Operasyon & Departman Takip Çizelgesini görselleştirir."""
    pipeline = get_pipeline_status(thread_id)
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding: 2px 2px;">
        <div style="font-size:13px; font-weight:600; color:#E2E8F0; letter-spacing:0.02em;">
            🏢 CANLI OPERASYON & DEPARTMAN ÇALIŞMA DURUMU
        </div>
        <div>
            <span style="font-size:12px; font-weight:600; color:{pipeline['overall_color']};">
                {pipeline['overall_text']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(5)
    for i, step in enumerate(pipeline["steps"]):
        with cols[i]:
            st.markdown(f"""
            <div class="step-card {step['class']}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:11px; font-weight:600; color:#F8FAFC;">{step['name']}</span>
                </div>
                <div style="font-size:10px; margin-bottom:5px;">
                    <span style="font-weight:600;">{step['label']}</span>
                </div>
                <div style="font-size:10px; color:#9CA3AF; line-height:1.3;">
                    {step['detail']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 3. Oturum Durumu (Session State) Yönetimi
# ==============================================================================
all_threads = get_all_threads()
default_thread = all_threads[0] if all_threads else f"holding-proje-{datetime.now().strftime('%Y%m%d-%H%M')}"

if "active_thread_id" not in st.session_state:
    st.session_state.active_thread_id = default_thread

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "is_running" not in st.session_state:
    st.session_state.is_running = False

if "waiting_for_hitl" not in st.session_state:
    st.session_state.waiting_for_hitl = False

if "current_deliverables" not in st.session_state:
    st.session_state.current_deliverables = {
        "research_summary": None,
        "code_deliverable": None,
        "allocated_budget": None,
        "is_audit_passed": False,
        "ceo_closing": None
    }

if "meta_chat_history" not in st.session_state:
    st.session_state.meta_chat_history = []

if "meta_pending_directive" not in st.session_state:
    st.session_state.meta_pending_directive = None

# ==============================================================================
# 4. Yan Menü (Sidebar) - Şirket Paneli & Ajan Radarı
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 OTONOM AJAN HOLDİNG")
    st.caption("Executive Management Cockpit • v4.0")
    
    # Harici Kapsamlı Dokümantasyon Bağlantıları
    st.link_button(
        "📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗",
        url="/LangGraph_Basucu_Kitabi",
        type="primary",
        use_container_width=True
    )
    st.link_button(
        "📖 Sistem Dokümantasyonu (Yeni Sekme) ↗",
        url="/Sistem_Dokumantasyonu",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown("#### 📡 Ajan & Altyapı Radarı")
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f'<span class="badge-gold">👑 CEO Ajanı</span><br><small style="color:#9CA3AF">Hazır & Aktif</small>', unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f'<span class="badge-cyan">⚡ Model</span><br><small style="color:#9CA3AF">{TARGET_MODEL}</small>', unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.markdown(f'<span class="badge-green">🔑 Key Havuzu</span><br><small style="color:#9CA3AF">{len(API_KEY_POOL)} Adet (.env)</small>', unsafe_allow_html=True)
    with col_sb4:
        st.markdown(f'<span class="badge-cyan">💾 SQLite DB</span><br><small style="color:#9CA3AF">enterprise.db</small>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏛️ Meta-Düzlem & İkinci Beyin")
    meta_doc_count = len(list_vault_documents())
    st.markdown(f'<span class="badge-gold">📚 Yaşayan Belge: {meta_doc_count} Adet</span>', unsafe_allow_html=True)
    st.caption("🤝 Co-Founder • ⚡ The Skeptic • 📜 Chief of Staff")

    st.markdown("---")
    st.markdown("#### 📂 Proje Oturumu (Thread ID)")
    
    thread_options = ["➕ Yeni Proje Oluştur..."] + all_threads
    current_index = 0
    if st.session_state.active_thread_id in all_threads:
        current_index = thread_options.index(st.session_state.active_thread_id)
        
    selected_option = st.selectbox(
        "Kayıtlı Proje Seçin / İnceleyin:",
        options=thread_options,
        index=current_index,
        help="Veritabanındaki geçmiş projeler veya yeni bir çalışma alanı"
    )
    
    if selected_option == "➕ Yeni Proje Oluştur...":
        new_id_input = st.text_input("Yeni Proje Kodu:", value=f"holding-proje-{datetime.now().strftime('%Y%m%d-%H%M')}")
        if st.button("✨ Çalışma Alanını Başlat", use_container_width=True):
            st.session_state.active_thread_id = new_id_input
            st.session_state.waiting_for_hitl = False
            st.session_state.current_deliverables = {
                "research_summary": None,
                "code_deliverable": None,
                "allocated_budget": None,
                "is_audit_passed": False,
                "ceo_closing": None
            }
            st.session_state.chat_history = [
                {"role": "assistant", "content": f"Sayın Yönetim Kurulu Başkanı, '{new_id_input}' nolu yeni çalışma alanınız oluşturuldu. Göreve hazırım."}
            ]
            st.rerun()
    else:
        if selected_option != st.session_state.active_thread_id:
            st.session_state.active_thread_id = selected_option
            cfg = {"configurable": {"thread_id": selected_option}}
            snap = sirket_motoru.app.get_state(cfg)
            if snap and snap.values:
                st.session_state.current_deliverables = {
                    "research_summary": snap.values.get("research_summary"),
                    "code_deliverable": snap.values.get("code_deliverable"),
                    "allocated_budget": snap.values.get("allocated_budget"),
                    "is_audit_passed": snap.values.get("is_audit_passed", False),
                    "ceo_closing": get_clean_text(snap.values["messages"][-1].content) if snap.values.get("messages") else None
                }
                st.session_state.chat_history = []
                for m in snap.values.get("messages", []):
                    role = "user" if isinstance(m, HumanMessage) else "assistant"
                    st.session_state.chat_history.append({"role": role, "content": get_clean_text(m.content)})
                
                st.session_state.waiting_for_hitl = bool(snap.next and "Audit_Approval_Dept" in snap.next)
            st.rerun()

    # Gelişmiş Hızlı Direktifler (Expander altında sakinleştirildi)
    with st.expander("⚡ Hızlı Yönetici Direktifleri", expanded=False):
        quick_prompts = [
            ("🛡️ Fintech AI Risk & Skorlama Servisi", "Fintech sektörü için yapay zeka destekli otonom kredi skorlama ve dolandırıcılık tespit mikroservisi geliştirin. Pazar dinamiklerini araştırın ve 250.000 TL bütçe onayı talep edin."),
            ("🏥 Sağlık AI Tahlil Analiz API'si", "Sağlık sektörü için KVKK ve HIPAA uyumlu otonom tahlil özetleme ve doktor asistanı mikroservisi inşa edin. Pazar analizini yapın ve bütçeyi hazırlayın."),
            ("🛒 E-Ticaret Akıllı Fiyatlandırma", "Büyük ölçekli e-ticaret siteleri için dinamik yapay zeka fiyat optimizasyon servisi oluşturun. Sektörü inceleyin ve onay sürecini başlatın.")
        ]
        for label, text in quick_prompts:
            if st.button(label, use_container_width=True):
                st.session_state.quick_directive = text
                st.rerun()

# ==============================================================================
# 5. Ana Başlık & Yönetici Durum Kartı
# ==============================================================================
st.markdown(f"""
<div class="executive-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 600; color: #F8FAFC;">👑 OTONOM AJAN HOLDİNG | YÖNETİCİ KOKPİTİ</h1>
            <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 13px;">
                Yönetim Kurulu Başkanı Çalışma Masası • Meta-Strateji • Operasyonel Orkestrasyon • Canlı İnsan Onayı (HITL)
            </p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em;">Aktif Proje</span><br>
            <span class="badge-gold" style="font-size: 13px;">🏷️ {st.session_state.active_thread_id}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. Ana Sekmeler (Executive Cockpit Tabs)
# ==============================================================================
tab_meta, tab_chat, tab_reports, tab_database, tab_radar = st.tabs([
    "🏛️ 0. Kurucular Odası & İkinci Beyin",
    "💬 1. CEO İletişim Masası",
    "📋 2. Raporlar & Çıktılar",
    "🗄️ 3. Veritabanı & Denetim",
    "🏢 4. Şirket Radarı & Organizasyon"
])

# ------------------------------------------------------------------------------
# TAB 0: KURUCULAR ODASI & İKİNCİ BEYİN (META-DÜZLEM)
# ------------------------------------------------------------------------------
with tab_meta:
    st.markdown("#### 🏛️ Kurucular Odası & İkinci Beyin (Meta-Strateji Masası)")
    st.caption("Operasyonel kod karmaşasından izole; yapay zeka kurucu ortağınızla vizyon, pivotlar ve felsefeyi tartışın, kalıcı Markdown kasasında arşivleyin.")

    # Meta-Ajan Rozetleri
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown('<span class="badge-gold">🤝 AI Co-Founder</span><br><small style="color:#9CA3AF">Vizyon & Stratejik Düşünce</small>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<span class="badge-cyan">⚡ The Skeptic</span><br><small style="color:#9CA3AF">Şeytanın Avukatı / Red Team</small>', unsafe_allow_html=True)
    with col_m3:
        st.markdown('<span class="badge-green">📜 Chief of Staff</span><br><small style="color:#9CA3AF">Hafıza & ADR Muhafızı</small>', unsafe_allow_html=True)
    with col_m4:
        all_vault_docs = list_vault_documents()
        st.markdown(f'<span class="badge-gold">📚 Bilgi Kasası</span><br><small style="color:#9CA3AF">{len(all_vault_docs)} Yaşayan Belge</small>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Çalışma Modu
    meta_mode = st.radio(
        "🎯 Masadaki Görüşme Modu:",
        [
            "🤝 Co-Founder ile Serbest Sohbet (Vizyon, Felsefe, Şirket Yapısı & Dış Dünya)",
            "⚡ Şeytanın Avukatı ile Stres Testi (Kör Noktalar, Maliyet Tuzakları, Batış Riskleri)",
            "🏛️ Kurucular Konseyi (Yuvarlak Masa: Co-Founder + Skeptic Çarpışması & Sentez)"
        ],
        horizontal=True
    )

    # Sohbet Alanı
    meta_chat_container = st.container(height=360)
    with meta_chat_container:
        if not st.session_state.meta_chat_history:
            st.info("👋 Hoş geldiniz Sayın Başkan! Masadaki yeriniz hazır. Vizyonunuzu, yeni bir iş modelini veya şirket dışındaki konuları konuşmaya hazırım.")
        
        for msg in st.session_state.meta_chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                with st.chat_message("user", avatar="👔"): st.write(content)
            elif role == "Co-Founder":
                with st.chat_message("assistant", avatar="🤝"): st.markdown(f"**🤝 [CO-FOUNDER]:**\n\n{content}")
            elif role == "Skeptic":
                with st.chat_message("assistant", avatar="⚡"): st.markdown(f"**⚡ [ŞEYTANIN AVUKATI]:**\n\n{content}")
            elif role == "Scribe":
                with st.chat_message("assistant", avatar="📜"): st.markdown(f"**📜 [CHIEF OF STAFF SENTEZİ]:**\n\n{content}")
            else:
                with st.chat_message("assistant", avatar="🏛️"): st.markdown(content)

    # Hızlı Aksiyon Araç Çubuğu
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    with col_act1:
        if st.button("💡 Beyin Fırtınası Kaydet", use_container_width=True):
            if not st.session_state.meta_chat_history:
                st.warning("Kaydedilecek bir geçmiş yok.")
            else:
                with st.spinner("📜 Kaydediliyor..."):
                    saved_path = save_session_as_brainstorm(st.session_state.meta_chat_history)
                    st.success(f"✅ Kaydedildi: `{os.path.basename(saved_path)}`")
    with col_act2:
        if st.button("🏛️ Stratejik Karar (ADR) Kaydet", use_container_width=True):
            if not st.session_state.meta_chat_history:
                st.warning("Kaydedilecek bir karar yok.")
            else:
                with st.spinner("📜 ADR oluşturuluyor..."):
                    saved_path = save_session_as_adr(st.session_state.meta_chat_history)
                    st.success(f"✅ ADR Kaydedildi: `{os.path.basename(saved_path)}`")
    with col_act3:
        if st.button("🚀 Operasyona Aktar (CEO'ya Gönder)", use_container_width=True, type="primary"):
            if not st.session_state.meta_chat_history:
                st.warning("Aktarılacak strateji henüz tartışılmadı.")
            else:
                with st.spinner("🎯 CEO direktifine dönüştürülüyor..."):
                    bridge_res = bridge_meta_to_operational_directive(st.session_state.meta_chat_history)
                    st.session_state.quick_directive = bridge_res["directive_text"]
                    st.success(f"✅ '{bridge_res['title']}' CEO Masasına aktarıldı!")
    with col_act4:
        if st.button("🧹 Odayı Temizle", use_container_width=True):
            st.session_state.meta_chat_history = []
            st.rerun()

    meta_input = st.chat_input("Kurucular Odasında tartışılacak fikri veya sorunuzu yazın...", key="meta_chat_input")
    if meta_input:
        st.session_state.meta_chat_history.append({"role": "user", "content": meta_input})
        if "Co-Founder ile Serbest" in meta_mode:
            with st.spinner("🤝 Co-Founder düşünüyor..."):
                reply = chat_with_cofounder(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": reply})
                st.rerun()
        elif "Şeytanın Avukatı" in meta_mode:
            with st.spinner("⚡ Şeytanın Avukatı inceliyor..."):
                reply = chat_with_skeptic(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": reply})
                st.rerun()
        else:
            with st.spinner("🏛️ Kurucular Konseyi toplanıyor..."):
                council = run_boardroom_council_debate(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": council["cofounder"]})
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": council["skeptic"]})
                st.session_state.meta_chat_history.append({"role": "Scribe", "content": council["scribe_synthesis"]})
                st.rerun()

    # GELİŞMİŞ: İkinci Beyin Kasası Gezgini (Advanced Expander)
    with st.expander("⚙️ Gelişmiş: İkinci Beyin Bilgi Kasası & Yaşayan Notlar (Knowledge Vault)", expanded=False):
        v_docs = list_vault_documents()
        if not v_docs:
            st.info("Kasada henüz belge yok.")
        else:
            col_vd1, col_vd2 = st.columns([1, 2])
            with col_vd1:
                doc_labels = [f"{d['category']} | {d['name']}" for d in v_docs]
                sel_idx = st.selectbox("İncelemek istediğiniz belgeyi seçin:", range(len(v_docs)), format_func=lambda i: doc_labels[i])
                chosen_doc = v_docs[sel_idx]
                st.info(f"**Kategori:** {chosen_doc['category']}\n\n**Dosya:** `{chosen_doc['rel_path']}`\n\n**Boyut:** {chosen_doc['size_kb']} KB")
            with col_vd2:
                doc_content = read_document_content(chosen_doc["path"])
                if "01_sirket_vizyonu.md" in chosen_doc["name"]:
                    edited_vision = st.text_area("Şirket Vizyonunu Düzenle:", value=doc_content, height=260)
                    if st.button("💾 Vizyonu Güncelle & Kaydet"):
                        if update_company_vision(edited_vision):
                            st.success("✅ Şirket Vizyonu güncellendi!")
                            st.rerun()
                else:
                    st.markdown(f"```markdown\n{doc_content}\n```")

# ------------------------------------------------------------------------------
# TAB 1: CEO İLETİŞİM & CANLI OPERASYON MASASI
# ------------------------------------------------------------------------------
with tab_chat:
    st.markdown("#### 👑 CEO Strateji Masası ile Doğrudan İletişim")
    st.caption("Doğrudan ana ajanınızla (CEO) konuşun, şirket direktifi verin veya departmanları seferber edin.")

    # CANLI OPERASYON VE DEPARTMAN İLERLEME ÇİZELGESİ (EXECUTIVE STEPPER)
    render_pipeline_stepper(st.session_state.active_thread_id)

    # Sohbet Geçmişi Alanı
    chat_container = st.container(height=340)
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Merhaba Sayın Yönetim Kurulu Başkanı! Ben Otonom Şirketinizin CEO'suyum. Pazar araştırması, yazılım mimarisi veya bütçe süreçlerini başlatmak için direktifinizi bekliyorum.")
        
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👔"): st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="👑"): st.write(msg["content"])

    # HUMAN-IN-THE-LOOP (HITL) CANLI ONAY KARTI (Linear Rafine Tasarım)
    if st.session_state.waiting_for_hitl:
        st.markdown("""
        <div class="hitl-box">
            <h4 style="color:#FB7185; margin:0 0 8px 0; font-size:15px; font-weight:600;">🛑 YÖNETİCİ BÜTÇE ONAYI BEKLENİYOR (HUMAN-IN-THE-LOOP)</h4>
            <p style="color:#E2E8F0; font-size:13px; margin:0 0 12px 0; line-height:1.5;">
                Mühendislik ve Araştırma departmanları hazırlıklarını tamamladı. Şirket kasasından 
                <b style="color:#34D399;">250.000 TL</b> bütçe tahsis edilmesi için <b>Yönetim Kurulu Başkanı (Siz)</b> yetkisi bekleniyor.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_hitl1, col_hitl2 = st.columns([2, 1])
        with col_hitl1:
            if st.button("✅ 250.000 TL Şirket Bütçesini ONAYLA ve Projeyi Başlat", type="primary", use_container_width=True):
                with st.status("🏢 Bütçe Tahsisi İşleniyor & Teslimat Tamamlanıyor...", expanded=True) as status_box:
                    config = {"configurable": {"thread_id": st.session_state.active_thread_id}}
                    status_box.write("🛡️ **[Finans & Denetim]:** Başkanlık yetkisi işleniyor, 250.000 TL fon tahsis ediliyor...")
                    
                    for event in sirket_motoru.app.stream(None, config=config, stream_mode="updates"):
                        if not isinstance(event, dict):
                            continue
                        for node_name, node_output in event.items():
                            if node_name == "Audit_Approval_Dept":
                                status_box.write("🛡️ **[Finans & Denetim]:** Bütçe tahsisi onaylandı ve fon bloke edildi (Kod: BGT-8842).")
                            elif node_name == "CEO":
                                status_box.write("👑 **[CEO / Executive Board]:** Proje kapanış bildirimi onaylandı.")
                    
                    snapshot = sirket_motoru.app.get_state(config)
                    final_state = snapshot.values or {}
                    st.session_state.waiting_for_hitl = False
                    st.session_state.current_deliverables = {
                        "research_summary": final_state.get("research_summary"),
                        "code_deliverable": final_state.get("code_deliverable"),
                        "allocated_budget": final_state.get("allocated_budget"),
                        "is_audit_passed": final_state.get("is_audit_passed", False),
                        "ceo_closing": get_clean_text(final_state["messages"][-1].content) if final_state.get("messages") else None
                    }
                    status_box.update(label="🚀 Şirket Operasyonu Başarıyla Tamamlandı!", state="complete", expanded=False)
                    closing_text = st.session_state.current_deliverables["ceo_closing"] or "Proje başarıyla tamamlandı!"
                    st.session_state.chat_history.append({"role": "assistant", "content": f"👑 **[CEO BİLDİRİMİ]:** Sayın Başkanım, bütçe onayınız başarıyla işlendi ve şirket projesi tüm departmanlarca tamamlandı!\n\n{closing_text}"})
                    st.balloons()
                    st.rerun()
                    
        with col_hitl2:
            if st.button("❌ Bütçeyi Reddet / Projeyi Durdur", use_container_width=True):
                st.session_state.waiting_for_hitl = False
                st.session_state.chat_history.append({"role": "assistant", "content": "👑 **[CEO BİLDİRİMİ]:** Yönetim Kurulu bütçe tahsisini reddetti. İşlem durduruldu ve bütçe bloke edilmedi."})
                st.rerun()

    # Kullanıcı Girdi Alanı
    default_input = st.session_state.pop("quick_directive", "")
    user_prompt = st.chat_input("Yönetim Kurulu Direktifinizi buraya yazın...", key="user_chat_input")
    
    if default_input and not user_prompt:
        user_prompt = default_input

    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        is_task = any(w in user_prompt.lower() for w in ["başlat", "proje", "araştır", "kodla", "bütçe", "oluştur", "sistem", "servis"])
        config = {"configurable": {"thread_id": st.session_state.active_thread_id}}
        
        if is_task:
            with st.status("🏢 Otonom Şirket Operasyonu Canlı İcra Ediliyor...", expanded=True) as status_box:
                initial_input = {
                    "messages": [HumanMessage(content=user_prompt)],
                    "next_step": "CEO",
                    "research_summary": None,
                    "code_deliverable": None,
                    "allocated_budget": None,
                    "is_audit_passed": False
                }
                status_box.write("👑 **[CEO / Executive Board]:** Yönetim Kurulu direktifi inceleniyor...")
                
                for event in sirket_motoru.app.stream(initial_input, config=config, stream_mode="updates"):
                    if not isinstance(event, dict):
                        continue
                    for node_name, node_output in event.items():
                        if node_name == "CEO":
                            next_dept = node_output.get("next_step") if isinstance(node_output, dict) else "-"
                            status_box.write(f"👑 **[CEO / Executive Board]:** Stratejik inceleme tamamlandı ➔ Sıradaki Görev: `{next_dept}`")
                        elif node_name == "Research_Dept":
                            status_box.write("🔬 **[Araştırma Departmanı]:** Sektör ve rekabet istihbarat raporu tamamlandı.")
                        elif node_name == "Engineering_Dept":
                            status_box.write("💻 **[Mühendislik Departmanı]:** Kurumsal Python mikroservis üretim kodu derlendi.")
                        elif node_name == "Audit_Approval_Dept":
                            status_box.write("🛡️ **[Finans & Denetim]:** Bütçe tahsis süreci hazırlandı.")
                        elif node_name == "__interrupt__":
                            status_box.write("🛑 **[Güvenlik Kilidi]:** Bütçe yetkilendirme aşamasına ulaşıldı. Yönetim Kurulu onayı bekleniyor.")
                
                snapshot = sirket_motoru.app.get_state(config)
                st.session_state.current_deliverables["research_summary"] = snapshot.values.get("research_summary")
                st.session_state.current_deliverables["code_deliverable"] = snapshot.values.get("code_deliverable")
                
                if snapshot.next and "Audit_Approval_Dept" in snapshot.next:
                    st.session_state.waiting_for_hitl = True
                    status_box.update(label="🛑 Bütçe Onayı Bekleniyor (Human-in-the-Loop) - Departmanlar Hazır", state="running", expanded=True)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "👑 **[CEO]:** Pazar araştırması ve üretim kodu tamamlandı! Kurumsal güvenlik protokolü gereği **250.000 TL şirket bütçesi tahsisi için onayınız bekleniyor.**"
                    })
                else:
                    st.session_state.waiting_for_hitl = False
                    status_box.update(label="✅ Operasyon Başarıyla Tamamlandı", state="complete", expanded=False)
                    last_msg = snapshot.values["messages"][-1]
                    st.session_state.chat_history.append({"role": "assistant", "content": get_clean_text(last_msg.content)})
                
                st.rerun()
                
                st.rerun()
        else:
            with st.spinner("👑 CEO yanıtlıyor..."):
                ceo_chat_llm = get_gemini_llm(temperature=0.3)
                context = (
                    f"Sen Otonom Şirketin CEO'susun. Muhattabın Yönetim Kurulu Başkanıdır. "
                    f"Son derece profesyonel, saygılı, net ve güven veren bir yönetici üslubu kullan. "
                    f"Mevcut aktif proje: '{st.session_state.active_thread_id}'. "
                    f"Kullanıcı mesajı: '{user_prompt}'"
                )
                res = ceo_chat_llm.invoke(context)
                reply = get_clean_text(res.content)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 3: ELLE TUTULUR RAPORLAR & ÇIKTILAR (TANGIBLE DELIVERABLES)
# ------------------------------------------------------------------------------
with tab_reports:
    st.markdown("#### 📋 Şirket Çıktıları & Teslimat Belgeleri")
    st.caption("Ajanların ürettiği tüm somut değerler; ham loglar yerine yönetici için yapılandırılmış resmi çıktılar:")

    d = st.session_state.current_deliverables
    col_rep1, col_rep2 = st.columns(2)
    
    with col_rep1:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#828FFF; margin:0 0 6px 0; font-size:14px;">🔬 1. Stratejik Pazar Analiz Raporu</h4>
            <span class="badge-cyan">Departman: Araştırma & İstihbarat</span>
        </div>
        """, unsafe_allow_html=True)
        if d.get("research_summary"):
            st.markdown(f"**Yönetici Özeti:**\n\n{d['research_summary']}")
            st.download_button(
                label="📥 Pazar Raporunu İndir (.md)",
                data=f"# Stratejik Pazar Raporu\n\n**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n**Proje:** {st.session_state.active_thread_id}\n\n## Bulgular\n{d['research_summary']}",
                file_name=f"pazar_raporu_{st.session_state.active_thread_id}.md",
                mime="text/markdown",
                use_container_width=True
            )
        else:
            st.info("Bu proje için henüz pazar araştırması tamamlanmadı.")

    with col_rep2:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#FBBF24; margin:0 0 6px 0; font-size:14px;">🛡️ 2. Bütçe & Denetim Tahsis Belgesi</h4>
            <span class="badge-gold">Departman: Kalite & Finans Denetimi</span>
        </div>
        """, unsafe_allow_html=True)
        if d.get("allocated_budget"):
            st.markdown(f"""
            - **Tahsis Edilen Bütçe :** <span style="font-size:18px; color:#34D399; font-weight:600;">{d['allocated_budget']:,.2f} TL</span>
            - **Finans Bütçe Kodu  :** `BGT-8842`
            - **Denetim Onayı      :** {'✅ ONAYLANDI' if d.get('is_audit_passed') else '⏳ Beklemede'}
            """, unsafe_allow_html=True)
            st.download_button(
                label="📥 Bütçe Belgesini İndir (.txt)",
                data=f"TC / KURUMSAL BÜTÇE TAHSİS BELGESİ\nProje: {st.session_state.active_thread_id}\nTutar: {d['allocated_budget']} TL\nDurum: ONAYLANDI\nKod: BGT-8842",
                file_name=f"butce_sertifikasi_{st.session_state.active_thread_id}.txt",
                use_container_width=True
            )
        else:
            st.info("Bütçe tahsisi henüz onaylanmadı.")

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="report-card">
        <h4 style="color:#34D399; margin:0 0 6px 0; font-size:14px;">💻 3. Kurumsal Yazılım Modülü & Kaynak Kodu</h4>
        <span class="badge-green">Departman: Yazılım & Mühendislik Mimarisi</span>
    </div>
    """, unsafe_allow_html=True)
    
    if d.get("code_deliverable"):
        st.code(d["code_deliverable"], language="python", line_numbers=True)
        st.download_button(
            label="📥 Üretim Kodunu İndir (.py)",
            data=d["code_deliverable"],
            file_name=f"mikroservis_{st.session_state.active_thread_id}.py",
            mime="text/x-python",
            use_container_width=True
        )
    else:
        st.info("Yazılım mimarisi henüz kod üretmedi.")

    # GELİŞMİŞ: PDF Whitepaper İndirme (Expander)
    with st.expander("⚙️ Gelişmiş: Kurumsal Mimari Whitepaper (PDF Rapor)", expanded=False):
        try:
            from pdf_olusturucu import generate_enterprise_documentation_pdf
            pdf_bytes_main = generate_enterprise_documentation_pdf()
            st.download_button(
                label="📥 Tüm Sistem Dokümantasyonunu PDF Olarak İndir (.pdf)",
                data=pdf_bytes_main,
                file_name="Otonom_Ajan_Sirketi_Mimari_Whitepaper.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF motoru: {str(e)[:40]}")

# ------------------------------------------------------------------------------
# TAB 4: VERİTABANI & GEÇMİŞ DENETİMİ (SQLITE VISUALIZER)
# ------------------------------------------------------------------------------
with tab_database:
    st.markdown("#### 🗄️ Kurumsal Kalıcılık & SQLite Veritabanı")
    st.caption("Veritabanı tablolarına kod yazmadan doğrudan erişin. Tüm geçmiş proje oturumları ve adım adım durumlar:")

    db_stats = get_database_statistics()
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1: st.metric("Toplam Kayıtlı Proje", f"{db_stats['total_threads']} Adet")
    with col_stat2: st.metric("Kayıtlı Checkpoint", f"{db_stats['total_checkpoints']} Adım")
    with col_stat3: st.metric("Veritabanı Boyutu", f"{db_stats['db_size_kb']} KB")
    with col_stat4: st.metric("Kalıcılık Motoru", "SQLite (SqliteSaver)")

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    if all_threads:
        threads_summary = []
        for tid in all_threads:
            step_count = get_thread_checkpoint_count(tid)
            cfg = {"configurable": {"thread_id": tid}}
            snap = sirket_motoru.app.get_state(cfg)
            has_res = "Evet" if snap and snap.values.get("research_summary") else "Hayır"
            has_code = "Evet" if snap and snap.values.get("code_deliverable") else "Hayır"
            budget = f"{snap.values.get('allocated_budget', 0):,.0f} TL" if snap and snap.values.get("allocated_budget") else "-"
            status = "Tamamlandı" if snap and snap.values.get("is_audit_passed") else ("Onay Bekliyor" if (snap and snap.next) else "Başlatıldı")
            threads_summary.append({
                "Proje ID (Thread)": tid,
                "Durum": status,
                "Araştırma": has_res,
                "Yazılım Kodu": has_code,
                "Tahsis Bütçe": budget,
                "Checkpoint": step_count
            })
        st.dataframe(pd.DataFrame(threads_summary), use_container_width=True, hide_index=True)

    # GELİŞMİŞ: Checkpoint Time-Travel Trail (Expander)
    with st.expander("⚙️ Gelişmiş: Adım Adım Zaman Çizelgesi (Time-Travel Trail)", expanded=False):
        try:
            cfg = {"configurable": {"thread_id": st.session_state.active_thread_id}}
            history = list(sirket_motoru.app.get_state_history(cfg))
            if history:
                history_rows = []
                for i, snap in enumerate(history):
                    src = snap.metadata.get("source", "user") if snap.metadata else "-"
                    step = snap.metadata.get("step", i) if snap.metadata else i
                    history_rows.append({
                        "Adım No": step,
                        "Kaynak": src,
                        "Bekleyen Düğüm": str(snap.next) if snap.next else "Bitiş (END)",
                        "Checkpoint ID": snap.config["configurable"].get("checkpoint_id", "")[:12] + "..."
                    })
                st.dataframe(pd.DataFrame(history_rows), use_container_width=True, hide_index=True)
            else:
                st.info("Bu proje için henüz checkpoint geçmişi bulunmuyor.")
        except Exception as e:
            st.warning(f"Zaman çizelgesi okunurken bilgi: {str(e)[:60]}")

# ------------------------------------------------------------------------------
# TAB 5: DEPARTMAN MATRİSİ & ŞİRKET RADARI
# ------------------------------------------------------------------------------
with tab_radar:
    st.markdown("#### 🏢 Şirket Organizasyon Şeması & Departman Görevleri")
    st.caption("Otonom Holding bünyesindeki departmanların mimari görev dağılımı ve yetki seviyeleri:")

    col_org1, col_org2 = st.columns(2)
    with col_org1:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#FBBF24; margin:0 0 6px 0; font-size:14px;">👑 1. CEO & Executive Board</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                <b>Rol:</b> Baş Orkestratör & Strateji Belirleyici<br>
                <b>Yetki:</b> Şirket hedeflerini inceler, Pydantic şemasıyla bir sonraki departmanı seçer veya projeyi sonlandırır.<br>
                <b>Teknoloji:</b> Structured Output (CEORouteDecision)
            </p>
        </div>
        <div class="report-card">
            <h4 style="color:#828FFF; margin:0 0 6px 0; font-size:14px;">🔬 2. Araştırma ve İstihbarat Departmanı</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                <b>Rol:</b> Pazar ve Rekabet Analisti<br>
                <b>Araç:</b> <code>query_market_intelligence</code><br>
                <b>Görev:</b> Sektör trendlerini, müşteri taleplerini ve büyüme oranlarını raporlar.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_org2:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#34D399; margin:0 0 6px 0; font-size:14px;">💻 3. Yazılım & Mühendislik Departmanı</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                <b>Rol:</b> Baş Yazılım Mimarı & Kıdemli Mühendis<br>
                <b>Araç:</b> <code>generate_production_code</code><br>
                <b>Görev:</b> Pazar raporuna uygun kurumsal Python mikroservis kodunu inşa eder.
            </p>
        </div>
        <div class="report-card">
            <h4 style="color:#FB7185; margin:0 0 6px 0; font-size:14px;">🛡️ 4. Kalite Denetim ve Bütçe Departmanı</h4>
            <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                <b>Rol:</b> Finans Direktörü & Güvenlik Denetçisi<br>
                <b>Araç:</b> <code>authorize_project_budget</code><br>
                <b>Kritik Özellik:</b> <b>Human-in-the-Loop</b>. Yönetim Kurulu Başkanı onayı olmadan bütçe bloke edilemez.
            </p>
        </div>
        """, unsafe_allow_html=True)
