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

# ==============================================================================
# 4. Yan Menü (Sidebar) - Şirket Paneli & Ajan Radarı
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 OTONOM AJAN HOLDİNG")
    st.caption("Executive Management Cockpit v3.0")
    
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
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. Ana Sekmeler (Executive Cockpit Tabs)
# ==============================================================================
tab_chat, tab_reports, tab_database, tab_radar = st.tabs([
    "💬 1. CEO İletişim & Operasyon Masası",
    "📋 2. Elle Tutulur Raporlar & Çıktılar",
    "🗄️ 3. Veritabanı & Geçmiş Denetimi",
    "🏢 4. Departman Matrisi & Şirket Radarı"
])

# ------------------------------------------------------------------------------
# TAB 1: CEO İLETİŞİM & CANLI OPERASYON MASASI
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
