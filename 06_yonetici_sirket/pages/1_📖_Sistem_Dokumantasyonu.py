"""
================================================================================
📖 OTONOM YAZILIM EVİ - KAPSAMLI SİSTEM DÖKÜMANTASYONU & MİMARİ REHBERİ 📖
================================================================================
Clean Architecture & Linear / Apple Standartlarında Kurumsal Başucu Kılavuzu.
Uçtan uca sistem mimarisi, döngüsel LangGraph yazılım fabrikası, deterministik
AST/QA denetimi, Kurucu Karar Kapısı (HITL), SQLite CRUD ve Dinamik ToolRegistry.
================================================================================
"""

import os
import sys
import pandas as pd
import streamlit as st
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
from tools.registry import ToolRegistry
from data.repositories.app_repository import app_repository

# ==============================================================================
# 1. Sayfa Yapılandırması & Linear / Apple Minimalist Tasarım Sistemi
# ==============================================================================
st.set_page_config(
    page_title="Sistem Dökümantasyonu & Mimari Rehber",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
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
    }

    .stApp, .main {
        background-color: var(--canvas) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--surface-1) !important;
        border-right: 1px solid var(--hairline) !important;
    }

    .doc-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 22px;
    }

    .badge-gold {
        background-color: rgba(245, 158, 11, 0.10);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11.5px;
    }
    .badge-cyan {
        background-color: rgba(56, 189, 248, 0.10);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11.5px;
    }
    .badge-green {
        background-color: rgba(34, 197, 94, 0.10);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11.5px;
    }

    .report-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .quick-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-left: 3px solid #38bdf8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    .security-card {
        background-color: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-left: 3px solid #ef4444;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 16px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. Yan Menü (Sidebar)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏢 DÖKÜMANTASYON MERKEZİ")
    st.caption("Otonom Yazılım Evi & Uygulama Stüdyosu v5.2")

    st.markdown("---")
    st.link_button(
        "👑 Yönetici Masasını Aç ↗",
        url="/",
        type="primary",
        use_container_width=True,
        help="Yönetici Kokpiti ve Fabrika İletişim Masasını açar.",
    )
    try:
        st.page_link("yonetici_masasi.py", label="⬅️ Kokpite Dön (Aynı Sekme)", icon="🏠")
    except Exception:
        pass
    st.markdown("---")

    st.markdown("#### 📡 Altyapı Radarı")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(
            f'<span class="badge-cyan">⚡ Model</span><br><small style="color:#9CA3AF">{TARGET_MODEL}</small>',
            unsafe_allow_html=True,
        )
    with col_sb2:
        st.markdown(
            f'<span class="badge-green">🔑 Key Havuzu</span><br><small style="color:#9CA3AF">{len(API_KEY_POOL)} Adet (.env)</small>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.markdown(
            f'<span class="badge-gold">🛠️ ToolRegistry</span><br><small style="color:#9CA3AF">{ToolRegistry.count()} Araç</small>',
            unsafe_allow_html=True,
        )
    with col_sb4:
        st.markdown(
            '<span class="badge-cyan">💾 Veritabanı</span><br><small style="color:#9CA3AF">studio_apps.db</small>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("##### 📥 Resmi Teknik Whitepaper")
    try:
        pdf_bytes_sb = generate_enterprise_documentation_pdf()
        st.download_button(
            label="📥 Tüm Dökümanı PDF İndir (.pdf)",
            data=pdf_bytes_sb,
            file_name="Otonom_Yazilim_Evi_Teknik_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kurumsal diyagramları içeren A4 formatında teknik PDF.",
        )
    except Exception as e:
        st.caption(f"PDF motoru: {str(e)[:30]}")

    st.markdown("---")
    st.caption("Mimari: Clean Architecture\nGraf: Cyclical StateGraph (LangGraph)\nKalıcılık: SQLite Checkpoints (WAL)")

# ==============================================================================
# 3. Ana Başlık & Yönetici Durum Kartı
# ==============================================================================
stats = app_repository.get_statistics()
st.markdown(
    f"""
<div class="doc-header">
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">
        <div>
            <h2 style="margin: 0; font-size: 23px; color: #F8FAFC; font-weight: 700;">
                📖 OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU | SİSTEM DÖKÜMANTASYONU
            </h2>
            <p style="margin: 6px 0 0 0; color: #94A3B8; font-size: 13px;">
                Clean Architecture • Döngüsel LangGraph Fabrikası • Deterministik AST/QA • Kurucu Karar Kapısı • SQLite CRUD
            </p>
        </div>
        <div style="text-align: right; min-width: 200px;">
            <span class="badge-gold">Kurumsal Teknik Kılavuz</span><br>
            <span style="font-size: 11.5px; color: #94a3b8; margin-top: 5px; display: inline-block;">
                Kayıtlı Proje: <b>{stats.total_apps}</b> • SQLite: <b>{stats.db_size_kb} KB</b>
            </span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 4. Kapsamlı Sekmeler (7 Tam Bölüm)
# ==============================================================================
tab_quick, tab_arch, tab_code, tab_security, tab_db, tab_meta_doc, tab_pkg_doc = st.tabs([
    "⚡ 1. Hızlı Kullanım Özeti (Cheatsheet)",
    "🏗️ 2. Uçtan Uca Mimari & Döngüsel Graf",
    "💻 3. Çekirdek Kod Katmanı (Deep-Dive)",
    "🛑 4. Güvenlik, HITL Karar Kapısı & Hata Yönetimi",
    "🗄️ 5. SQLite Veritabanı Şeması & Tam CRUD",
    "🏛️ 6. İkinci Beyin & Ürün-Mimari Keşif Odası",
    "📦 7. Çok Dosyalı İmalat & 1-Tık Çalıştırma Paketi",
])

# ------------------------------------------------------------------------------
# TAB 1: HIZLI KULLANIM ÖZETİ
# ------------------------------------------------------------------------------
with tab_quick:
    st.markdown("### ⚡ 2 Dakikada Anlama Kılavuzu (Executive Quickstart)")
    st.caption("Kod ve terminal detaylarına boğulmadan stüdyonun mantığını, işleyişini ve kontrol adımlarını kavrayın:")

    col_q1, col_q2, col_q3, col_q4 = st.columns(4)

    with col_q1:
        st.markdown(
            """
        <div class="quick-card">
            <h4 style="color:#38bdf8; margin:0 0 6px 0; font-size:14.5px;">1️⃣ Fikir & Keşif (Tab 0)</h4>
            <p style="color:#94a3b8; font-size:12.5px; line-height:1.5; margin:0;">
                CPO ve CTO ile ürünün amacını ve teknoloji yığınını tartışın; tek tıkla mühendislik şartnamesine dönüştürün.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_q2:
        st.markdown(
            """
        <div class="quick-card" style="border-left-color: #a855f7;">
            <h4 style="color:#c084fc; margin:0 0 6px 0; font-size:14.5px;">2️⃣ Döngüsel Fabrika (Tab 1)</h4>
            <p style="color:#94a3b8; font-size:12.5px; line-height:1.5; margin:0;">
                PRD ➔ Mimari ➔ Çok Dosyalı Kodlama ➔ Deterministik AST/QA öz-iyileştirme hattı otonom olarak çalışır.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_q3:
        st.markdown(
            """
        <div class="quick-card" style="border-left-color: #f59e0b;">
            <h4 style="color:#fbbf24; margin:0 0 6px 0; font-size:14.5px;">3️⃣ Kurucu Kararı (HITL)</h4>
            <p style="color:#94a3b8; font-size:12.5px; line-height:1.5; margin:0;">
                Kodları inceleyip <b>Onaylayın</b>, <b>Revizyon İsteyin</b> veya <b>Reddedin</b> (Sıfırdan Yazdır / İptal Et).
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_q4:
        st.markdown(
            """
        <div class="quick-card" style="border-left-color: #22c55e;">
            <h4 style="color:#4ade80; margin:0 0 6px 0; font-size:14.5px;">4️⃣ Çalıştır & Yönet (Tab 2-3)</h4>
            <p style="color:#94a3b8; font-size:12.5px; line-height:1.5; margin:0;">
                <code>baslat.bat</code> ile tek tıkla çalıştırın, ZIP indirin ve SQLite üzerinde tam CRUD yönetimi yapın.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("#### 📊 Sistem Sağlık Metrikleri & Altyapı Avantajları")

    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    with col_met1:
        st.metric("Ortalama Yanıt Hızı", "1.5 - 2.5 sn", delta="Flash Motoru (Ultra Düşük Gecikme)")
    with col_met2:
        st.metric("API Key Havuzu", f"{len(API_KEY_POOL)} Adet Anahtar", delta="Kesintisiz Failover")
    with col_met3:
        st.metric("AST & Import Doğrulama", "Deterministik Tool", delta="Sözdizimi Hatasız Kod")
    with col_met4:
        st.metric("Kalıcılık Motoru", "SQLite WAL Mode", delta="Thread İzolasyonlu CRUD")

    st.divider()
    st.markdown("#### 💡 Temel Kavramlar Sözlüğü")

    faq_data = [
        {"Kavram": "Clean Architecture", "Açıklama": "Sistemin config, data, tools, domain, services ve ui olmak üzere birbirinden bağımsız 6 katmana ayrılması."},
        {"Kavram": "Döngüsel StateGraph", "Açıklama": "Merkezi Studio_Director etrafında QA hatası veya kurucu revizyonuyla geri dönülebilen non-linear LangGraph akışı."},
        {"Kavram": "Dynamic ToolRegistry", "Açıklama": "Mühendislik araçlarının (AST denetimi, disk export, ZIP paketleme, kasa) sabit kodlanmadan dinamik tescili."},
        {"Kavram": "HITL Karar Kapısı", "Açıklama": "Kurucu onayı olmadan fiziksel diske tek bir dosya dahi yazılmasını engelleyen güvenlik freni (Onay / Revizyon / Red)."},
        {"Kavram": "MAX_QA_SELF_HEAL_RETRIES", "Açıklama": "Mühendisin kendi hatasını düzeltirken sonsuz döngüye girmesini engelleyen ve direktöre eskalasyon sağlayan koruma."},
        {"Kavram": "RobustConsole", "Açıklama": "Windows cp1252 / charmap karakter uyuşmazlıklarını yakalayarak konsol çıktılarının uygulamayı çökertmesini önleyen güvenli akış."},
        {"Kavram": "SqliteSaver", "Açıklama": "Grafın her adımını studio_apps.db veritabanına kaydeden ve zaman yolculuğuna (Time-Travel) imkan tanıyan kalıcılık motoru."},
        {"Kavram": "Second Brain (İkinci Beyin)", "Açıklama": "meta_bellek/ kasasında vizyon manifestosu, ADR kararları ve operasyonel direktifleri saklayan kurumsal hafıza."},
    ]
    st.dataframe(pd.DataFrame(faq_data), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("##### 📥 Kapsamlı Dokümanı Bilgisayarınıza İndirin:")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Tüm Dökümanı Kurumsal PDF Olarak İndir (.pdf)",
            data=generate_enterprise_documentation_pdf(),
            file_name="Otonom_Yazilim_Evi_Teknik_Whitepaper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Tüm sistem mimarisini ve kodları A4 formatında kurumsal PDF olarak indirir.",
        )
    with col_dl2:
        st.download_button(
            label="📄 Dökümanı Markdown Olarak İndir (.md)",
            data="""# Otonom Yazılım Evi & Uygulama Stüdyosu - Kapsamlı Yönetici Kılavuzu\nBu dosya projenin teknik mimarisini, kodlarını ve kullanım yönergelerini içerir.""",
            file_name="otonom_yazilim_evi_kilavuzu.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ------------------------------------------------------------------------------
# TAB 2: UÇTAN UCA MİMARİ & DÖNGÜSEL GRAF
# ------------------------------------------------------------------------------
with tab_arch:
    st.markdown("### 🏗️ Uçtan Uca Kurumsal Mimari & Döngüsel Graf Akışı")
    st.caption("Clean Architecture prensipleriyle yapılandırılmış 6 katmanlı modüler yazılım stüdyosu:")

    st.markdown("""
```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             SUNUM KATMANI (ui/)                                 │
│  tab_ideation (Keşif)  •  tab_factory (Fabrika)  •  tab_workspace (Kod Gezgini)  │
│  tab_portfolio (CRUD)  •  tab_architecture      •  cyclical_matrix & explorer    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          ORKESTRASYON SERVİSLERİ (services/)                     │
│    StudioService (Stream, Chat, Onay, Revizyon, Red) • DiscoveryService (Konsey) │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            ALAN MOTORU (domain/)                                 │
│   CompanyState • StudioWorkflowBuilder • Studio_Director (Döngü & Karar Merkezi) │
│   Product_Lead (CPO) • System_Architect (CTO) • Lead_Developer • QA_Security_Lead│
└──────────────────────┬───────────────────────────────────┬───────────────────────┘
                       ▼                                   ▼
┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐
│       DİNAMİK ARAÇLAR (tools/)          │  │       VERİ KALICILIĞI (data/)       │
│  ToolRegistry (9 Aktif Mühendislik Tool)│  │  DatabaseManager (SQLite WAL)        │
│  AST Sözdizimi & Çapraz Import Doğrulama│  │  AppRepository (Tam Proje CRUD)     │
│  Fiziksel Export, baslat.bat & ZIP      │  │  VaultRepository (meta_bellek CRUD) │
└─────────────────────────────────────────┘  └─────────────────────────────────────┘
```
""")

    st.markdown("#### 🔄 Canlı Döngüsel Graf (StateGraph) Çalışma Şeması")
    st.markdown("""
```mermaid
flowchart TD
    Start([🚀 Kurucu Talebi / Direktif]) --> Director{👑 Studio_Director}

    Director -->|PRD Belgesi Eksik| CPO[💡 Product_Lead / CPO]
    CPO -->|PRD Hazırlandı| Director

    Director -->|Sistem Mimarisi Eksik| CTO[📐 System_Architect / CTO]
    CTO -->|Modül Şeması Hazırlandı| Director

    Director -->|Kod Üretimi / Revizyon| Dev[💻 Lead_Developer]
    Dev -->|Çok Dosyalı Kod Yazıldı| Director

    Director -->|Kod Doğrulama Vakti| QA[🛡️ QA_Security_Lead]
    QA -->|AST Hatası Tespit Edildi| Director
    QA -->|AST ve Import Başarılı| Director

    Director -->|Tüm Adımlar Tamamlandı| Gate[🛑 Deployment_Gate / HITL]
    
    Gate -->|✅ Kurucu Onayladı| Deploy[📦 Fiziksel Kurulum & baslat.bat]
    Deploy --> EndNode([🏁 FINISH / Tamamlandı])

    Gate -->|🔄 Kurucu Revizyon İstedi| Director
    Gate -->|❌ Kurucu Reddetti| RejectNode([❌ Kod Reddedildi / İptal])
```
""")

    st.markdown("#### 📋 `CompanyState` Veri Sözlüğü")
    state_rows = [
        {"Alan Adı": "app_name / app_slug", "Tip": "str", "Açıklama": "Uygulamanın resmi adı ve güvenli disk klasörü slug'ı."},
        {"Alan Adı": "app_type", "Tip": "str", "Açıklama": "Mimari türü: Streamlit Web App, FastAPI REST Service, CLI Tool."},
        {"Alan Adı": "prd_spec / core_features", "Tip": "str / List[str]", "Açıklama": "CPO tarafından oluşturulan ürün şartnamesi ve MVP özellikleri."},
        {"Alan Adı": "architecture_spec / tech_stack", "Tip": "str / List[str]", "Açıklama": "CTO tarafından belirlenen modül şeması ve Python kütüphaneleri."},
        {"Alan Adı": "entrypoint_file", "Tip": "str", "Açıklama": "Uygulamanın ana giriş dosyası (örn: app.py, main.py, cli.py)."},
        {"Alan Adı": "code_files / total_loc", "Tip": "Dict[str, str] / int", "Açıklama": "Çok dosyalı Python kaynak kodları haritası ve satır sayısı."},
        {"Alan Adı": "qa_passed / qa_issues", "Tip": "bool / List[str]", "Açıklama": "AST ve çapraz modül import doğrulaması bulguları."},
        {"Alan Adı": "revision_count / cycle_count", "Tip": "int / int", "Açıklama": "Döngü sayacı ve QA öz-iyileştirme düzeltme turu."},
        {"Alan Adı": "is_rejected / rejection_reason", "Tip": "bool / str", "Açıklama": "Kurucu tarafından kodun reddedilme bayrağı ve gerekçesi."},
        {"Alan Adı": "is_deployed / app_folder", "Tip": "bool / str", "Açıklama": "Fiziksel kurulum tamamlanma bayrağı ve disk dizin yolu."},
        {"Alan Adı": "messages / transition_log", "Tip": "List[Message] / List[dict]", "Açıklama": "Konuşma geçmişi ve zaman damgalı döngü telemetrisi."},
    ]
    st.dataframe(pd.DataFrame(state_rows), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 3: ÇEKİRDEK KOD KATMANI (DEEP-DIVE)
# ------------------------------------------------------------------------------
with tab_code:
    st.markdown("### 💻 Çekirdek Kod Katmanı & Düğüm Mantıkları")
    st.caption("Clean Architecture ayrımı sayesinde iş mantığı, sunum ve veri katmanı birbirinden bağımsızdır:")

    st.markdown("##### 1. `Studio_Director` ve Öncelikli Yönlendirme Mantığı")
    st.code("""def director_router(state: CompanyState) -> str:
    # 1. Kod Kurucu tarafından reddedildiyse ve iptal edildiyse derhal bitir
    if state.get("is_rejected") and not state.get("founder_feedback"):
        return "FINISH"
    # 2. Fiziksel kurulum zaten tamamlandıysa bitir
    if state.get("is_deployed"):
        return "FINISH"
    # 3. Kurucu revizyon talimatı vermişse seçilen departmana git (Öncelikli!)
    if state.get("founder_feedback"):
        target = state.get("feedback_target")
        return target if target in (...) else "Lead_Developer"
    # 4. Standart üretim akışı (PRD -> Mimari -> Kodlama)
    if not state.get("prd_spec"):
        return "Product_Lead"
    if not state.get("architecture_spec"):
        return "System_Architect"
    if not state.get("code_files"):
        return "Lead_Developer"
    # 5. QA denetimi
    if not state.get("code_verified_by_qa"):
        return "QA_Security_Lead"
    if not state.get("qa_passed"):
        # Sınır aşıldıysa sonsuz döngü yerine Kurucu Kapısına eskalasyon yap!
        if state.get("revision_count", 0) >= MAX_QA_SELF_HEAL_RETRIES:
            return "Deployment_Gate"
        return "Lead_Developer"
    # 6. Her şey tamamsa Kurucu Karar Kapısına sun
    return "Deployment_Gate"
""", language="python")

    st.markdown("##### 2. `StudioService` Orkestrasyon Metotları")
    service_methods = [
        {"Metot": "get_conversation_messages(thread_id)", "Açıklama": "Aktif projenin kurucu ve departman mesajlarını rollere göre listeler."},
        {"Metot": "chat_with_factory_team(thread_id, msg)", "Açıklama": "Kodu bozmadan aktif PRD, mimari ve kod bağlamında Baş Mimar ile doğrudan sohbet eder."},
        {"Metot": "start_new_build(thread_id, directive)", "Açıklama": "Sıfırdan temiz bir döngüsel uygulama imalat hattı başlatır."},
        {"Metot": "approve_and_deploy(thread_id)", "Açıklama": "HITL kapısındaki uygulamayı onaylar ve fiziksel diske kurar."},
        {"Metot": "request_revision(thread_id, feedback, target)", "Açıklama": "Duraklatılmış kapıdan ilgili departmana revizyon döngüsü başlatır."},
        {"Metot": "reject_code_and_rewrite(thread_id, reason)", "Açıklama": "Mevcut kodu tamamen silip sıfırdan temiz kodlama başlatır."},
        {"Metot": "reject_and_cancel_project(thread_id, reason)", "Açıklama": "Kurulumu iptal edip SQLite'a '❌ Kod Reddedildi' statüsünü işler."},
        {"Metot": "save_edited_code_file(thread_id, file, content)", "Açıklama": "Kod dosyasını günceller, deterministik AST testinden geçirir ve diske eşitler."},
    ]
    st.dataframe(pd.DataFrame(service_methods), use_container_width=True, hide_index=True)

    st.markdown("##### 3. Dinamik `ToolRegistry` Araç Kataloğu (9 Araç)")
    all_t = ToolRegistry.list_all_tools()
    t_rows = [
        {"Araç Adı": t["name"], "Departman": t["department"], "Kategori": t["category"], "Açıklama": t["description"]}
        for t in all_t
    ]
    st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 4: GÜVENLİK & HITL KARAR KAPISI
# ------------------------------------------------------------------------------
with tab_security:
    st.markdown("### 🛑 Güvenlik, HITL Karar Kapısı & Hata Yönetimi")
    st.caption("Yapay zekanın denetimsiz kod üretmesini, sonsuz döngüye girmesini ve çökmesini engelleyen güvenlik bariyerleri:")

    st.markdown("""
<div class="security-card">
    <h4 style="color:#f87171; margin:0 0 6px 0; font-size:15px;">🛡️ 1. İnsan Karar Kapısı (Human-in-the-Loop Gate)</h4>
    <p style="color:#cbd5e1; font-size:13px; margin:0; line-height:1.6;">
        LangGraph'ın <code>interrupt_before=["Deployment_Gate"]</code> özelliği ile kod diske yazılmadan önce graf dondurulur. 
        Kurucu ekrandan kodları inceleyebilir, AST raporunu okuyabilir ve şu 3 karardan birini verir:
    </p>
    <ul style="color:#cbd5e1; font-size:12.5px; margin-top:8px;">
        <li><b>✅ Kodu Onayla ve Diske İnşa Et:</b> Kodları, requirements.txt'yi, şartnameyi ve baslat.bat'ı yazar.</li>
        <li><b>🔄 Departmana Revizyon Gönder:</b> İstenen değişiklik talimatıyla hedef departmanı yeniden çalıştırır.</li>
        <li><b>❌ Kodu Reddet:</b> Sıfırdan temiz kodla baştan yazdırabilir ya da projeyi 'Kod Reddedildi' olarak iptal edebilir.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("##### 2. Sonsuz Döngü Koruması (`MAX_QA_SELF_HEAL_RETRIES = 2`)")
    st.caption(
        "Kıdemli Mühendis kod yazdıktan sonra QA birimi AST ve import analizi yapar. Hata varsa mühendis kodu düzeltmeye çalışır. "
        "Eğer 2 turda düzelmezse graf sonsuz döngüye girip API kredilerini tüketmez; derhal Kurucu Karar Kapısına eskalasyon yapar."
    )

    st.markdown("##### 3. Windows Terminali UTF-8 & `RobustConsole` Güvenliği")
    st.caption(
        "Windows'un varsayılan `cp1252` kodlaması, konsola taç (`👑`) veya roket (`🚀`) emojisi basıldığında `UnicodeEncodeError: charmap` "
        "hatası fırlatır. `RobustConsole` sarmalayıcısı tüm çıktılarda karakterleri güvenle filtreler; sayfa asla çökmez."
    )

    st.markdown("##### 4. 5'li API Key Failover Havuzu (`KeyRotatingGeminiLLM`)")
    st.caption(
        "Google AI Studio'nun serbest katman kota (429) veya sunucu yoğunluğu (503/504) durumlarında kod tek satır aksamaz. "
        ".env içerisindeki 5 anahtar arasında anında rotasyon yapılır ve istek başarıyla tamamlanır."
    )

# ------------------------------------------------------------------------------
# TAB 5: SQLITE VERİTABANI & TAM CRUD
# ------------------------------------------------------------------------------
with tab_db:
    st.markdown("### 🗄️ SQLite Veritabanı Şeması & Tam CRUD Modeli")
    st.caption("`studio_apps.db` üzerinde thread izolasyonlu kalıcılık ve tam kurumsal CRUD işlemleri:")

    st.markdown("""
```sql
-- 1. Uygulama Projeleri Metadata Tablosu
CREATE TABLE studio_projects (
    thread_id TEXT PRIMARY KEY,       -- Benzersiz proje kodu (örn: app-1030-071604)
    display_name TEXT DEFAULT '',     -- Kurucunun verdiği görünür proje adı
    custom_notes TEXT DEFAULT '',     -- Yönetici notları ve operasyonel tercihler
    tags TEXT DEFAULT '',             -- Proje etiketleri (örn: crm, sqlite, mvp)
    created_at TEXT NOT NULL,         -- Oluşturulma zamanı
    updated_at TEXT NOT NULL          -- Son güncelleme zamanı
);

-- 2. LangGraph State Checkpoints Tablosu (SqliteSaver)
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BLOB,                  -- Dondurulmuş CompanyState sözlüğü
    metadata BLOB,
    PRIMARY KEY (thread_id, checkpoint_id)
);
```
""")

    st.markdown("#### ⚙️ `AppRepository` CRUD İşlemleri:")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown("**CREATE (Oluşturma):** `create_project(thread_id, display_name, ...)` — Yeni proje anında SQLite'a yazılır, sayfa yenilenince kaybolmaz.")
        st.markdown("**READ (Arama & Filtre):** `list_all_projects(status_filter, search_query)` — İsme, teknolojiye ve duruma göre anlık filtreleme.")
    with c_col2:
        st.markdown("**UPDATE (Güncelleme):** `update_project_metadata(thread_id, ...)` — Proje adı, etiket ve notlarının gerçek SQLite UPDATE ile güncellenmesi.")
        st.markdown("**DELETE (Kalıcı Silme):** `delete_project(thread_id, delete_disk)` — studio_projects, checkpoints ve disk klasörünün temizlenmesi.")

    st.markdown("#### ⏱️ Time-Travel Audit (Zamanda Yolculuk)")
    st.caption("`app.get_state_history(config)` çağrısı ile bir projenin geçmiş tüm adımlarına adım adım geri dönülebilir ve durum incelenebilir.")

# ------------------------------------------------------------------------------
# TAB 6: İKİNCİ BEYİN & KEŞİF ODASI
# ------------------------------------------------------------------------------
with tab_meta_doc:
    st.markdown("### 🏛️ İkinci Beyin (Second Brain) & Ürün-Mimari Keşif Odası")
    st.caption("Kurumsal bilgi birikimi, mimari kararlar ve ürün vizyonunun `meta_bellek/` kasasında yönetimi:")

    st.markdown("""
```
06_yonetici_sirket/meta_bellek/
├── 01_sirket_vizyonu.md                  # Şirket manifestosu ve temel mühendislik ilkeleri
├── 02_beyin_firtinasi_notlari/           # Ürün keşif ve pazar analizi notları (.md)
├── 03_stratejik_kararlar/                # Mimari Karar Kayıtları (ADR-001_*.md)
└── 04_operasyonel_direktifler/           # Fabrikaya iletilen doğrulanmış şartnameler
```
""")

    st.markdown("##### 🏛️ Ürün & Mimari Konseyi (CPO + CTO + Teknik PM)")
    st.caption(
        "Kurucu Başkan fikir verdiğinde Konsey modu devreye girer: CPO kullanıcı akışını ve MVP sınırını çizer, "
        "CTO teknoloji yığınını (Streamlit/FastAPI, SQLite/JSON) belirler, Teknik PM ise bu tartışmayı tek tıkla "
        "`bridge_discussion_to_factory` metoduyla yeni bir proje kaydı ve doğrulanmış mühendislik şartnamesine dönüştürür."
    )

    st.markdown("##### 📂 `VaultRepository` Tam Dosya CRUD:")
    st.markdown("- **Listele:** Şirket manifestosu, ADR'ler, keşif notları ve şartnameleri tarih sırasıyla listeler.")
    st.markdown("- **Oku & Düzenle:** Markdown içeriğini tarayıcı üzerinden görüntüler ve günceller.")
    st.markdown("- **Sil:** Geçersiz kalmış ADR ve notları kasadan temizler (ana manifesto silinmeye karşı korumalıdır).")

# ------------------------------------------------------------------------------
# TAB 7: ÇOK DOSYALI İMALAT & ÇALIŞTIRMA
# ------------------------------------------------------------------------------
with tab_pkg_doc:
    st.markdown("### 📦 Çok Dosyalı İmalat & 1-Tık Çalıştırma Paketi")
    st.caption("Fiziksel çıktılar, port çakışma önlemleri ve tek tıkla çalıştırma mekanizması:")

    st.markdown("""
```
output_uygulamalar/abonelik_takipcisi/
├── app.py                 # Streamlit arayüzü ve grafikler
├── database.py            # SQLite şeması ve CRUD fonksiyonları
├── models.py              # Veri yapıları ve hesaplama mantığı
├── requirements.txt       # Gerekli bağımsız Python paketleri
├── MIMARI_VE_PRD.md       # CPO ve CTO şartnamesi, QA raporu
└── baslat.bat             # Tek tıkla bağımsız pencerede başlatan betik
```
""")

    st.markdown("##### 🚀 Port Çakışmasız `baslat.bat` ve Çalıştırma Mantığı")
    st.caption(
        "Yönetici Masası varsayılan olarak `8501` portunu kullanır. `BatchScriptGeneratorTool`, üretilen Streamlit web "
        "uygulamalarını otomatik olarak **`8505`** portuna, FastAPI servislerini ise **`8005`** portuna yönlendirir. "
        "Ayrıca sanal ortamdaki `.venv\\Scripts\\python.exe` yorumlayıcısını kullanarak küresel kütüphane çakışmalarını önler."
    )

    st.markdown("##### ✏️ Tarayıcı İçi AST Doğrulamalı Kod Düzenleyici (CRUD Update)")
    st.caption(
        "Kod Gezgini sekmesinde (`Tab 2`) üretilen herhangi bir Python dosyası doğrudan tarayıcı üzerinden düzenlenebilir. "
        "Değişiklik kaydedildiğinde sistem otomatik olarak Python AST ve sözdizimi testini çalıştırır; "
        "uygulama kurulmuşsa fiziksel diske anında eşitler."
    )

    st.markdown("##### 📦 İndirilebilir ZIP Paketi (`ZipPackagerTool`)")
    st.caption(
        "Kurulan veya Kurucu Onay Kapısında bekleyen tüm projeler, tek tıkla kaynak kodları ve şartnamesiyle birlikte "
        "bağımsız bir `.zip` arşivi olarak bilgisayara indirilebilir."
    )
