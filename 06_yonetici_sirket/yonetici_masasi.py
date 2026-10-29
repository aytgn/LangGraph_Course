"""
================================================================================
🏗️ OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU — KURUCU YÖNETİCİ KOKPİTİ 🏗️
================================================================================
Ne uygulaması yapılacağının, hangi amaçla ve hangi altyapı/teknolojilerle
geliştirileceğinin tartışıldığı; ardından döngüsel LangGraph yazılım fabrikası
(PRD -> Sistem Mimarisi -> Çok Dosyalı Kodlama <-> QA/AST Döngüsü -> Kurucu
Onayı/Revizyonu -> Fiziksel Paketleme & Tek Tıkla Çalıştırma) ile gerçek çalışan
uygulamaların üretildiği yönetici masası.
================================================================================
"""

import io
import os
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Çalışma dizini ve modül yolları
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
for _p in (current_dir, root_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

load_dotenv(os.path.join(root_dir, ".env"))

import sirket_motoru
from model_factory import API_KEY_POOL, TARGET_MODEL, get_gemini_llm
from meta_katman.direktif_koprusu import bridge_meta_to_operational_directive
from meta_katman.ikinci_beyin import (
    list_vault_documents,
    read_document_content,
    update_company_vision,
)
from meta_katman.meta_motoru import (
    chat_with_cofounder,
    chat_with_skeptic,
    run_boardroom_council_debate,
    save_session_as_adr,
    save_session_as_brainstorm,
)

# ==============================================================================
# 1. Sayfa Yapılandırması ve Linear/Apple Tasarım Sistemi
# ==============================================================================
st.set_page_config(
    page_title="AI Yazılım Evi & Uygulama Stüdyosu | Yönetici Kokpiti",
    page_icon="🏗️",
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
        --hairline-strong: rgba(255, 255, 255, 0.16);
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --text-tertiary: #6B7280;
        --accent: #5E6AD2;
        --accent-hover: #6E7BF5;
    }

    .stApp, .main {
        background-color: var(--canvas) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
    }

    /* Streamlit varsayılan sayfa listesini gizle */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--surface-1) !important;
        border-right: 1px solid var(--hairline) !important;
    }

    .executive-header {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 18px;
    }

    /* Döngüsel Departman Matrisi Kartları */
    .dept-card {
        background-color: var(--surface-2);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 12px 14px;
        min-height: 108px;
        transition: all 0.2s ease;
    }
    .dept-card:hover {
        border-color: var(--hairline-strong);
    }
    .dept-done {
        border-color: rgba(16, 185, 129, 0.42) !important;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.06) 0%, rgba(16, 185, 129, 0.01) 100%) !important;
    }
    .dept-active {
        border-color: rgba(56, 189, 248, 0.65) !important;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(14, 165, 233, 0.03) 100%) !important;
    }
    .dept-loop {
        border-color: rgba(245, 158, 11, 0.65) !important;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(217, 119, 6, 0.03) 100%) !important;
    }
    .dept-hitl {
        border-color: rgba(244, 63, 94, 0.68) !important;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.13) 0%, rgba(225, 29, 72, 0.04) 100%) !important;
    }
    .dept-idle {
        opacity: 0.68;
    }

    .trail-box {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 10px 14px;
        margin: 8px 0 14px 0;
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .badge-gold {
        background-color: rgba(245, 158, 11, 0.10);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.24);
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }
    .badge-cyan {
        background-color: rgba(94, 106, 210, 0.12);
        color: #93A0FF;
        border: 1px solid rgba(94, 106, 210, 0.28);
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }
    .badge-green {
        background-color: rgba(16, 185, 129, 0.10);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }

    .report-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }

    .hitl-box {
        background: linear-gradient(135deg, rgba(94, 106, 210, 0.10) 0%, rgba(16, 185, 129, 0.05) 100%);
        border: 1px solid rgba(94, 106, 210, 0.45);
        border-left: 4px solid #6E7BF5;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 14px 0;
    }

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
    .stTabs [aria-selected="true"] {
        background-color: var(--surface-2) !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 13px;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border: none !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-hover) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. Veritabanı ve Yardımcı Fonksiyonlar
# ==============================================================================
DB_PATH = sirket_motoru.DB_PATH


def get_clean_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content])
    return str(content)


def get_all_threads() -> list[str]:
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid DESC")
        rows = [r[0] for r in cur.fetchall()]
        conn.close()
        # Sırayı koruyarak tekilleştir
        seen = set()
        unique_threads = []
        for t in rows:
            if t not in seen:
                seen.add(t)
                unique_threads.append(t)
        return unique_threads
    except Exception:
        return []


def get_thread_checkpoint_count(thread_id: str) -> int:
    if not os.path.exists(DB_PATH):
        return 0
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cnt = cur.fetchone()[0]
        conn.close()
        return cnt
    except Exception:
        return 0


def get_database_statistics() -> dict:
    if not os.path.exists(DB_PATH):
        return {"total_apps": 0, "total_checkpoints": 0, "db_size_kb": 0}
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT count(DISTINCT thread_id), count(*) FROM checkpoints")
        t_cnt, c_cnt = cur.fetchone()
        conn.close()
        size_kb = round(os.path.getsize(DB_PATH) / 1024, 1)
        return {"total_apps": t_cnt, "total_checkpoints": c_cnt, "db_size_kb": size_kb}
    except Exception:
        return {"total_apps": 0, "total_checkpoints": 0, "db_size_kb": 0}


def build_zip_bytes_from_state(values: dict) -> bytes:
    """Üretilen uygulama dosyalarını bellekte ZIP arşivine dönüştürür."""
    buf = io.BytesIO()
    code_files = values.get("code_files") or {}
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in code_files.items():
            zf.writestr(fname, content)
        spec_md = (
            f"# {values.get('app_name', 'Uygulama')}\n\n"
            f"## PRD\n{values.get('prd_spec', '')}\n\n"
            f"## Sistem Mimarisi\n{values.get('architecture_spec', '')}\n\n"
            f"## QA Raporu\n{values.get('qa_report', '')}\n"
        )
        zf.writestr("MIMARI_VE_PRD.md", spec_md)
    buf.seek(0)
    return buf.getvalue()


def sync_session_from_thread(thread_id: str):
    """Seçilen thread'in durumunu session_state içine yükler."""
    cfg = {"configurable": {"thread_id": thread_id}}
    try:
        snap = sirket_motoru.app.get_state(cfg)
    except Exception:
        snap = None

    st.session_state.chat_history = []
    if snap and snap.values:
        vals = snap.values
        for m in vals.get("messages", []):
            role = "user" if isinstance(m, HumanMessage) else "assistant"
            st.session_state.chat_history.append({"role": role, "content": get_clean_text(m.content)})
        st.session_state.waiting_for_hitl = bool(snap.next and "Deployment_Gate" in snap.next)
    else:
        st.session_state.waiting_for_hitl = False


def render_cyclical_studio_matrix(thread_id: str):
    """
    Dümdüz doğrusal stepper yerine; LangGraph'ın döngüsel (git-gel yapabilen)
    yapısını, aktif departman matrisini ve gerçek düğüm geçiş izini gösterir.
    """
    cfg = {"configurable": {"thread_id": thread_id}}
    try:
        snap = sirket_motoru.app.get_state(cfg)
    except Exception:
        snap = None

    vals = snap.values if snap and snap.values else {}
    next_nodes = snap.next if snap and snap.next else ()

    cycle = vals.get("cycle_count") or 0
    rev_count = vals.get("revision_count") or 0
    has_prd = bool(vals.get("prd_spec"))
    has_arch = bool(vals.get("architecture_spec"))
    code_files = vals.get("code_files") or {}
    total_loc = vals.get("total_loc") or 0
    qa_verified = bool(vals.get("code_verified_by_qa"))
    qa_passed = bool(vals.get("qa_passed"))
    is_deployed = bool(vals.get("is_deployed"))
    waiting_hitl = bool("Deployment_Gate" in next_nodes)
    logs = vals.get("transition_log") or []

    # Genel Durum Rozeti
    if waiting_hitl:
        overall_badge = "🛑 KURUCU ONAYI / REVİZYON KARARI BEKLENİYOR (HITL)"
        overall_color = "#FB7185"
    elif is_deployed:
        overall_badge = "🚀 FİZİKSEL PAKET İNŞA EDİLDİ & ÇALIŞMAYA HAZIR"
        overall_color = "#34D399"
    elif cycle > 0:
        overall_badge = f"🔄 DÖNGÜSEL ÜRETİM AKTİF (Tur #{cycle})"
        overall_color = "#38BDF8"
    else:
        overall_badge = "⚪ YENİ UYGULAMA OTURUMU (GÖREV BEKLİYOR)"
        overall_color = "#9CA3AF"

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
            <div style="font-size:13px; font-weight:600; color:#E2E8F0;">
                🕸️ DÖNGÜSEL YAZILIM FABRİKASI & DEPARTMAN AĞI
                <span style="color:#9CA3AF; font-weight:400; margin-left:8px;">
                    (Orkestrasyon Döngüsü: <b>#{cycle}</b> • QA/Revizyon Turu: <b>#{rev_count}</b>)
                </span>
            </div>
            <div style="font-size:12px; font-weight:600; color:{overall_color};">
                {overall_badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5 Departman Düğümü Matrisi (Merkez Orkestratör + 4 Uzman Birim)
    c1, c2, c3, c4, c5 = st.columns(5)

    # 1. Stüdyo Direktörü (Orkestratör)
    last_target = logs[-1].get("target", "-") if logs else "-"
    dir_cls = "dept-done" if is_deployed else ("dept-active" if cycle > 0 else "dept-idle")
    with c1:
        st.markdown(
            f"""
            <div class="dept-card {dir_cls}">
                <div style="font-size:12px; font-weight:600; color:#F8FAFC;">👑 Stüdyo Direktörü</div>
                <div style="font-size:10px; color:#FBBF24; font-weight:600; margin:4px 0;">
                    {'MERKEZ ORKESTRATÖR' if cycle == 0 else f'{cycle} Kez Karar Verdi'}
                </div>
                <div style="font-size:11px; color:#9CA3AF; line-height:1.35;">
                    {f"Son Yönlendirme: <b>{last_target}</b>" if cycle > 0 else "Departmanlar arası ileri/geri döngüyü yönetir."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Ürün & Kapsam Lideri (CPO)
    prd_cls = "dept-done" if has_prd else "dept-idle"
    feat_cnt = len(vals.get("core_features") or [])
    with c2:
        st.markdown(
            f"""
            <div class="dept-card {prd_cls}">
                <div style="font-size:12px; font-weight:600; color:#F8FAFC;">💡 Ürün Lideri (CPO)</div>
                <div style="font-size:10px; color:{'#34D399' if has_prd else '#6B7280'}; font-weight:600; margin:4px 0;">
                    {'✅ PRD HAZIR' if has_prd else '⚪ BEKLEMEDE'}
                </div>
                <div style="font-size:11px; color:#9CA3AF; line-height:1.35;">
                    {f"{vals.get('app_type', '')} • {feat_cnt} MVP Özelliği" if has_prd else "Uygulama amacı ve MVP kapsamını çıkarır."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Sistem Mimarı (CTO)
    arch_cls = "dept-done" if has_arch else "dept-idle"
    stack_preview = ", ".join((vals.get("tech_stack") or [])[:3])
    with c3:
        st.markdown(
            f"""
            <div class="dept-card {arch_cls}">
                <div style="font-size:12px; font-weight:600; color:#F8FAFC;">📐 Sistem Mimarı (CTO)</div>
                <div style="font-size:10px; color:{'#34D399' if has_arch else '#6B7280'}; font-weight:600; margin:4px 0;">
                    {'✅ MİMARİ KURULDU' if has_arch else '⚪ BEKLEMEDE'}
                </div>
                <div style="font-size:11px; color:#9CA3AF; line-height:1.35;">
                    {stack_preview if has_arch else "Framework, veritabanı ve modül şemasını seçer."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Kıdemli Yazılımcı (Full-Stack)
    dev_cls = "dept-loop" if (rev_count > 0 and not is_deployed and not waiting_hitl) else ("dept-done" if code_files else "dept-idle")
    with c4:
        st.markdown(
            f"""
            <div class="dept-card {dev_cls}">
                <div style="font-size:12px; font-weight:600; color:#F8FAFC;">💻 Yazılım Mühendisliği</div>
                <div style="font-size:10px; color:{'#34D399' if code_files else '#6B7280'}; font-weight:600; margin:4px 0;">
                    {f"✅ {len(code_files)} DOSYA ({total_loc} SATIR)" if code_files else '⚪ BEKLEMEDE'}
                </div>
                <div style="font-size:11px; color:#9CA3AF; line-height:1.35;">
                    {f"Giriş: {vals.get('entrypoint_file', 'app.py')} (Rev #{rev_count})" if code_files else "Çok dosyalı gerçek Python kodunu inşa eder."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. QA, AST & Yayına Alma Kapısı
    if is_deployed:
        qa_cls, qa_lbl, qa_col = "dept-done", "🚀 YAYINDA / DİSKTE", "#34D399"
        qa_desc = f"Klasör: output_uygulamalar/{vals.get('app_slug', '')}"
    elif waiting_hitl:
        qa_cls, qa_lbl, qa_col = "dept-hitl", "🛑 ONAY / REVİZYON KAPISI", "#FDA4AF"
        qa_desc = f"QA: {'✅ Hatasız' if qa_passed else '⚠️ İncelemede'} • Kurucu kararı bekleniyor"
    elif qa_verified and not qa_passed:
        qa_cls, qa_lbl, qa_col = "dept-loop", "🔄 HATA YAKALADI -> DÖNGÜ", "#FBBF24"
        qa_desc = "AST/QA bulguları yazılımcıya geri gönderildi."
    else:
        qa_cls, qa_lbl, qa_col = "dept-idle", "⚪ DENETİM BEKLİYOR", "#6B7280"
        qa_desc = "AST sözdizimi, import ve kalite testi yapar."

    with c5:
        st.markdown(
            f"""
            <div class="dept-card {qa_cls}">
                <div style="font-size:12px; font-weight:600; color:#F8FAFC;">🛡️ QA & Dağıtım Kapısı</div>
                <div style="font-size:10px; color:{qa_col}; font-weight:600; margin:4px 0;">{qa_lbl}</div>
                <div style="font-size:11px; color:#9CA3AF; line-height:1.35;">{qa_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Canlı Döngüsel Geçiş İzi (Graph Hop Trail)
    if logs:
        node_icons = {
            "Studio_Director": "👑 Direktör",
            "Product_Lead": "💡 CPO",
            "System_Architect": "📐 CTO",
            "Lead_Developer": "💻 Yazılımcı",
            "QA_Security_Lead": "🛡️ QA/AST",
            "Deployment_Gate": "🚀 Paketleyici",
        }
        badges_html = []
        for idx, item in enumerate(logs):
            n_label = node_icons.get(item.get("node", ""), item.get("node", ""))
            cyc = item.get("cycle", "")
            is_backloop = "geri" in item.get("action", "").lower() or "düzeltme" in item.get("action", "").lower() or "revizyon" in item.get("action", "").lower()
            border_c = "rgba(245,158,11,0.5)" if is_backloop else "rgba(255,255,255,0.12)"
            text_c = "#FBBF24" if is_backloop else "#E2E8F0"
            badges_html.append(
                f'<span title="{item.get("action", "")}" style="display:inline-block; background:#15181E; '
                f'border:1px solid {border_c}; color:{text_c}; padding:2px 8px; border-radius:5px; margin:2px; font-size:11px;">'
                f'{n_label} <small style="color:#6B7280;">#{cyc}</small></span>'
            )
        trail_str = ' <span style="color:#5E6AD2; font-weight:700;">➔</span> '.join(badges_html)
        last_action = logs[-1].get("action", "")
        st.markdown(
            f"""
            <div class="trail-box">
                <b style="color:#CBD5E1;">🔁 Canlı Graf Geçiş İzi:</b> {trail_str}
                <div style="margin-top:4px; font-size:11px; color:#9CA3AF;">
                    <b>Son İşlem ({logs[-1].get('time', '')}):</b> {last_action}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def stream_studio_execution(input_payload, config: dict, status_title: str):
    """LangGraph akışını canlı olarak st.status kutusuna yazar."""
    with st.status(status_title, expanded=True) as status_box:
        for event in sirket_motoru.app.stream(input_payload, config=config, stream_mode="updates"):
            if not isinstance(event, dict):
                continue
            for node_name, node_out in event.items():
                if node_name == "Studio_Director" and isinstance(node_out, dict):
                    nxt = node_out.get("next_step", "-")
                    cyc = node_out.get("cycle_count", "-")
                    status_box.write(f"👑 **[Stüdyo Direktörü — Döngü #{cyc}]:** Sıradaki hedef birim ➔ `{nxt}`")
                elif node_name == "Product_Lead" and isinstance(node_out, dict):
                    status_box.write(
                        f"💡 **[Ürün Lideri - CPO]:** `{node_out.get('app_name')}` ({node_out.get('app_type')}) için PRD ve MVP kapsamı çıkarıldı."
                    )
                elif node_name == "System_Architect" and isinstance(node_out, dict):
                    stack = ", ".join(node_out.get("tech_stack") or [])
                    status_box.write(f"📐 **[Sistem Mimarı - CTO]:** Altyapı seçildi (`{stack}`), modül şeması hazırlandı.")
                elif node_name == "Lead_Developer" and isinstance(node_out, dict):
                    f_cnt = len(node_out.get("code_files") or {})
                    loc = node_out.get("total_loc") or 0
                    status_box.write(f"💻 **[Kıdemli Yazılımcı]:** `{f_cnt}` dosya ve `{loc}` satır gerçek Python kodu inşa edildi.")
                elif node_name == "QA_Security_Lead" and isinstance(node_out, dict):
                    passed = node_out.get("qa_passed", False)
                    if passed:
                        status_box.write("🛡️ **[QA & AST Denetimi]:** ✅ Sözdizimi, modül importları ve özellik kapsamı doğrulandı!")
                    else:
                        issues = node_out.get("qa_issues") or []
                        status_box.write(
                            f"🛡️ **[QA & AST Denetimi]:** ⚠️ {len(issues)} teknik hata yakalandı! Otomatik düzeltme döngüsü için Yazılımcıya geri gönderiliyor..."
                        )
                elif node_name == "Deployment_Gate" and isinstance(node_out, dict):
                    if node_out.get("is_deployed"):
                        status_box.write(f"🚀 **[Paketleme]:** Uygulama fiziksel diske yazıldı: `{node_out.get('app_folder')}`")
                    else:
                        status_box.write("🔄 **[Revizyon Döngüsü]:** Kurucu geri bildirimi işleme alındı, ilgili departmana yönlendiriliyor...")
                elif node_name == "__interrupt__":
                    status_box.write("🛑 **[Kurucu Onay Kapısı]:** Mimari ve kod hazır! İncelemeniz veya revizyon talebiniz bekleniyor.")

        snap = sirket_motoru.app.get_state(config)
        if snap.next and "Deployment_Gate" in snap.next:
            st.session_state.waiting_for_hitl = True
            status_box.update(label="🛑 Uygulama Kodu & QA Hazır — Kurucu Onayınız veya Revizyonunuz Bekleniyor", state="running", expanded=True)
        else:
            st.session_state.waiting_for_hitl = False
            status_box.update(label="🚀 Uygulama Başarıyla Paketlendi!", state="complete", expanded=False)


# ==============================================================================
# 3. Session State Başlatma
# ==============================================================================
all_threads = get_all_threads()
default_thread = all_threads[0] if all_threads else f"app-studio-{datetime.now().strftime('%m%d-%H%M')}"

if "active_thread_id" not in st.session_state:
    st.session_state.active_thread_id = default_thread
    sync_session_from_thread(default_thread)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "waiting_for_hitl" not in st.session_state:
    st.session_state.waiting_for_hitl = False

if "meta_chat_history" not in st.session_state:
    st.session_state.meta_chat_history = []


# ==============================================================================
# 4. Sol Kenar Çubuğu (Sidebar) — Stüdyo Kontrol & Uygulama Seçici
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏗️ AI YAZILIM STÜDYOSU")
    st.caption("Autonomous App Venture Studio • v5.0")

    st.link_button(
        "📚 LangGraph Başucu Kitabı (Yeni Sekme) ↗",
        url="/LangGraph_Basucu_Kitabi",
        type="primary",
        use_container_width=True,
    )
    st.link_button(
        "📖 Sistem Dokümantasyonu (Yeni Sekme) ↗",
        url="/Sistem_Dokumantasyonu",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("#### 📡 Stüdyo Altyapı Durumu")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown('<span class="badge-gold">🏗️ 5 Ajan</span><br><small style="color:#9CA3AF">Döngüsel Fabrika</small>', unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f'<span class="badge-cyan">⚡ Model</span><br><small style="color:#9CA3AF">{TARGET_MODEL}</small>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.markdown(f'<span class="badge-green">🔑 Key Havuzu</span><br><small style="color:#9CA3AF">{len(API_KEY_POOL)} Aktif Key</small>', unsafe_allow_html=True)
    with col_sb4:
        st.markdown('<span class="badge-cyan">💾 SQLite</span><br><small style="color:#9CA3AF">studio_apps.db</small>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📂 Aktif Uygulama Projesi")

    thread_options = ["➕ Yeni Uygulama Projesi Aç..."] + all_threads
    idx = thread_options.index(st.session_state.active_thread_id) if st.session_state.active_thread_id in all_threads else 0

    selected_opt = st.selectbox(
        "Geliştirilen Uygulamalar:",
        options=thread_options,
        index=idx,
        help="Geçmiş uygulamalar arasında geçiş yapın veya yeni bir uygulama başlatın.",
    )

    if selected_opt == "➕ Yeni Uygulama Projesi Aç...":
        suggested_id = f"app-{datetime.now().strftime('%m%d-%H%M%S')}"
        new_app_id = st.text_input("Proje Kodu (Slug):", value=suggested_id)
        if st.button("✨ Yeni Uygulama Masası Aç", use_container_width=True, type="primary"):
            clean_id = sirket_motoru.sanitize_slug(new_app_id)
            st.session_state.active_thread_id = clean_id
            st.session_state.waiting_for_hitl = False
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": (
                        f"👋 Yeni uygulama çalışma alanınız (`{clean_id}`) hazır! "
                        "Önce **0. Ürün & Mimari Tartışma Odası**'nda ne yapacağımızı ve teknolojileri konuşabilir "
                        "veya doğrudan buradan uygulama inşasını başlatabilirsiniz."
                    ),
                }
            ]
            st.rerun()
    else:
        if selected_opt != st.session_state.active_thread_id:
            st.session_state.active_thread_id = selected_opt
            sync_session_from_thread(selected_opt)
            st.rerun()

    with st.expander("⚡ Örnek Somut Uygulama Fikirleri", expanded=False):
        sample_apps = [
            (
                "💳 Abonelik & Nakit Akışı Uygulaması (Streamlit)",
                "Bireysel ve freelance kullanıcılar için aylık abonelikleri, gelir-gider kalemlerini ve yaklaşan ödemeleri SQLite veritabanında tutan, kategori bazlı Altair grafikleri ve CSV dışa aktarma özelliği sunan bir Streamlit web uygulaması geliştirin.",
            ),
            (
                "📦 Akıllı Stok & Sipariş REST API (FastAPI)",
                "Küçük e-ticaret depoları için ürün stok takibi, kritik stok eşiği uyarıları, sipariş düşme ve tedarikçi yenileme uç noktaları sunan SQLite + Pydantic tabanlı çalışan bir FastAPI REST mikroservisi geliştirin.",
            ),
            (
                "⏱️ Pomodoro & Odak Analitik Masası (Streamlit)",
                "Yazılımcılar için görev bazlı çalışma oturumlarını kaydeden, öncelik matrisi (Eisenhower) sunan ve haftalık verimlilik istatistiklerini SQLite üzerinde görselleştiren bir Streamlit uygulaması inşa edin.",
            ),
            (
                "🔍 Log & JSON Anomali Analiz Aracı (CLI)",
                "Sunucu log ve JSON kayıtlarını tarayıp hata frekanslarını, yavaş yanıt sürelerini ve kritik uyarıları Rich tablosuyla özetleyip Markdown raporu üreten örnek veri destekli bir Python CLI aracı geliştirin.",
            ),
        ]
        for label, prompt_txt in sample_apps:
            if st.button(label, use_container_width=True):
                # Yeni bir proje oturumu açıp doğrudan fabrikaya gönder
                new_tid = f"app-{datetime.now().strftime('%m%d-%H%M%S')}"
                st.session_state.active_thread_id = new_tid
                st.session_state.chat_history = []
                st.session_state.waiting_for_hitl = False
                st.session_state.quick_build_prompt = prompt_txt
                st.rerun()


# ==============================================================================
# 5. Üst Başlık (Header)
# ==============================================================================
active_cfg = {"configurable": {"thread_id": st.session_state.active_thread_id}}
try:
    active_snap = sirket_motoru.app.get_state(active_cfg)
    active_vals = active_snap.values if active_snap and active_snap.values else {}
except Exception:
    active_vals = {}

active_app_title = active_vals.get("app_name") or st.session_state.active_thread_id
active_app_type = active_vals.get("app_type") or "Henüz Belirlenmedi"

st.markdown(
    f"""
<div class="executive-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
            <h1 style="margin:0; font-size:21px; font-weight:600; color:#F8FAFC;">
                🏗️ OTONOM YAZILIM EVİ & UYGULAMA STÜDYOSU
            </h1>
            <p style="margin:4px 0 0 0; color:#9CA3AF; font-size:13px;">
                Ürün Fikri & Amaç Tartışması • Altyapı & Tech Stack Seçimi • Döngüsel Kodlama & AST/QA • Fiziksel Uygulama Teslimatı
            </p>
        </div>
        <div style="text-align:right;">
            <span style="font-size:11px; color:#9CA3AF;">Aktif Uygulama: <b>{active_app_title}</b></span><br>
            <span class="badge-gold">🏷️ {st.session_state.active_thread_id}</span>
            <span class="badge-cyan" style="margin-left:4px;">🧩 {active_app_type}</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 6. Ana Sekmeler (5 Odaklı Çalışma Alanı)
# ==============================================================================
tab_ideation, tab_factory, tab_workspace, tab_portfolio, tab_org = st.tabs(
    [
        "💡 0. Ürün & Mimari Tartışma Odası",
        "🏗️ 1. Otonom Yazılım Fabrikası (Canlı Döngü)",
        "💻 2. Üretilen Uygulama & Çalıştırma Konsolu",
        "🗄️ 3. Uygulama Portföyü (SQLite)",
        "🏢 4. Stüdyo Mimarisi & Dokümanlar",
    ]
)


# ------------------------------------------------------------------------------
# SEKME 0: ÜRÜN & MİMARİ TARTIŞMA ODASI (NE YAPACAĞIZ? HANGİ TEKNOLOJİYLE?)
# ------------------------------------------------------------------------------
with tab_ideation:
    st.markdown("#### 💡 Ürün Keşfi, Amaç & Teknoloji Yığını (Tech Stack) Tartışma Masası")
    st.caption(
        "Tek satır kod yazmadan önce CPO ve CTO ajanlarınızla **ne uygulaması yapacağımızı, hangi problemi çözeceğini, "
        "hangi arayüz ve veritabanı altyapısıyla kuracağımızı** tartışın; olgunlaşınca tek tıkla Yazılım Fabrikası'na aktarın."
    )

    # Hızlı Teknik Çerçeve Tercihleri (Tartışmaya Bağlam Katar)
    col_pref1, col_pref2, col_pref3 = st.columns(3)
    with col_pref1:
        pref_ui = st.selectbox(
            "🖥️ Düşünülen Uygulama Arayüzü:",
            [
                "Tartışarak Birlikte Karar Verelim",
                "Streamlit Web Uygulaması (Görsel Arayüz)",
                "FastAPI REST Mikroservisi (Swagger API)",
                "CLI & Otomasyon Aracı (Komut Satırı)",
            ],
        )
    with col_pref2:
        pref_db = st.selectbox(
            "💾 Düşünülen Veri Katmanı:",
            [
                "Tartışarak Birlikte Seçelim",
                "SQLite3 Yerel İlişkisel Veritabanı",
                "JSON / Dosya Tabanlı Hafif Depolama",
                "Bellek İçi + CSV / Excel Raporlama",
            ],
        )
    with col_pref3:
        meta_mode = st.selectbox(
            "🎯 Masadaki Muhatap Modu:",
            [
                "🏛️ Ürün & Mimari Konseyi (CPO + CTO Birlikte Tartışsın)",
                "💡 CPO ile Ürün & MVP Kapsamı (Ne yapalım, ne işe yarasın?)",
                "📐 CTO ile Altyapı & Tech Stack (Hangi teknoloji, nasıl mimari?)",
            ],
        )

    meta_chat_box = st.container(height=360)
    with meta_chat_box:
        if not st.session_state.meta_chat_history:
            st.info(
                "👋 **Tartışma Odasına Hoş Geldiniz!** Aklınızdaki ham bir uygulama fikrini veya çözmek istediğiniz bir problemi yazın.\n\n"
                "*Örnek:* 'Kendi portföyümdeki hisseleri ve kripto varlıkları takip edeceğim, alım maliyetimi hesaplayacak bir uygulama yapalım. "
                "Hangi özellikler olsun, Streamlit mi FastAPI mi kullanalım?'"
            )
        for msg in st.session_state.meta_chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                with st.chat_message("user", avatar="👔"):
                    st.write(content)
            elif role == "Co-Founder":
                with st.chat_message("assistant", avatar="💡"):
                    st.markdown(f"**💡 [CPO — ÜRÜN & KAPSAM VİZYONU]:**\n\n{content}")
            elif role == "Skeptic":
                with st.chat_message("assistant", avatar="📐"):
                    st.markdown(f"**📐 [CTO — ALTYAPI & TECH STACK MİMARİSİ]:**\n\n{content}")
            elif role == "Scribe":
                with st.chat_message("assistant", avatar="📋"):
                    st.markdown(f"**📋 [TEKNİK PM — YOL HARİTASI SENTEZİ]:**\n\n{content}")
            else:
                with st.chat_message("assistant", avatar="🏗️"):
                    st.markdown(content)

    # Aksiyon Butonları
    col_ma1, col_ma2, col_ma3, col_ma4 = st.columns([2.2, 1.3, 1.3, 1.0])
    with col_ma1:
        if st.button("🚀 Kararlaştırılan Uygulamayı Yazılım Fabrikası'na Gönder ve İnşa Et!", type="primary", use_container_width=True):
            if not st.session_state.meta_chat_history:
                st.warning("Önce nasıl bir uygulama yapacağımızı birkaç cümleyle tartışalım.")
            else:
                with st.spinner("📋 Tartışılan ürün ve teknoloji kararları mühendislik şartnamesine dönüştürülüyor..."):
                    extra_tech_note = f"Arayüz Tercihi: {pref_ui} | Veri Katmanı Tercihi: {pref_db}"
                    res = bridge_meta_to_operational_directive(st.session_state.meta_chat_history, custom_notes=extra_tech_note)
                    new_slug = sirket_motoru.sanitize_slug(res["title"])
                    new_tid = f"{new_slug[:28]}-{datetime.now().strftime('%H%M')}"
                    st.session_state.active_thread_id = new_tid
                    st.session_state.chat_history = []
                    st.session_state.waiting_for_hitl = False
                    st.session_state.quick_build_prompt = res["directive_text"]
                    st.success(
                        f"✅ **'{res['title']}'** şartnamesi hazırlandı ve `{new_tid}` projesi olarak **1. Otonom Yazılım Fabrikası** sekmesine aktarıldı! "
                        "Lütfen üstten **1. Otonom Yazılım Fabrikası** sekmesine geçin."
                    )
    with col_ma2:
        if st.button("💾 Ürün Keşif Notu Kaydet", use_container_width=True):
            if st.session_state.meta_chat_history:
                with st.spinner("Kaydediliyor..."):
                    p = save_session_as_brainstorm(st.session_state.meta_chat_history)
                    st.success(f"Kaydedildi: `{os.path.basename(p)}`")
    with col_ma3:
        if st.button("📐 Mimari Karar (ADR) Kaydet", use_container_width=True):
            if st.session_state.meta_chat_history:
                with st.spinner("ADR oluşturuluyor..."):
                    p = save_session_as_adr(st.session_state.meta_chat_history)
                    st.success(f"ADR Kaydedildi: `{os.path.basename(p)}`")
    with col_ma4:
        if st.button("🧹 Masayı Temizle", use_container_width=True):
            st.session_state.meta_chat_history = []
            st.rerun()

    idea_input = st.chat_input("Ne uygulaması yapalım? Amacını, özelliklerini veya teknoloji sorunuzu yazın...", key="ideation_input")
    if idea_input:
        enriched_topic = f"{idea_input}\n[Kurucu Ön Çerçevesi — Arayüz: {pref_ui}, Veri Katmanı: {pref_db}]"
        st.session_state.meta_chat_history.append({"role": "user", "content": idea_input})
        if "CPO ile Ürün" in meta_mode:
            with st.spinner("💡 CPO ürün kapsamını ve özellikleri kurguluyor..."):
                rep = chat_with_cofounder(enriched_topic, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": rep})
                st.rerun()
        elif "CTO ile Altyapı" in meta_mode:
            with st.spinner("📐 CTO altyapı, veritabanı ve modül mimarisini değerlendiriyor..."):
                rep = chat_with_skeptic(enriched_topic, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": rep})
                st.rerun()
        else:
            with st.spinner("🏛️ Ürün & Mimari Konseyi (CPO + CTO) toplanıyor..."):
                debate = run_boardroom_council_debate(enriched_topic, st.session_state.meta_chat_history[:-1])
                st.session_state.meta_chat_history.append({"role": "Co-Founder", "content": debate["cofounder"]})
                st.session_state.meta_chat_history.append({"role": "Skeptic", "content": debate["skeptic"]})
                st.session_state.meta_chat_history.append({"role": "Scribe", "content": debate["scribe_synthesis"]})
                st.rerun()

    with st.expander("📚 Kayıtlı Ürün Notları & Mimari Kararlar (Knowledge Vault)", expanded=False):
        v_docs = list_vault_documents()
        if v_docs:
            c_v1, c_v2 = st.columns([1, 2])
            with c_v1:
                labels = [f"{d['category']} | {d['name']}" for d in v_docs]
                s_i = st.selectbox("Belge Seçin:", range(len(v_docs)), format_func=lambda i: labels[i])
                chosen = v_docs[s_i]
            with c_v2:
                d_txt = read_document_content(chosen["path"])
                if "01_sirket_vizyonu.md" in chosen["name"]:
                    new_v = st.text_area("Stüdyo Manifestosunu Düzenle:", value=d_txt, height=220)
                    if st.button("💾 Manifestoyu Güncelle"):
                        update_company_vision(new_v)
                        st.success("Güncellendi!")
                        st.rerun()
                else:
                    st.markdown(d_txt)


# ------------------------------------------------------------------------------
# SEKME 1: OTONOM YAZILIM FABRİKASI & CANLI DÖNGÜSEL İCRA
# ------------------------------------------------------------------------------
with tab_factory:
    # Döngüsel Departman Ağı ve Canlı Geçiş İzi
    render_cyclical_studio_matrix(st.session_state.active_thread_id)

    # Eğer Tartışma Odası'ndan veya kenar çubuğundan bekleyen bir inşa emri geldiyse otomatik başlat!
    queued_prompt = st.session_state.pop("quick_build_prompt", None)

    factory_chat = st.container(height=300)
    with factory_chat:
        if not st.session_state.chat_history and not queued_prompt:
            st.info(
                "🏗️ **Otonom Yazılım Fabrikası Hazır!** Doğrudan geliştirmek istediğiniz uygulamayı aşağıya yazabilirsiniz.\n\n"
                "*Örnek:* `'Müşteri destek taleplerini önceliklendiren, SQLite kayıtlı ve istatistik panelli bir Streamlit uygulaması geliştirin.'* "
                "veya teknik bir sorunuzu doğrudan baş mühendise danışabilirsiniz."
            )
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👔"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🏗️"):
                    st.markdown(msg["content"])

    # KURUCU ONAY & DÖNGÜSEL REVİZYON KAPISI (HITL)
    if st.session_state.waiting_for_hitl:
        snap_hitl = sirket_motoru.app.get_state(active_cfg)
        v_hitl = snap_hitl.values if snap_hitl and snap_hitl.values else {}
        files_built = list((v_hitl.get("code_files") or {}).keys())

        st.markdown(
            f"""
            <div class="hitl-box">
                <h4 style="color:#93A0FF; margin:0 0 6px 0; font-size:15px; font-weight:600;">
                    🛑 KURUCU MİMARİ & KOD İNCELEME KAPISI (HUMAN-IN-THE-LOOP)
                </h4>
                <p style="color:#E2E8F0; font-size:13px; margin:0; line-height:1.55;">
                    <b>Uygulama:</b> {v_hitl.get('app_name', '-')} ({v_hitl.get('app_type', '-')}) &nbsp;|&nbsp;
                    <b>Altyapı:</b> {', '.join(v_hitl.get('tech_stack') or [])} &nbsp;|&nbsp;
                    <b>Üretilen Dosyalar ({len(files_built)} adet / {v_hitl.get('total_loc', 0)} satır):</b> <code>{', '.join(files_built)}</code><br>
                    <span style="color:#9CA3AF; font-size:12px;">
                        Kodları <b>2. Üretilen Uygulama & Çalıştırma Konsolu</b> sekmesinden inceleyebilir, onaylayıp fiziksel diske (`baslat.bat` ile) inşa edebilir
                        veya aşağıdan revizyon/ek özellik isteyerek departman döngüsünü devam ettirebilirsiniz!
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_h1, col_h2 = st.columns([1.4, 1.6])
        with col_h1:
            if st.button(
                "✅ Mimariyi ve Kodu ONAYLA — Fiziksel Uygulama Paketini İnşa Et",
                type="primary",
                use_container_width=True,
            ):
                stream_studio_execution(
                    None,
                    config=active_cfg,
                    status_title="🚀 Uygulama Dosyaları ve baslat.bat Fiziksel Diske İnşa Ediliyor...",
                )
                sync_session_from_thread(st.session_state.active_thread_id)
                st.balloons()
                st.rerun()

            if st.button("❌ Bu İnşayı Durdur / İptal Et", use_container_width=True):
                st.session_state.waiting_for_hitl = False
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": "🛑 Kurucu kararıyla fiziksel dağıtım durduruldu. Taslak kodlar bellekte korunuyor."}
                )
                st.rerun()

        with col_h2:
            rev_text = st.text_input(
                "🔄 Döngüsel Revizyon / Ek Özellik Talebi (İsteğe Bağlı):",
                placeholder="Örn: 'JSON dışa aktarma butonu ekle' veya 'Veritabanını SQLite yerine JSON yap'...",
                key="hitl_revision_input",
            )
            rev_dept_label = st.radio(
                "Revizyon Hangi Departmana Dönsün?",
                [
                    "🤖 Otomatik Seç (Direktör Karar Versin)",
                    "💻 Yazılım Mühendisliğine Dönsün (Özellik / UI / Kod Değişikliği)",
                    "📐 Sistem Mimarına Dönsün (Altyapı / Tech Stack / DB Değişikliği)",
                ],
                horizontal=True,
            )
            if st.button("🔁 Revizyon Döngüsünü Başlat (Departmana Geri Gönder)", use_container_width=True):
                if not rev_text.strip():
                    st.warning("Lütfen yapılmasını istediğiniz değişikliği kısaca yazın.")
                else:
                    target_dept = None
                    if "Yazılım Mühendisliğine" in rev_dept_label:
                        target_dept = "Lead_Developer"
                    elif "Sistem Mimarına" in rev_dept_label:
                        target_dept = "System_Architect"

                    sirket_motoru.app.update_state(
                        active_cfg,
                        {
                            "founder_feedback": rev_text.strip(),
                            "feedback_target": target_dept,
                            "messages": [HumanMessage(content=f"[KURUCU REVİZYON TALEBİ]: {rev_text.strip()}")],
                        },
                    )
                    stream_studio_execution(
                        None,
                        config=active_cfg,
                        status_title="🔄 Kurucu Revizyon Döngüsü Çalıştırılıyor (Departmanlar Güncelliyor)...",
                    )
                    sync_session_from_thread(st.session_state.active_thread_id)
                    st.rerun()

    # Doğrudan Fabrika Girdisi
    direct_prompt = st.chat_input(
        "Geliştirilecek uygulamayı tarif edin (veya teknik soru sormak için başında '?' kullanın)...",
        key="factory_chat_input",
    )
    effective_prompt = queued_prompt or direct_prompt

    if effective_prompt:
        txt_clean = effective_prompt.strip()
        is_pure_question = txt_clean.startswith("?") or (
            txt_clean.endswith("?")
            and len(txt_clean) < 120
            and not any(w in txt_clean.lower() for w in ["geliştir", "inşa", "oluştur", "kodla", "yapalım", "kur", "yaz"])
        )

        if is_pure_question:
            st.session_state.chat_history.append({"role": "user", "content": txt_clean})
            with st.spinner("📐 Baş Mimar & Stüdyo Direktörü yanıtlıyor..."):
                advisor_llm = get_gemini_llm(temperature=0.35)
                q_prompt = (
                    "Sen Otonom Yazılım Stüdyosunun Baş Mimarı ve Direktörüsün. "
                    f"Aktif uygulama: '{active_app_title}' ({active_app_type}). "
                    "Kurucunun teknik veya ürün sorusunu net, pratik ve yol gösterici biçimde yanıtla:\n\n"
                    f"SORU: {txt_clean}"
                )
                ans = get_clean_text(advisor_llm.invoke(q_prompt).content)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.rerun()
        else:
            # Eğer mevcut thread zaten tamamlanmış başka bir uygulamaysa ve yeni sıfırdan inşa isteniyorsa:
            if active_vals.get("is_deployed"):
                # Mevcut dağıtılmış uygulamada revizyon olarak devam et!
                sirket_motoru.app.update_state(
                    active_cfg,
                    {
                        "is_deployed": False,
                        "founder_feedback": txt_clean,
                        "messages": [HumanMessage(content=txt_clean)],
                    },
                )
                stream_studio_execution(
                    {"messages": [HumanMessage(content=txt_clean)], "is_deployed": False, "founder_feedback": txt_clean},
                    config=active_cfg,
                    status_title="🔄 Mevcut Uygulama Üzerinde Yeni Geliştirme Döngüsü Başlatıldı...",
                )
            else:
                initial_state = {
                    "messages": [HumanMessage(content=txt_clean)],
                    "next_step": "Studio_Director",
                    "app_name": None,
                    "app_slug": None,
                    "app_type": None,
                    "purpose_summary": None,
                    "core_features": None,
                    "prd_spec": None,
                    "tech_stack": None,
                    "database_choice": None,
                    "entrypoint_file": None,
                    "planned_files": None,
                    "architecture_spec": None,
                    "code_files": None,
                    "total_loc": 0,
                    "code_verified_by_qa": False,
                    "qa_passed": False,
                    "qa_report": None,
                    "qa_issues": [],
                    "revision_count": 0,
                    "founder_feedback": None,
                    "feedback_target": None,
                    "is_deployed": False,
                    "app_folder": None,
                    "run_command_hint": None,
                    "cycle_count": 0,
                    "transition_log": [],
                }
                stream_studio_execution(
                    initial_state,
                    config=active_cfg,
                    status_title="🏗️ Otonom Yazılım Fabrikası Çalışıyor (PRD ➔ Mimari ➔ Kodlama ➔ AST/QA)...",
                )
            sync_session_from_thread(st.session_state.active_thread_id)
            st.rerun()


# ------------------------------------------------------------------------------
# SEKME 2: ÜRETİLEN UYGULAMA & ÇALIŞTIRMA KONSOLU (TANGIBLE APP WORKSPACE)
# ------------------------------------------------------------------------------
with tab_workspace:
    st.markdown("#### 💻 Üretilen Uygulama Dosyaları, Mimari Şartname & Canlı Çalıştırma")

    if not active_vals.get("prd_spec") and not active_vals.get("code_files"):
        st.info(
            "Bu proje oturumunda henüz üretilmiş bir uygulama bulunmuyor. "
            "**0. Tartışma Odası** veya **1. Yazılım Fabrikası** sekmesinden bir uygulama inşası başlatabilirsiniz."
        )
    else:
        # Üst Özet Metrikler ve Fiziksel Çalıştırma Çubuğu
        code_map = active_vals.get("code_files") or {}
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Uygulama Tipi", active_vals.get("app_type") or "-")
        with m2:
            st.metric("Üretilen Dosya", f"{len(code_map)} Adet")
        with m3:
            st.metric("Python Kod Satırı", f"{active_vals.get('total_loc') or 0} Satır")
        with m4:
            qa_stat = "✅ Doğrulandı" if active_vals.get("qa_passed") else ("⏳ İncelemede" if code_map else "-")
            st.metric("AST & QA Durumu", qa_stat)

        # Fiziksel Klasör & Tek Tıkla Başlatıcı
        app_folder = active_vals.get("app_folder")
        if active_vals.get("is_deployed") and app_folder and os.path.exists(app_folder):
            st.markdown(
                f"""
                <div class="report-card" style="border-color:rgba(16,185,129,0.45);">
                    <div style="font-size:14px; font-weight:600; color:#34D399; margin-bottom:4px;">
                        🚀 Uygulama Fiziksel Diskte Hazır!
                    </div>
                    <div style="font-size:12px; color:#E2E8F0;">
                        <b>Klasör Yolu:</b> <code>{app_folder}</code><br>
                        <b>Çalıştırma Komutu:</b> <code>{active_vals.get('run_command_hint', '')}</code>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_run1, col_run2, col_run3 = st.columns(3)
            with col_run1:
                if st.button("▶️ Uygulamayı Yeni Pencerede Başlat (baslat.bat)", type="primary", use_container_width=True):
                    bat_file = os.path.join(app_folder, "baslat.bat")
                    if os.path.exists(bat_file):
                        subprocess.Popen(["cmd.exe", "/c", "start", "", bat_file], cwd=app_folder)
                        st.success("🚀 Uygulama yeni bir terminal/tarayıcı penceresinde başlatıldı!")
                    else:
                        st.error("baslat.bat bulunamadı.")
            with col_run2:
                if st.button("📂 Uygulama Klasörünü Aç (Explorer)", use_container_width=True):
                    subprocess.Popen(["explorer.exe", app_folder])
            with col_run3:
                zip_bytes = build_zip_bytes_from_state(active_vals)
                st.download_button(
                    "📦 Tüm Uygulama Paketini İndir (.zip)",
                    data=zip_bytes,
                    file_name=f"{active_vals.get('app_slug', 'uygulama')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
        elif code_map:
            zip_bytes = build_zip_bytes_from_state(active_vals)
            st.download_button(
                "📦 Taslak Uygulama Paketini İndir (.zip) — (Fiziksel inşa için Fabrika sekmesinden Onaylayın)",
                data=zip_bytes,
                file_name=f"{active_vals.get('app_slug', 'taslak_uygulama')}.zip",
                mime="application/zip",
                use_container_width=True,
            )

        # Alt Sekmeler: Kaynak Kodlar | PRD | Sistem Mimarisi | QA Raporu
        sub_code, sub_prd, sub_arch, sub_qa = st.tabs(
            ["📂 Çok Dosyalı Kaynak Kodu", "💡 Ürün Şartnamesi (PRD)", "📐 Sistem Mimarisi & Tech Stack", "🛡️ QA & AST Denetim Raporu"]
        )

        with sub_code:
            if code_map:
                f_names = list(code_map.keys())
                sel_file = st.selectbox("İncelemek İstediğiniz Dosyayı Seçin:", f_names)
                f_content = code_map[sel_file]
                lang = "python" if sel_file.endswith(".py") else ("markdown" if sel_file.endswith(".md") else "text")
                st.code(f_content, language=lang, line_numbers=True)
                st.download_button(
                    f"📥 {sel_file} Dosyasını İndir",
                    data=f_content,
                    file_name=sel_file,
                    use_container_width=True,
                )
            else:
                st.info("Henüz kod dosyası üretilmedi.")

        with sub_prd:
            if active_vals.get("core_features"):
                st.markdown("**🎯 MVP Temel Özellikleri:**")
                for feat in active_vals["core_features"]:
                    st.markdown(f"- ✅ {feat}")
                st.markdown("---")
            st.markdown(active_vals.get("prd_spec") or "PRD henüz oluşturulmadı.")

        with sub_arch:
            if active_vals.get("tech_stack"):
                st.markdown(f"**🛠️ Seçilen Teknoloji Yığını:** `{', '.join(active_vals['tech_stack'])}`")
                st.markdown(f"**💾 Veri Katmanı:** `{active_vals.get('database_choice', '-')}`")
                st.markdown("---")
            st.markdown(active_vals.get("architecture_spec") or "Mimari belge henüz oluşturulmadı.")

        with sub_qa:
            st.markdown(active_vals.get("qa_report") or "QA denetimi henüz çalışmadı.")


# ------------------------------------------------------------------------------
# SEKME 3: UYGULAMA PORTFÖYÜ & SQLITE VERİTABANI (APP REGISTRY)
# ------------------------------------------------------------------------------
with tab_portfolio:
    st.markdown("#### 🗄️ Geliştirilen Uygulamalar Portföyü (`studio_apps.db`)")
    st.caption("Her uygulama kendi gerçek adı, arayüz tipi, teknoloji yığını, dosya/satır sayısı ve QA döngüsüyle benzersiz olarak kaydedilir:")

    db_stats = get_database_statistics()
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Toplam Uygulama Projesi", f"{db_stats['total_apps']} Adet")
    with s2:
        st.metric("Toplam LangGraph Checkpoint", f"{db_stats['total_checkpoints']} Adım")
    with s3:
        st.metric("SQLite Boyutu", f"{db_stats['db_size_kb']} KB")
    with s4:
        disk_apps = [d for d in os.listdir(sirket_motoru.OUTPUT_APPS_DIR) if os.path.isdir(os.path.join(sirket_motoru.OUTPUT_APPS_DIR, d))]
        st.metric("Diskte Kurulu Paket", f"{len(disk_apps)} Klasör")

    if all_threads:
        portfolio_rows = []
        for tid in all_threads:
            cfg_t = {"configurable": {"thread_id": tid}}
            snap_t = sirket_motoru.app.get_state(cfg_t)
            v_t = snap_t.values if snap_t and snap_t.values else {}
            c_files = v_t.get("code_files") or {}
            t_stack = ", ".join((v_t.get("tech_stack") or [])[:4]) or "-"
            waiting_t = bool(snap_t and snap_t.next and "Deployment_Gate" in snap_t.next)

            if v_t.get("is_deployed"):
                st_label = "🚀 Fiziksel Paket Hazır"
            elif waiting_t:
                st_label = "🛑 Kurucu Onayı Bekliyor"
            elif v_t.get("prd_spec"):
                st_label = "🔄 Geliştiriliyor"
            else:
                st_label = "⚪ Başlangıç"

            portfolio_rows.append(
                {
                    "Proje Kodu": tid,
                    "Uygulama Adı": v_t.get("app_name") or "(Henüz İsimlendirilmedi)",
                    "Uygulama Tipi": v_t.get("app_type") or "-",
                    "Teknoloji Yığını": t_stack,
                    "Dosya / Satır": f"{len(c_files)} dosya / {v_t.get('total_loc') or 0} satır" if c_files else "-",
                    "Döngü / Revizyon": f"#{v_t.get('cycle_count') or 0} tur ({v_t.get('revision_count') or 0} rev)",
                    "QA Durumu": "✅ Geçti" if v_t.get("qa_passed") else ("⚠️ Bekliyor" if c_files else "-"),
                    "Durum": st_label,
                }
            )
        st.dataframe(pd.DataFrame(portfolio_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Veritabanında henüz kayıtlı bir uygulama projesi yok.")

    with st.expander("⏱️ Gelişmiş: Aktif Uygulamanın Checkpoint Zaman Çizelgesi (Time-Travel)", expanded=False):
        try:
            hist = list(sirket_motoru.app.get_state_history(active_cfg))
            if hist:
                h_rows = []
                for idx_h, sn in enumerate(hist):
                    src = sn.metadata.get("source", "-") if sn.metadata else "-"
                    stp = sn.metadata.get("step", idx_h) if sn.metadata else idx_h
                    h_rows.append(
                        {
                            "Adım": stp,
                            "Kaynak": src,
                            "Sıradaki Düğüm": ", ".join(sn.next) if sn.next else "END",
                            "Checkpoint ID": sn.config["configurable"].get("checkpoint_id", "")[:14] + "...",
                        }
                    )
                st.dataframe(pd.DataFrame(h_rows), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.caption(f"Zaman çizelgesi bilgisi: {exc}")


# ------------------------------------------------------------------------------
# SEKME 4: YAZILIM EVİ MİMARİSİ & DEPARTMANLAR
# ------------------------------------------------------------------------------
with tab_org:
    st.markdown("#### 🏢 Otonom Yazılım Stüdyosu Departmanları & Döngüsel Çalışma İlkeleri")
    st.caption("Şirketimiz danışmanlık/araştırma şablonları yerine doğrudan çalışan yazılım ürünleri inşa eden 5 uzman birimden oluşur:")

    co1, co2 = st.columns(2)
    with co1:
        st.markdown(
            """
            <div class="report-card">
                <h4 style="color:#FBBF24; margin:0 0 6px 0; font-size:14px;">👑 1. Stüdyo Direktörü (Döngüsel Orkestratör)</h4>
                <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                    <b>Rol:</b> Merkezi Yönlendirici (Hub)<br>
                    <b>Görev:</b> Süreci dümdüz bir hat gibi değil, canlı bir döngü olarak yönetir. QA hata bulursa kodu yazılımcıya geri yollar; Kurucu revizyon isterse mimara veya yazılımcıya geri döndürür.
                </p>
            </div>
            <div class="report-card">
                <h4 style="color:#E879F9; margin:0 0 6px 0; font-size:14px;">💡 2. Ürün & Kapsam Lideri (CPO)</h4>
                <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                    <b>Rol:</b> Ürün Stratejisti & PRD Yazarı<br>
                    <b>Görev:</b> Uygulamanın çözdüğü gerçek problemi, kullanıcı akışını, başlangıç örnek verilerini (seed data) ve somut MVP özelliklerini belirler.
                </p>
            </div>
            <div class="report-card">
                <h4 style="color:#38BDF8; margin:0 0 6px 0; font-size:14px;">📐 3. Sistem Mimarı & CTO</h4>
                <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                    <b>Rol:</b> Altyapı & Tech Stack Lideri<br>
                    <b>Görev:</b> İşe en uygun teknoloji yığınını (<code>Streamlit</code>, <code>FastAPI</code>, <code>SQLite3</code>, <code>Pydantic</code>, <code>CLI</code>) ve dosyalar arası fonksiyon/sınıf sözleşmelerini tasarlar.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with co2:
        st.markdown(
            """
            <div class="report-card">
                <h4 style="color:#34D399; margin:0 0 6px 0; font-size:14px;">💻 4. Kıdemli Yazılım Mühendisi (Full-Stack)</h4>
                <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                    <b>Rol:</b> Çok Dosyalı Uygulama Geliştirici<br>
                    <b>Görev:</b> Hiçbir <code>TODO</code> veya içi boş şablon bırakmadan; veritabanı katmanını, iş mantığını, kullanıcı arayüzünü/API uçlarını ve <code>README.md</code> dosyasını eksiksiz kodlar.
                </p>
            </div>
            <div class="report-card">
                <h4 style="color:#FB7185; margin:0 0 6px 0; font-size:14px;">🛡️ 5. QA, AST Denetçisi & Kurucu Kapısı (HITL)</h4>
                <p style="color:#9CA3AF; font-size:13px; line-height:1.5;">
                    <b>Rol:</b> Deterministik Sözdizimi + AI Kalite Kontrolü<br>
                    <b>Görev:</b> Üretilen tüm Python dosyalarını <code>ast.parse()</code> ve çapraz modül import kontrolünden geçirir. Kurucu onayladığında <code>output_uygulamalar/</code> altına <code>baslat.bat</code> ile fiziksel olarak inşa eder.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("📄 Kurumsal Sistem Mimari Dokümanını İndir (PDF)", expanded=False):
        try:
            from pdf_olusturucu import generate_enterprise_documentation_pdf

            pdf_b = generate_enterprise_documentation_pdf()
            st.download_button(
                "📥 Sistem Mimari Rehberini PDF İndir",
                data=pdf_b,
                file_name="AI_Yazilim_Studyosu_Mimari_Rehberi.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.caption(f"PDF motoru notu: {exc}")
