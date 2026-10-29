"""
================================================================================
👑 OTONOM AJAN ŞİRKETİ - YÖNETİCİ KOKPİTİ (EXECUTIVE MANAGEMENT DESK) 👑
================================================================================
Yönetim Kurulu Başkanı / Karar Verici için tasarlanmış kurumsal kontrol arayüzü.
Doğrudan ana ajanla (CEO) konuşma, elle tutulur raporları inceleme,
SQLite veritabanını görselleştirme ve Human-in-the-Loop bütçe onayı verme masası.
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
from meta_katman.kod_araclari import (
    WorkspaceSecurity,
    CodeSnapshotManager,
    CodeQualityEngine,
    CodeInspector
)
from meta_katman.otonom_kodlayici import (
    plan_and_generate_code_patch,
    execute_approved_code_patch,
    rollback_code_change,
    discover_relevant_files_for_task,
    plan_and_generate_codebase_patch,
    execute_approved_codebase_patch,
    rollback_codebase_batch
)

# ==============================================================================
# 1. Sayfa Yapılandırması ve Kurumsal Tasarım (Executive Theme)
# ==============================================================================
st.set_page_config(
    page_title="Otonom Ajan Şirketi | Yönetici Masası",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kurumsal Yönetici Stili (CSS)
st.markdown("""
<style>
    /* Ana Font & Arka Plan */
    .main {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    
    /* Üst Başlık Kartı */
    .executive-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* Rozetler ve Metrikler */
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
    .badge-green {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid #10B981;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    
    /* Human-in-the-Loop Onay Kutusu */
    .hitl-box {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(185, 28, 28, 0.2) 100%);
        border: 2px solid #EF4444;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.25);
    }
    
    /* Rapor Kartları */
    .report-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Sekme Başlıkları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #1E293B;
        border-radius: 8px 8px 0 0;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border-bottom: 2px solid #38BDF8 !important;
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

if "swe_active_patch" not in st.session_state:
    st.session_state.swe_active_patch = None

if "swe_codebase_patch" not in st.session_state:
    st.session_state.swe_codebase_patch = None

if "swe_last_backup" not in st.session_state:
    st.session_state.swe_last_backup = None

if "swe_last_batch_id" not in st.session_state:
    st.session_state.swe_last_batch_id = None

# ==============================================================================
# 4. Yan Menü (Sidebar) - Şirket Paneli & Ajan Radarı
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 OTONOM AJAN HOLDİNG")
    st.caption("Executive Management Cockpit v3.0")
    
    # Birebir aynı zengin formatta ayrı web-browser sekmesinde dökümantasyonu ve başucu kitabını açma butonları
    st.link_button(
        "📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗",
        url="/LangGraph_Basucu_Kitabi",
        type="primary",
        use_container_width=True,
        help="12 bölümlük karanlık temalı interaktif LangGraph & Otonom Ajan Mimarisi Başucu Kitabını (ve PDF indirme ekranını) ayrı bir tarayıcı sekmesinde sunucusuz açar."
    )
    st.link_button(
        "📖 Dökümantasyonu Ayrı Sekmede Aç ↗",
        url="/Sistem_Dokumantasyonu",
        use_container_width=True,
        help="Sistem mimarisini, kod katmanlarını ve hızlı kullanım rehberini ayrı bir web sekmesinde açar."
    )
    
    st.markdown("---")
    st.markdown("#### 📡 Ajan & Altyapı Radarı")
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f'<span class="badge-gold">👑 CEO Ajanı</span><br><small style="color:#94A3B8">Hazır & Aktif</small>', unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f'<span class="badge-cyan">⚡ Model</span><br><small style="color:#94A3B8">{TARGET_MODEL}</small>', unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.markdown(f'<span class="badge-green">🔑 Key Havuzu</span><br><small style="color:#94A3B8">{len(API_KEY_POOL)} Adet (.env)</small>', unsafe_allow_html=True)
    with col_sb4:
        st.markdown(f'<span class="badge-cyan">💾 SQLite DB</span><br><small style="color:#94A3B8">enterprise.db</small>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏛️ Meta-Düzlem & İkinci Beyin")
    meta_doc_count = len(list_vault_documents())
    st.markdown(f'<span class="badge-gold">📚 Yaşayan Belge: {meta_doc_count} Adet</span>', unsafe_allow_html=True)
    st.caption("🤝 Co-Founder • ⚡ The Skeptic • 📜 Chief of Staff")

    st.markdown("---")
    st.markdown("#### 📂 Proje Oturumu (Thread ID)")
    
    # Mevcut projeleri seç veya yeni başlat
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
            # Veritabanından bu thread'in durumunu çek
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
                
                # Graf askıda mı kalmış?
                st.session_state.waiting_for_hitl = bool(snap.next and "Audit_Approval_Dept" in snap.next)
            st.rerun()

    st.markdown("---")
    st.markdown("#### ⚡ Hızlı Yönetici Direktifleri")
    st.caption("Tek tıkla CEO ajanı için proje başlatın:")
    
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
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 26px; color: #F8FAFC;">👑 OTONOM AJAN ŞİRKETİ | YÖNETİCİ KOKPİTİ</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 14px;">
                Yönetim Kurulu Başkanı Çalışma Masası • CEO Orkestrasyonu • SQLite Veritabanı • Canlı İnsan Onayı (HITL)
            </p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 12px; color: #94A3B8;">Aktif Proje Oturumu</span><br>
            <span class="badge-gold" style="font-size: 14px;">🏷️ {st.session_state.active_thread_id}</span>
            <div style="margin-top: 8px; display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap;">
                <a href="/LangGraph_Basucu_Kitabi" target="_blank" style="display:inline-block; background: linear-gradient(135deg, #10B981 0%, #059669 100%); color:#042F2E; text-decoration:none; font-weight:700; padding:6px 14px; border-radius:6px; font-size:12px; box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);">
                    📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗
                </a>
                <a href="/Sistem_Dokumantasyonu" target="_blank" style="display:inline-block; background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%); color:#FFFFFF; text-decoration:none; font-weight:600; padding:6px 14px; border-radius:6px; font-size:12px; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);">
                    📖 Kapsamlı Mimari Dokümanı (Yeni Sekme) ↗
                </a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. Ana Sekmeler (Executive Cockpit Tabs)
# ==============================================================================
tab_meta, tab_swe, tab_chat, tab_reports, tab_database, tab_radar = st.tabs([
    "🏛️ 0. Kurucular Odası & İkinci Beyin (Meta-Düzlem)",
    "🛠️ 1. Otonom Kodlayıcı & SWE-Agent Studio",
    "💬 2. CEO İletişim & Operasyon Masası",
    "📋 3. Elle Tutulur Raporlar & Çıktılar",
    "🗄️ 4. Veritabanı & Geçmiş Denetimi",
    "🏢 5. Departman Matrisi & Şirket Radarı"
])

# ------------------------------------------------------------------------------
# TAB 0: KURUCULAR ODASI & İKİNCİ BEYİN (META-DÜZLEM & STRATEJİ MASASI)
# ------------------------------------------------------------------------------
with tab_meta:
    st.markdown("#### 🏛️ Kurucular Odası & İkinci Beyin (Meta-Strateji Masası)")
    st.caption(
        "Operasyonel kod ve görev karmaşasından bağımsız olarak; yapay zeka kurucu ortağınızla şirket yapısını, "
        "vizyonu, radikal pivotları ve şirket dışındaki serbest konuları konuşun. Tartışılanları tek tıkla "
        "kalıcı İkinci Beyin (Second Brain) kasasında arşivleyin veya operasyonel CEO'ya direktif olarak iletin."
    )

    # 1. Meta-Ajan Kadrosu ve Durum Rozetleri
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown('<span class="badge-gold">🤝 AI Co-Founder</span><br><small style="color:#94A3B8">Vizyon & Stratejik Düşünce</small>', unsafe_allow_html=True)
    with col_m2:
        st.markdown('<span class="badge-cyan">⚡ The Skeptic</span><br><small style="color:#94A3B8">Şeytanın Avukatı / Red Team</small>', unsafe_allow_html=True)
    with col_m3:
        st.markdown('<span class="badge-green">📜 Chief of Staff</span><br><small style="color:#94A3B8">Hafıza & ADR Muhafızı</small>', unsafe_allow_html=True)
    with col_m4:
        all_vault_docs = list_vault_documents()
        st.markdown(f'<span class="badge-gold">📚 Bilgi Kasası</span><br><small style="color:#94A3B8">{len(all_vault_docs)} Yaşayan Belge</small>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 2. Çalışma Modu Seçimi
    meta_mode = st.radio(
        "🎯 Masadaki Görüşme Modu:",
        [
            "🤝 Co-Founder ile Serbest Sohbet (Vizyon, Felsefe, Şirket Yapısı & Dış Dünya)",
            "⚡ Şeytanın Avukatı ile Stres Testi (Kör Noktalar, Maliyet Tuzakları, Batış Riskleri)",
            "🏛️ Kurucular Konseyi (Yuvarlak Masa: Co-Founder + Skeptic Çarpışması & Sentez)"
        ],
        horizontal=True
    )

    # 3. Sohbet Konteyneri
    meta_chat_container = st.container(height=380)
    with meta_chat_container:
        if not st.session_state.meta_chat_history:
            st.info(
                "👋 **Hoş geldiniz Sayın Kurucu ve Başkan!**\n\n"
                "Burası günlük operasyonel kod karmaşasından izole **Kurucular Odası**'dır. "
                "Burada şirketimizin hedeflerini, büyük pazar pivotlarını, eğitim vizyonumuzu veya şirket dışındaki "
                "felsefi/teknolojik her konuyu serbestçe konuşabiliriz.\n\n"
                "💡 **Nasıl kullanılır?** Aşağıdan bir mod seçip fikrinizi yazın. Masadaki Co-Founder ve Şeytanın Avukatı "
                "sizinle tartışmaya hazır!"
            )
        
        for msg in st.session_state.meta_chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                with st.chat_message("user", avatar="👔"):
                    st.write(content)
            elif role == "Co-Founder":
                with st.chat_message("assistant", avatar="🤝"):
                    st.markdown(f"**🤝 [CO-FOUNDER & STRATEJİST]:**\n\n{content}")
            elif role == "Skeptic":
                with st.chat_message("assistant", avatar="⚡"):
                    st.markdown(f"**⚡ [ŞEYTANIN AVUKATI / RED TEAM]:**\n\n{content}")
            elif role == "Scribe":
                with st.chat_message("assistant", avatar="📜"):
                    st.markdown(f"**📜 [CHIEF OF STAFF SENTEZİ & DİREKTİF]:**\n\n{content}")
            else:
                with st.chat_message("assistant", avatar="🏛️"):
                    st.markdown(content)

    # 4. Hızlı Aksiyon ve İkinci Beyin Araç Çubuğu
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    with col_act1:
        if st.button("💡 Beyin Fırtınası Kaydet", use_container_width=True):
            if not st.session_state.meta_chat_history:
                st.warning("Kaydedilecek bir görüşme geçmişi bulunamadı.")
            else:
                with st.spinner("📜 Chief of Staff konuşmayı analiz ediyor ve Markdown kasasına kaydediyor..."):
                    saved_path = save_session_as_brainstorm(st.session_state.meta_chat_history)
                    st.success(f"✅ Beyin fırtınası kaydedildi: `{os.path.basename(saved_path)}`")
    
    with col_act2:
        if st.button("🏛️ Stratejik Karar (ADR) Kaydet", use_container_width=True):
            if not st.session_state.meta_chat_history:
                st.warning("Kaydedilecek bir karar geçmişi bulunamadı.")
            else:
                with st.spinner("📜 Resmi Stratejik Karar Kaydı (ADR) oluşturuluyor..."):
                    saved_path = save_session_as_adr(st.session_state.meta_chat_history)
                    st.success(f"✅ ADR Kaydı oluşturuldu: `{os.path.basename(saved_path)}`")

    with col_act3:
        if st.button("🚀 Operasyona Aktar (CEO'ya Gönder)", use_container_width=True, type="primary"):
            if not st.session_state.meta_chat_history:
                st.warning("Operasyona aktarılacak bir strateji henüz tartışılmadı.")
            else:
                with st.spinner("🎯 Tartışma CEO direktifine dönüştürülüyor..."):
                    bridge_res = bridge_meta_to_operational_directive(st.session_state.meta_chat_history)
                    st.session_state.quick_directive = bridge_res["directive_text"]
                    st.success(f"✅ '{bridge_res['title']}' görevi CEO Masasına aktarıldı! '💬 1. CEO İletişim Masası' sekmesinden hemen çalıştırabilirsiniz.")

    with col_act4:
        if st.button("🧹 Odayı Temizle (Yeni Oturum)", use_container_width=True):
            st.session_state.meta_chat_history = []
            st.rerun()

    # 5. Kullanıcı Giriş Alanı
    meta_input = st.chat_input("Kurucular Odasında tartışılacak fikri, vizyonu veya sorunuzu yazın...", key="meta_chat_input")
    if meta_input:
        st.session_state.meta_chat_history.append({"role": "user", "content": meta_input})
        
        if "Co-Founder ile Serbest" in meta_mode:
            with st.spinner("🤝 Co-Founder vizyonunuzu genişleterek düşünüyor..."):
                reply = chat_with_cofounder(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": reply})
                st.rerun()
        elif "Şeytanın Avukatı" in meta_mode:
            with st.spinner("⚡ Şeytanın Avukatı kör noktaları ve batış risklerini inceliyor..."):
                reply = chat_with_skeptic(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": reply})
                st.rerun()
        else:
            # Kurucular Konseyi (Yuvarlak Masa)
            with st.spinner("🏛️ Kurucular Konseyi toplanıyor (Co-Founder + Skeptic Çarpışması)..."):
                council = run_boardroom_council_debate(meta_input, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": council["cofounder"]})
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": council["skeptic"]})
                st.session_state.meta_chat_history.append({"role": "Scribe", "content": council["scribe_synthesis"]})
                st.rerun()

    # 6. İkinci Beyin Kasası Gezgini (Second Brain Explorer)
    st.markdown("---")
    with st.expander("📚 İkinci Beyin Bilgi Kasası & Yaşayan Notlar (Knowledge Vault Explorer)", expanded=False):
        v_docs = list_vault_documents()
        if not v_docs:
            st.info("Bilgi kasasında henüz belge bulunmuyor.")
        else:
            col_vd1, col_vd2 = st.columns([1, 2])
            with col_vd1:
                st.markdown("##### 📁 Kasadaki Yaşayan Belgeler")
                doc_labels = [f"{d['category']} | {d['name']}" for d in v_docs]
                sel_idx = st.selectbox(
                    "İncelemek istediğiniz belgeyi seçin:",
                    range(len(v_docs)),
                    format_func=lambda i: doc_labels[i],
                    key="vault_doc_selector"
                )
                chosen_doc = v_docs[sel_idx]
                
                st.info(
                    f"**Kategori:** {chosen_doc['category']}\n\n"
                    f"**Dosya Yolu:** `{chosen_doc['rel_path']}`\n\n"
                    f"**Boyut:** {chosen_doc['size_kb']} KB\n\n"
                    f"**Son Güncelleme:** {chosen_doc['modified']}"
                )
            
            with col_vd2:
                st.markdown(f"##### 📄 Belge Önizlemesi: `{chosen_doc['name']}`")
                doc_content = read_document_content(chosen_doc["path"])
                
                if "01_sirket_vizyonu.md" in chosen_doc["name"]:
                    edited_vision = st.text_area("Şirket Vizyonunu Canlı Düzenle:", value=doc_content, height=320)
                    if st.button("💾 Şirket Vizyonunu Güncelle & Kaydet"):
                        if update_company_vision(edited_vision):
                            st.success("✅ Şirket Vizyonu ve Manifestosu güncellendi!")
                            st.rerun()
                else:
                    st.markdown(
                        f"""<div style="background-color:#1E293B; padding:18px; border-radius:10px; border:1px solid #334155; max-height:400px; overflow-y:auto;">
                        {doc_content}
                        </div>""",
                        unsafe_allow_html=True
                    )

# ------------------------------------------------------------------------------
# TAB 1: OTONOM KODLAYICI & SWE-AGENT STUDIO (CODEBASE-WIDE)
# ------------------------------------------------------------------------------
with tab_swe:
    st.markdown("#### 🛠️ Otonom Yazılım Mühendisi & Kod Tabanı Stüdyosu (Codebase-Wide SWE Studio)")
    st.caption(
        "Tek tek dosya seçmenize veya kod bilmenize gerek yok! Projenizde ne değiştirmek istediğinizi doğal dille yazın; "
        "Yapay Zeka Mimarı tüm kod tabanını otonom tarar, ilgili tüm dosyaları tespit eder, AST doğrulamalı kod üretir ve "
        "tek bir tıkla tüm projeye atomik olarak uygular."
    )

    # Üst Güvenlik ve Durum Rozetleri
    col_sw1, col_sw2, col_sw3, col_sw4 = st.columns(4)
    with col_sw1:
        st.markdown('<span class="badge-green">🌐 Kapsam</span><br><small style="color:#94A3B8">Tüm Kod Tabanı (Codebase-Wide)</small>', unsafe_allow_html=True)
    with col_sw2:
        st.markdown('<span class="badge-cyan">🧠 Otonom Tarama</span><br><small style="color:#94A3B8">AI Architect Dosya Keşfi</small>', unsafe_allow_html=True)
    with col_sw3:
        st.markdown('<span class="badge-gold">🧪 AST Denetimi</span><br><small style="color:#94A3B8">0 Sözdizimi Hatası Garantisi</small>', unsafe_allow_html=True)
    with col_sw4:
        backups_count = len(CodeSnapshotManager.list_snapshots())
        st.markdown(f'<span class="badge-green">💾 Toplu Snapshot</span><br><small style="color:#94A3B8">{backups_count} Güvenli Yedek (.bak)</small>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Hızlı Direktif Şablonları (Executive Prompt Chips)
    st.markdown("##### 💡 Hızlı Yönetici Direktifleri (Tıklayıp Doldurun):")
    col_chip1, col_chip2 = st.columns(2)
    with col_chip1:
        if st.button("🎨 'Arayüzü AI Slop renklerinden kurtar, Linear tarzı minimalist CSS yap'", use_container_width=True):
            st.session_state.swe_quick_instruction = "Arayüzdeki AI Slop renkleri (fosforlu cyan, sarı, parlayan kırmızı kutu) sil, Linear.app koyu kömür minimalizmini ve rafine indigo temasını tüm sayfalara uygula."
    with col_chip2:
        if st.button("🛡️ 'Tüm projede güvenlik kontrollerini ve hata yakalamalarını artır'", use_container_width=True):
            st.session_state.swe_quick_instruction = "Tüm kod tabanında hata yakalama (try/except) ve güvenlik sınırlarını güçlendir, eksik tip ipuçlarını tamamla."

    # Direktif Giriş Alanı
    default_text = st.session_state.pop("swe_quick_instruction", "")
    swe_instruction = st.text_area(
        "Şirketinizde veya projenizde ne değiştirmek istiyorsunuz? (Teknik detay bilmeniz gerekmez):",
        value=default_text,
        placeholder="Örnek: Arayüzdeki parlayan AI Slop renklerini kaldır, Linear.app minimalist kömür temasını ve rafine tipografiyi tüm arayüze uygula.",
        height=100,
        help="Siz sadece hedefinizi yazın. Mimar ajan hangi dosyaların etkileneceğini kendisi bulacak ve kodu hazırlayacaktır."
    )

    # Çalıştırma Butonları
    col_btn_run, col_btn_clear = st.columns([3, 1])
    with col_btn_run:
        btn_run_codebase = st.button("🚀 Tüm Projeyi Otonom Tara, Planla & Kodla (Codebase-Wide)", type="primary", use_container_width=True)
    with col_btn_clear:
        if st.button("🧹 Temizle", use_container_width=True):
            st.session_state.swe_codebase_patch = None
            st.session_state.swe_active_patch = None
            st.rerun()

    # İsteğe Bağlı: Manuel Tek Dosya Modu (Gelişmiş)
    with st.expander("⚙️ Gelişmiş: Belirli Bir Dosyaya Cerrahi Müdahale (Opsiyonel)", expanded=False):
        st.caption("Eğer tüm projeyi değil sadece tek bir dosyayı hedeflemek isterseniz buradan seçebilirsiniz:")
        all_proj_files = CodeInspector.list_project_files()
        manual_target_file = st.selectbox("Cerrahi Dosya Seçimi:", options=["Otomatik Tespit (Tavsiye Edilen)"] + all_proj_files)

    if btn_run_codebase:
        if not swe_instruction.strip():
            st.warning("Lütfen gerçekleştirmek istediğiniz hedefi yukarıdaki kutuya yazın.")
        else:
            with st.spinner("🤖 Baş Yazılım Mimarı tüm proje kod tabanını tarıyor, ilgili dosyaları tespit ediyor ve AST doğrulamalı kod üretiyor..."):
                try:
                    specific_list = [manual_target_file] if manual_target_file != "Otomatik Tespit (Tavsiye Edilen)" else None
                    codebase_result = plan_and_generate_codebase_patch(
                        instruction=swe_instruction,
                        specific_files=specific_list
                    )
                    st.session_state.swe_codebase_patch = codebase_result
                    st.rerun()
                except Exception as e:
                    st.error(f"Otonom kodlama hatası: {e}")

    # ==============================================================================
    # ÇOKLU DOSYA DİFF VE HUMAN-IN-THE-LOOP PROJE ONAY PANOSU
    # ==============================================================================
    cb_patch = st.session_state.get("swe_codebase_patch")
    if cb_patch:
        st.markdown("---")
        st.markdown("### 📋 Baş Mimarın Proje Değişiklik Raporu & Onay Masası")

        # Mimari Plan ve Etki Kartı
        col_plan1, col_plan2 = st.columns([2, 1])
        with col_plan1:
            st.info(f"🧠 **Mimari Plan:**\n{cb_patch['architectural_plan']}")
        with col_plan2:
            st.markdown(
                f"""<div style="background-color:#1E293B; padding:16px; border-radius:8px; border:1px solid #334155;">
                <span style="font-size:12px; color:#94A3B8;">Etki Değerlendirmesi</span><br>
                <b style="color:#F59E0B; font-size:14px;">{cb_patch['estimated_impact']}</b><br><br>
                <span style="font-size:12px; color:#94A3B8;">Etkilenen Dosya Sayısı</span><br>
                <b style="color:#38BDF8; font-size:16px;">{cb_patch['total_files']} Adet Proje Dosyası</b>
                </div>""",
                unsafe_allow_html=True
            )

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        st.markdown(f"##### 🎯 Otonom Olarak Belirlenen ve Düzenlenen Dosyalar ({cb_patch['total_files']} Adet):")

        # Her dosya için ayrı bir sekmede Diff göster
        file_patches = cb_patch.get("file_patches", [])
        if file_patches:
            tab_labels = [f"📄 {p['target_file']}" for p in file_patches]
            diff_tabs = st.tabs(tab_labels)

            for i, p in enumerate(file_patches):
                with diff_tabs[i]:
                    if p.get("syntax_valid"):
                        st.success(f"✅ **AST Sözdizimi Testi: GEÇTİ (0 Hata)** | Dosya: `{p['target_file']}`")
                    else:
                        st.error(f"❌ **Sözdizimi Hatası:** {p.get('syntax_error')}")

                    st.markdown(f"**📌 Dosya Özeti:** {p.get('summary', 'Değişiklik yapıldı.')}")

                    diff_str = p.get("diff", "")
                    if diff_str:
                        st.code(diff_str, language="diff")
                    else:
                        st.info("Bu dosyada önerilen değişiklik bulunmuyor.")

        # Toplu Onay ve İcra Butonları
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        col_exec_all, col_reject_all, col_roll_all = st.columns([2, 1, 1])

        with col_exec_all:
            all_valid = cb_patch.get("success", False)
            if st.button("🚀 Tüm Değişiklikleri Projeye Uygula (1-Tıkla Canlıya Al)", type="primary", use_container_width=True, disabled=not all_valid):
                with st.spinner("💾 Toplu zaman damgalı snapshot alınıyor ve tüm dosyalar atomik olarak güncelleniyor..."):
                    try:
                        exec_res = execute_approved_codebase_patch(cb_patch)
                        st.session_state.swe_last_batch_id = exec_res["batch_id"]
                        st.session_state.swe_codebase_patch = None
                        st.success(f"🎉 **PROJE GÜNCELLENDİ!** {len(exec_res['written_files'])} dosya diske yazıldı. Toplu Snapshot ID: `{exec_res['batch_id']}`")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Uygulama hatası: {e}")

        with col_reject_all:
            if st.button("❌ İptal Et / Reddet", use_container_width=True):
                st.session_state.swe_codebase_patch = None
                st.info("Önerilen proje değişikliği iptal edildi.")
                st.rerun()

        with col_roll_all:
            last_batch = st.session_state.get("swe_last_batch_id")
            if st.button("↩️ Son Toplu Değişikliği Geri Al (Rollback)", use_container_width=True, disabled=not last_batch):
                try:
                    restored = rollback_codebase_batch(last_batch)
                    st.success(f"✅ Son toplu değişiklik geri alındı! Eski haline dönen dosyalar: {restored}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Geri alma hatası: {e}")

    # Geçmiş Yedekler Gezgini
    st.markdown("---")
    with st.expander("📂 Otomatik Kod Yedekleri Kasası (.backups/) & Rollback Geçmişi", expanded=False):
        snapshots = CodeSnapshotManager.list_snapshots()
        if not snapshots:
            st.caption("Henüz bir yedek dosyası (.bak) bulunmuyor.")
        else:
            for s in snapshots[:10]:
                col_s1, col_s2 = st.columns([3, 1])
                with col_s1:
                    st.code(f"{s['filename']} ({s['size_kb']} KB) - {s['timestamp']}", language="bash")
                with col_s2:
                    if st.button("Geri Yükle", key=f"btn_res_{s['filename']}"):
                        try:
                            # Dosya adından hedefi çıkar
                            parts = s["filename"].split("___")
                            if len(parts) >= 2:
                                rel_name = parts[1][:-4].replace("__", os.sep)
                            else:
                                rel_name = "_".join(s["filename"].split("_")[2:]).replace(".bak", "")
                            CodeSnapshotManager.restore_snapshot(s["path"], rel_name)
                            st.success(f"✅ '{rel_name}' başarıyla bu yedeğe geri döndürüldü!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Geri yükleme hatası: {e}")

# ------------------------------------------------------------------------------
# TAB 2: CEO İLETİŞİM & CANLI OPERASYON MASASI
# ------------------------------------------------------------------------------
with tab_chat:
    st.markdown("#### 👑 CEO Strateji Masası ile Doğrudan İletişim")
    st.caption("Arka plandaki kod ve terminal karmaşası yerine doğrudan ana ajanınızla (CEO) konuşun, direktif verin veya sorular sorun.")

    # Sohbet Geçmişi Alanı
    chat_container = st.container(height=420)
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Merhaba Sayın Yönetim Kurulu Başkanı! Ben Otonom Şirketinizin CEO'suyum. Pazar araştırması, yazılım mimarisi veya bütçe onay süreçlerini başlatmak için direktifinizi bekliyorum.")
        
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👔"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="👑"):
                    st.write(msg["content"])

    # 🛑 HUMAN-IN-THE-LOOP (HITL) CANLI ONAY KARTI
    if st.session_state.waiting_for_hitl:
        st.markdown("""
        <div class="hitl-box">
            <h3 style="color:#EF4444; margin-top:0;">🛑 YÖNETİCİ ONAYI BEKLENİYOR (HUMAN-IN-THE-LOOP)</h3>
            <p style="color:#FCA5A5; font-size:15px; margin-bottom:12px;">
                Mühendislik ve Araştırma departmanları hazırlıklarını tamamladı. Şirket kasasından 
                <b>250.000 TL</b> bütçe tahsis edilmesi için <b>Yönetim Kurulu Başkanı (Siz)</b> yetkisi ve onayı bekleniyor.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_hitl1, col_hitl2 = st.columns([2, 1])
        with col_hitl1:
            if st.button("✅ 250.000 TL Şirket Bütçesini ONAYLA ve Projeyi Başlat", type="primary", use_container_width=True):
                with st.spinner("Yönetici onayı iletilecek, bütçe bloke edilip şirket projesi teslim ediliyor..."):
                    config = {"configurable": {"thread_id": st.session_state.active_thread_id}}
                    final_state = sirket_motoru.app.invoke(None, config=config)
                    
                    st.session_state.waiting_for_hitl = False
                    st.session_state.current_deliverables = {
                        "research_summary": final_state.get("research_summary"),
                        "code_deliverable": final_state.get("code_deliverable"),
                        "allocated_budget": final_state.get("allocated_budget"),
                        "is_audit_passed": final_state.get("is_audit_passed", False),
                        "ceo_closing": get_clean_text(final_state["messages"][-1].content) if final_state.get("messages") else None
                    }
                    
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
        # Kullanıcı mesajını ekle
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        
        # Karar: Bu bir genel soru mu, yoksa şirket görevi mi?
        is_task = any(w in user_prompt.lower() for w in ["başlat", "proje", "araştır", "kodla", "bütçe", "oluştur", "sistem", "servis"])
        
        config = {"configurable": {"thread_id": st.session_state.active_thread_id}}
        
        if is_task:
            with st.spinner("👑 CEO Yönetim Kurulu Direktifini İnceliyor & Departmanları Seferber Ediyor..."):
                initial_input = {
                    "messages": [HumanMessage(content=user_prompt)],
                    "next_step": "CEO",
                    "research_summary": None,
                    "code_deliverable": None,
                    "allocated_budget": None,
                    "is_audit_passed": False
                }
                
                # 1. Faz Çalıştırılır (Bütçe öncesinde interrupt olur)
                sirket_motoru.app.invoke(initial_input, config=config)
                snapshot = sirket_motoru.app.get_state(config)
                
                # Deliverables güncelle
                st.session_state.current_deliverables["research_summary"] = snapshot.values.get("research_summary")
                st.session_state.current_deliverables["code_deliverable"] = snapshot.values.get("code_deliverable")
                
                if snapshot.next and "Audit_Approval_Dept" in snapshot.next:
                    st.session_state.waiting_for_hitl = True
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "👑 **[CEO]:** Pazar araştırması ve üretim kodu departmanlarımızca hazırlandı! Ancak kurumsal güvenlik politikası gereği **250.000 TL bütçe tahsisi için sizin onayınız bekleniyor.** Lütfen yukarıdaki onay kartını inceleyiniz."
                    })
                else:
                    st.session_state.waiting_for_hitl = False
                    last_msg = snapshot.values["messages"][-1]
                    st.session_state.chat_history.append({"role": "assistant", "content": get_clean_text(last_msg.content)})
                
                st.rerun()
        else:
            # CEO ile doğrudan sohbet (Danışma & Durum Sorma)
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
# TAB 2: ELLE TUTULUR RAPORLAR & ÇIKTILAR (TANGIBLE DELIVERABLES)
# ------------------------------------------------------------------------------
with tab_reports:
    st.markdown("#### 📋 Şirket Çıktıları & Yönetim Kurulu Teslimat Dosyası")
    st.caption("Ajanların ürettiği tüm somut değerler; ham loglar yerine doğrudan yönetici için paketlenmiş resmi dokümanlar:")

    d = st.session_state.current_deliverables
    
    col_rep1, col_rep2 = st.columns(2)
    
    # 1. Pazar Araştırması Raporu
    with col_rep1:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#06B6D4; margin-top:0;">🔬 1. Stratejik Pazar & Sektör Analiz Raporu</h4>
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
            st.info("Bu proje için henüz pazar araştırması tamamlanmadı. CEO'ya direktif vererek başlatabilirsiniz.")

    # 2. Kurumsal Bütçe ve Onay Belgesi
    with col_rep2:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#F59E0B; margin-top:0;">🛡️ 2. Kurumsal Bütçe & Denetim Tahsis Belgesi</h4>
            <span class="badge-gold">Departman: Kalite & Finans Denetimi</span>
        </div>
        """, unsafe_allow_html=True)
        
        if d.get("allocated_budget"):
            st.markdown(f"""
            - **Tahsis Edilen Bütçe :** <span style="font-size:20px; color:#10B981; font-weight:bold;">{d['allocated_budget']:,.2f} TL</span>
            - **Finans Bütçe Kodu  :** `BGT-8842`
            - **Denetim Onayı      :** {'✅ ONAYLANDI' if d.get('is_audit_passed') else '⏳ Beklemede'}
            - **Yetkili Makam      :** Yönetim Kurulu Başkanı (Human-in-the-Loop)
            """, unsafe_allow_html=True)
            
            st.download_button(
                label="📥 Bütçe Tahsis Belgesini İndir (.txt)",
                data=f"TC / KURUMSAL BÜTÇE TAHSİS BELGESİ\nProje: {st.session_state.active_thread_id}\nTutar: {d['allocated_budget']} TL\nDurum: ONAYLANDI\nKod: BGT-8842",
                file_name=f"butce_sertifikasi_{st.session_state.active_thread_id}.txt",
                use_container_width=True
            )
        else:
            st.info("Bütçe tahsisi henüz onaylanmadı veya talep edilmedi.")

    st.markdown("---")
    
    # 3. Mühendislik Çıktısı (Üretim Kodu)
    st.markdown("""
    <div class="report-card">
        <h4 style="color:#10B981; margin-top:0;">💻 3. Kurumsal Yazılım Modülü & Kaynak Kodu</h4>
        <span class="badge-green">Departman: Yazılım & Mühendislik Mimarisi</span>
    </div>
    """, unsafe_allow_html=True)
    
    if d.get("code_deliverable"):
        st.code(d["code_deliverable"], language="python", line_numbers=True)
        st.download_button(
            label="📥 Üretim Kodunu Python Dosyası Olarak İndir (.py)",
            data=d["code_deliverable"],
            file_name=f"mikroservis_{st.session_state.active_thread_id}.py",
            mime="text/x-python",
            use_container_width=True
        )
    else:
        st.info("Yazılım mimarisi henüz kod üretmedi. CEO görevlendirme yaptığında kaynak kod burada görüntülenecektir.")

    st.markdown("---")
    
    # 4. Kurumsal Sistem Mimarisi & Teknik Whitepaper (PDF Rapor)
    st.markdown("""
    <div class="report-card">
        <h4 style="color:#38BDF8; margin-top:0;">📖 4. Kurumsal Sistem Mimarisi & Teknik Whitepaper (Resmi PDF)</h4>
        <span class="badge-gold">Tam Sistem Dökümantasyonu • Kodlar • Şemalar • Kalıcılık</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Tüm otonom şirketin uçtan uca mimarisini, LangGraph akışlarını, SQLite kalıcılık modelini ve güvenlik kurallarını içeren resmi A4 PDF dokümanını tek tıkla indirebilirsiniz:")
    try:
        from pdf_olusturucu import generate_enterprise_documentation_pdf
        pdf_bytes_main = generate_enterprise_documentation_pdf()
        st.download_button(
            label="📥 Tüm Sistem Dökümantasyonunu PDF Olarak İndir (.pdf)",
            data=pdf_bytes_main,
            file_name="Otonom_Ajan_Sirketi_Mimari_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kodları A4 formatında kurumsal PDF olarak indirir."
        )
    except Exception as e:
        st.caption(f"PDF motoru: {str(e)[:40]}")

# ------------------------------------------------------------------------------
# TAB 3: VERİTABANI & GEÇMİŞ DENETİMİ (SQLITE VISUALIZER)
# ------------------------------------------------------------------------------
with tab_database:
    st.markdown("#### 🗄️ Kurumsal Kalıcılık & SQLite Veritabanı Arayüzü")
    st.caption("Veritabanı tablolarına kod yazmadan, doğrudan yönetici gözüyle erişin. Tüm geçmiş proje oturumları, checkpoint'ler ve durumlar:")

    db_stats = get_database_statistics()
    
    # Üst İstatistik Kartları
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Toplam Kayıtlı Proje", f"{db_stats['total_threads']} Adet")
    with col_stat2:
        st.metric("Kayıtlı Checkpoint Adımı", f"{db_stats['total_checkpoints']} Adım")
    with col_stat3:
        st.metric("Veritabanı Dosya Boyutu", f"{db_stats['db_size_kb']} KB")
    with col_stat4:
        st.metric("Veritabanı Motoru", "SQLite (SqliteSaver)")

    st.markdown("---")
    st.markdown("##### 🔍 Kayıtlı Proje Oturumları ve Durumları")
    
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
                "Checkpoint Adımı": step_count
            })
            
        df_threads = pd.DataFrame(threads_summary)
        st.dataframe(df_threads, use_container_width=True, hide_index=True)
    else:
        st.info("enterprise.db henüz boş. İlk projenizi başlatın!")

    # Checkpoint Zaman Çizelgesi
    st.markdown("---")
    st.markdown(f"##### ⏱️ '{st.session_state.active_thread_id}' İçin Adım Adım Zaman Çizelgesi (Time-Travel Trail)")
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
                    "Tetikleyen Kaynak": src,
                    "Sıradaki Bekleyen Düğüm": str(snap.next) if snap.next else "Bitiş (END)",
                    "Checkpoint ID": snap.config["configurable"].get("checkpoint_id", "")[:12] + "..."
                })
            df_hist = pd.DataFrame(history_rows)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Bu proje için henüz checkpoint geçmişi bulunmuyor.")
    except Exception as e:
        st.warning(f"Zaman çizelgesi okunurken bilgi: {str(e)[:60]}")

# ------------------------------------------------------------------------------
# TAB 4: DEPARTMAN MATRİSİ & ŞİRKET RADARI
# ------------------------------------------------------------------------------
with tab_radar:
    st.markdown("#### 🏢 Şirket Organizasyon Şeması & Departman Görevleri")
    st.caption("Otonom Holding bünyesinde çalışan otonom departmanların mimari görev dağılımı ve yetki seviyeleri:")

    col_org1, col_org2 = st.columns(2)
    
    with col_org1:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#F59E0B; margin-top:0;">👑 1. CEO & Executive Board</h4>
            <p style="color:#94A3B8; font-size:14px;">
                <b>Rol:</b> Baş Orkestratör & Strateji Belirleyici<br>
                <b>Yetki:</b> Şirket hedeflerini inceler, Pydantic şemasıyla bir sonraki departmanı seçer veya projeyi sonlandırır.<br>
                <b>Teknoloji:</b> Structured Output (CEORouteDecision)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#06B6D4; margin-top:0;">🔬 2. Araştırma ve İstihbarat Departmanı</h4>
            <p style="color:#94A3B8; font-size:14px;">
                <b>Rol:</b> Pazar ve Rekabet Analisti<br>
                <b>Araç:</b> <code>query_market_intelligence</code><br>
                <b>Görev:</b> Sektör trendlerini, müşteri taleplerini ve büyüme oranlarını raporlar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_org2:
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#10B981; margin-top:0;">💻 3. Yazılım & Mühendislik Departmanı</h4>
            <p style="color:#94A3B8; font-size:14px;">
                <b>Rol:</b> Baş Yazılım Mimarı & Kıdemli Mühendis<br>
                <b>Araç:</b> <code>generate_production_code</code><br>
                <b>Görev:</b> Pazar raporuna uygun, kurumsal ve tip-güvenli Python mikroservis kodunu inşa eder.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="report-card">
            <h4 style="color:#EF4444; margin-top:0;">🛡️ 4. Kalite Denetim ve Bütçe Departmanı</h4>
            <p style="color:#94A3B8; font-size:14px;">
                <b>Rol:</b> Finans Direktörü & Güvenlik Denetçisi<br>
                <b>Araç:</b> <code>authorize_project_budget</code><br>
                <b>Kritik Özellik:</b> <b>Human-in-the-Loop</b>. Yönetim Kurulu Başkanı onayı olmadan tek bir kuruş bloke edilemez.
            </p>
        </div>
        """, unsafe_allow_html=True)
