"""
================================================================================
📖 ZİNCİRLERDEN OTONOM ŞİRKETLERE: LANGGRAPH E-KİTAP DERLEYİCİ & OKUYUCU 📖
================================================================================
Sunucusuz (Zero-Daemon), karanlık temalı, sayfa sayfa (bölüm bölüm) okunabilen,
Mermaid şema destekli, arama ve tarayıcı hafızalı (localStorage + JSON yedek)
modern Web E-Kitap üreticisi.

Kullanım:
  python kitap_okuyucu.py --build   -> LANGGRAPH_E_KITAP.html üretir ve çıkar (Daemon yok)
  python kitap_okuyucu.py --open    -> Üretir, tarayıcıda açar ve anında çıkar (Daemon yok)
================================================================================
"""

import os
import re
import sys
import json
import socket
import webbrowser
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_MD_PATH = os.path.join(ROOT_DIR, "LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.md")
BOOK_PDF_PATH = os.path.join(ROOT_DIR, "LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.pdf")
STATIC_HTML_PATH = os.path.join(ROOT_DIR, "LANGGRAPH_E_KITAP.html")
NOTES_JSON_PATH = os.path.join(ROOT_DIR, "kitap_notlarim.json")


def parse_book_into_chapters(md_text: str) -> list[dict]:
    """
    Markdown kitabını mantıksal sayfalara (Önsöz, Bölüm 1..12, Ek 1..2) ayırır.
    Böylece tek bir uzun sayfa yerine gerçek bir e-kitap gibi sayfa sayfa okunur.
    """
    lines = md_text.splitlines()
    chapters = []

    current_part = "Giriş & Manifesto"
    current_title = "Kapak & Önsöz"
    current_lines = []

    part_pattern = re.compile(r"^#\s+(KISIM\s+[IVX]+:.*|🧭\s*EKLER:.*)$")
    chapter_pattern = re.compile(r"^##\s+(Önsöz:.*|Bölüm\s+\d+:.*|Ek\s+\d+:.*)$")

    started_chapters = False
    prev_part = current_part

    for line in lines:
        p_match = part_pattern.match(line.strip())
        c_match = chapter_pattern.match(line.strip())

        if p_match:
            current_part = p_match.group(1).replace("🧭 ", "").strip()
            continue

        if c_match:
            header_text = c_match.group(1).strip()
            if started_chapters and current_lines:
                content_str = "\n".join(current_lines).strip()
                content_str = re.sub(r"(\n---\s*)+$", "", content_str).strip()
                word_count = len(content_str.split())
                chapters.append({
                    "id": len(chapters),
                    "part": prev_part,
                    "title": current_title,
                    "short_title": _make_short_title(current_title),
                    "markdown": content_str,
                    "read_min": max(2, round(word_count / 170))
                })
                current_lines = []

            started_chapters = True
            prev_part = current_part
            current_title = header_text
            current_lines.append(line)
        else:
            if not started_chapters:
                prev_part = current_part
            current_lines.append(line)

    if current_lines:
        content_str = "\n".join(current_lines).strip()
        content_str = re.sub(r"(\n---\s*)+$", "", content_str).strip()
        word_count = len(content_str.split())
        chapters.append({
            "id": len(chapters),
            "part": prev_part,
            "title": current_title,
            "short_title": _make_short_title(current_title),
            "markdown": content_str,
            "read_min": max(2, round(word_count / 170))
        })

    return chapters


def _make_short_title(title: str) -> str:
    if title.startswith("Önsöz:"):
        return "Önsöz: Mimari Manifesto"
    return title


def clean_markdown_links(md_text: str) -> str:
    """Yerel file:/// linklerini web okuyucuda temiz kod rozetlerine dönüştürür."""
    def repl(match):
        label = match.group(1)
        url = match.group(2)
        if url.startswith("file:///"):
            return f"`📂 {label}`"
        return match.group(0)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, md_text)


def get_chapters_json_str() -> str:
    with open(BOOK_MD_PATH, "r", encoding="utf-8") as f:
        raw_md = clean_markdown_links(f.read())
    chapters = parse_book_into_chapters(raw_md)
    # </script> çakışmasını önlemek için güvenli kaçış
    return json.dumps(chapters, ensure_ascii=False).replace("</", "<\\/")


# ==============================================================================
# KARANLIK TEMALI SUNUCUSUZ (SERVERLESS) WEB KİTAP OKUYUCU ŞABLONU
# ==============================================================================
READER_HTML = r"""<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zincirlerden Otonom Şirketlere — LangGraph Başucu Kitabı</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark-dimmed.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --reader-font-size: 18px;
    }
    body {
      background-color: #090d16;
      color: #e2e8f0;
      font-family: 'Inter', sans-serif;
    }
    .book-prose {
      font-family: 'Literata', Georgia, serif;
      font-size: var(--reader-font-size);
      line-height: 1.85;
      color: #cbd5e1;
    }
    .book-prose h1 {
      font-family: 'Inter', sans-serif;
      font-size: 2.1em;
      font-weight: 800;
      line-height: 1.25;
      color: #f8fafc;
      margin-bottom: 0.75em;
      letter-spacing: -0.02em;
    }
    .book-prose h2 {
      font-family: 'Inter', sans-serif;
      font-size: 1.65em;
      font-weight: 800;
      line-height: 1.3;
      color: #f8fafc;
      margin-top: 0.4em;
      margin-bottom: 0.8em;
      padding-bottom: 0.45em;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .book-prose h3 {
      font-family: 'Inter', sans-serif;
      font-size: 1.28em;
      font-weight: 700;
      color: #34d399;
      margin-top: 1.9em;
      margin-bottom: 0.65em;
    }
    .book-prose h4 {
      font-family: 'Inter', sans-serif;
      font-size: 1.08em;
      font-weight: 700;
      color: #38bdf8;
      margin-top: 1.5em;
      margin-bottom: 0.5em;
    }
    .book-prose p {
      margin-bottom: 1.25em;
    }
    .book-prose strong {
      color: #f1f5f9;
      font-weight: 700;
    }
    .book-prose em {
      color: #93c5fd;
    }
    .book-prose ul, .book-prose ol {
      margin-bottom: 1.35em;
      padding-left: 1.5em;
    }
    .book-prose ul { list-style-type: disc; }
    .book-prose ol { list-style-type: decimal; }
    .book-prose li {
      margin-bottom: 0.55em;
    }
    .book-prose hr {
      border: 0;
      border-top: 1px solid rgba(255,255,255,0.08);
      margin: 2.2em 0;
    }
    .book-prose code:not(pre code) {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.84em;
      background: rgba(15, 23, 42, 0.9);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.22);
      padding: 0.15em 0.45em;
      border-radius: 6px;
    }
    .book-prose pre {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82em;
      line-height: 1.6;
      background: #0d1321 !important;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 14px;
      padding: 1.15em 1.3em;
      overflow-x: auto;
      margin: 1.5em 0;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    .book-prose blockquote {
      border-left: 4px solid #38bdf8;
      background: rgba(15, 23, 42, 0.65);
      padding: 1em 1.35em;
      border-radius: 0 14px 14px 0;
      margin: 1.5em 0;
      color: #e2e8f0;
      font-style: italic;
    }
    .book-prose blockquote p:last-child { margin-bottom: 0; }
    .book-prose table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin: 1.75em 0;
      font-family: 'Inter', sans-serif;
      font-size: 0.86em;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 14px;
      overflow: hidden;
    }
    .book-prose th {
      background: rgba(30, 41, 59, 0.85);
      color: #f8fafc;
      font-weight: 700;
      text-align: left;
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .book-prose td {
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      background: rgba(15, 23, 42, 0.5);
      color: #cbd5e1;
      vertical-align: top;
    }
    .book-prose tr:last-child td { border-bottom: none; }
    .mermaid-box {
      background: #0d1424;
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 16px;
      padding: 22px;
      margin: 1.8em 0;
      display: flex;
      justify-content: center;
      overflow-x: auto;
    }
    .callout-card {
      border-radius: 16px;
      padding: 18px 22px;
      margin: 1.6em 0;
      font-family: 'Inter', sans-serif;
      font-size: 0.92em;
      line-height: 1.65;
      font-style: normal;
    }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
  </style>
</head>
<body class="h-screen overflow-hidden flex flex-col">

  <!-- Üst İlerleme Çubuğu -->
  <div class="w-full h-1 bg-slate-900">
    <div id="top-progress" class="h-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 transition-all duration-300" style="width: 7%"></div>
  </div>

  <!-- Üst Başlık Barı -->
  <header class="h-16 bg-slate-950/90 backdrop-blur border-b border-white/10 px-4 md:px-6 flex items-center justify-between shrink-0 z-30">
    <div class="flex items-center gap-3">
      <button onclick="toggleSidebar()" class="p-2 rounded-xl hover:bg-white/10 text-slate-300 transition" title="İçindekiler Menüsü">
        ☰
      </button>
      <div class="flex items-center gap-2.5">
        <span class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 text-slate-950 font-extrabold flex items-center justify-center shadow-lg shadow-emerald-500/20">📖</span>
        <div>
          <div class="text-sm font-bold text-white leading-tight">Zincirlerden Otonom Şirketlere</div>
          <div id="header-subtitle" class="text-[11px] text-slate-400 font-mono">LangGraph & Ajan Mimarisi Başucu Kitabı</div>
        </div>
      </div>
    </div>

    <!-- Sağ Kontroller -->
    <div class="flex items-center gap-2 md:gap-3">
      <a id="cockpit-back-btn" href="/" target="_top" class="hidden px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/15 text-slate-200 text-xs font-semibold transition items-center gap-1.5">
        <span>👑</span> <span class="hidden lg:inline">Yönetici Kokpiti</span>
      </a>

      <span id="read-badge" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-white/10 text-xs text-slate-300 font-mono">
        ⏱️ ~5 dk okuma
      </span>

      <!-- Font Boyutu -->
      <div class="hidden md:flex items-center bg-slate-900 border border-white/10 rounded-xl p-0.5 text-xs">
        <button onclick="changeFontSize(-2)" class="px-2.5 py-1 hover:bg-white/10 rounded-lg text-slate-300 font-semibold">A-</button>
        <button onclick="changeFontSize(0)" class="px-2 py-1 hover:bg-white/10 rounded-lg text-slate-400">A</button>
        <button onclick="changeFontSize(2)" class="px-2.5 py-1 hover:bg-white/10 rounded-lg text-slate-200 font-bold">A+</button>
      </div>

      <!-- Notlarım Butonu -->
      <button onclick="toggleNotesDrawer()" class="px-3 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-semibold transition flex items-center gap-1.5">
        <span>📝</span> <span class="hidden sm:inline">Bölüm Notum</span>
      </button>

      <!-- PDF İndir Butonu -->
      <a id="pdf-download-btn" href="__PDF_HREF__" download="LangGraph_ve_Otonom_Ajanlar_Kitabi.pdf" target="_blank" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 text-xs font-extrabold transition shadow-lg shadow-emerald-500/20 flex items-center gap-1.5">
        <span>📥</span> <span>PDF İndir</span>
      </a>
    </div>
  </header>

  <!-- Gövde: Sol İçindekiler + Orta Sayfa Okuyucu + Sağ Not Çekmecesi -->
  <div class="flex-1 flex overflow-hidden relative">

    <!-- SOL İÇİNDEKİLER PANELİ -->
    <aside id="sidebar" class="w-80 bg-slate-950/95 border-r border-white/10 flex flex-col shrink-0 transition-all duration-300 z-20">
      <div class="p-4 border-b border-white/10">
        <div class="relative">
          <input id="search-input" oninput="filterTOC()" type="text" placeholder="Kitap içinde kavram ara..." class="w-full bg-slate-900 border border-white/10 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500">
          <span class="absolute left-3 top-2 text-slate-500 text-xs">🔍</span>
        </div>
        <div class="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span id="progress-label">Okuma İlerlemesi: 1 / 15</span>
          <span id="completed-label" class="text-emerald-400">0 tamamlandı</span>
        </div>
      </div>

      <nav id="toc-list" class="flex-1 overflow-y-auto custom-scroll p-3 space-y-4">
        <!-- JS ile doldurulur -->
      </nav>
    </aside>

    <!-- ORTA KİTAP SAYFASI ALANI -->
    <main id="reader-scroll" class="flex-1 overflow-y-auto custom-scroll px-5 sm:px-10 md:px-16 py-10 scroll-smooth">
      <div class="max-w-3xl mx-auto">
        <!-- Kısım & Sayfa Üst Rozeti -->
        <div class="flex items-center justify-between mb-4">
          <span id="chapter-part-badge" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            KISIM I
          </span>
          <span id="page-counter" class="text-xs font-mono text-slate-500">Sayfa 1 / 15</span>
        </div>

        <!-- Bölüm İçeriği -->
        <article id="chapter-content" class="book-prose">
          Yükleniyor...
        </article>

        <!-- Sayfa Sonu Okundu İşareti & İleri-Geri Kartları -->
        <div class="mt-14 pt-8 border-t border-white/10">
          <div class="flex items-center justify-between mb-6">
            <button onclick="markCurrentCompleted()" id="btn-complete" class="px-4 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-semibold transition flex items-center gap-2">
              <span>✓</span> <span>Bu Bölümü Tamamladım Olarak İşaretle</span>
            </button>
            <span class="text-[11px] text-slate-500 font-mono hidden sm:inline">İpucu: Klavyede ⬅️ ve ➡️ yön tuşlarıyla sayfa çevirebilirsiniz</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-16">
            <button id="btn-prev" onclick="prevChapter()" class="text-left p-5 rounded-2xl bg-slate-900/70 hover:bg-slate-900 border border-white/10 hover:border-cyan-500/40 transition group">
              <div class="text-xs text-slate-400 mb-1 group-hover:text-cyan-400">← Önceki Sayfa</div>
              <div id="prev-title" class="text-sm font-bold text-slate-200 truncate">-</div>
            </button>

            <button id="btn-next" onclick="nextChapter()" class="text-right p-5 rounded-2xl bg-slate-900/70 hover:bg-slate-900 border border-white/10 hover:border-emerald-500/40 transition group">
              <div class="text-xs text-slate-400 mb-1 group-hover:text-emerald-400">Sonraki Sayfa →</div>
              <div id="next-title" class="text-sm font-bold text-slate-200 truncate">-</div>
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- SAĞ BÖLÜM NOTLARI ÇEKMECESİ -->
    <aside id="notes-drawer" class="hidden w-80 bg-slate-950 border-l border-white/10 p-5 flex-col shrink-0 z-20">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-bold text-amber-300 flex items-center gap-2">📝 Bölüm Notlarım</h3>
        <button onclick="toggleNotesDrawer()" class="text-slate-400 hover:text-white text-sm">✕</button>
      </div>
      <p id="notes-chapter-label" class="text-xs text-slate-400 mb-3 truncate"></p>
      <textarea id="chapter-note-input" oninput="autoSaveNote()" class="flex-1 w-full bg-slate-900 border border-white/10 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-amber-500 resize-none" placeholder="Bu bölümde aklınıza gelen fikirleri, şirket senaryolarınızı veya sorularınızı buraya not alın..."></textarea>
      <div class="mt-3 flex items-center justify-between">
        <span id="note-save-msg" class="text-[11px] text-slate-500">Tarayıcı hafızasında kalıcıdır</span>
        <button onclick="saveCurrentNote()" class="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold transition">
          💾 Kaydet
        </button>
      </div>
      <div class="mt-3 pt-3 border-t border-white/10 flex items-center justify-between gap-2">
        <button onclick="exportNotesJson()" class="flex-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/10 text-[11px] text-slate-300 font-semibold transition">
          📥 Yedek İndir (.json)
        </button>
        <label class="flex-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/10 text-[11px] text-slate-300 font-semibold transition text-center cursor-pointer">
          📤 Yedek Yükle
          <input type="file" accept=".json" onchange="importNotesJson(event)" class="hidden">
        </label>
      </div>
    </aside>

  </div>

  <script>
    const CHAPTERS = __CHAPTERS_JSON__;
    const PDF_BASE64 = "__PDF_BASE64__";
    const COCKPIT_URL = "__COCKPIT_URL__";

    function safeGetStorage(key, fallback) {
      try {
        const val = localStorage.getItem(key);
        return val !== null ? val : fallback;
      } catch (e) {
        return fallback;
      }
    }

    function safeSetStorage(key, val) {
      try {
        localStorage.setItem(key, val);
      } catch (e) {}
    }

    let currentIdx = parseInt(safeGetStorage('lg_book_chapter', '0'), 10);
    if (isNaN(currentIdx) || currentIdx < 0 || currentIdx >= CHAPTERS.length) currentIdx = 0;

    let completedSet = new Set();
    try {
      completedSet = new Set(JSON.parse(safeGetStorage('lg_book_completed', '[]')));
    } catch (e) {}

    let bookNotes = {};
    try {
      bookNotes = JSON.parse(safeGetStorage('lg_book_notes', '{}')) || {};
    } catch (e) {
      bookNotes = {};
    }

    let fontSize = parseInt(safeGetStorage('lg_book_fontsize', '18'), 10);
    document.documentElement.style.setProperty('--reader-font-size', fontSize + 'px');

    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
      fontFamily: 'Inter, sans-serif'
    });

    function transformAlerts(html) {
      const types = {
        'IMPORTANT': { icon: '💡', title: 'Önemli Mimari İlke', cls: 'bg-purple-950/40 border border-purple-500/35 text-purple-100', head: 'text-purple-300' },
        'TIP':       { icon: '🚀', title: 'Pratik İpucu',       cls: 'bg-emerald-950/40 border border-emerald-500/35 text-emerald-100', head: 'text-emerald-300' },
        'WARNING':   { icon: '⚠️', title: 'Kritik Uyarı',       cls: 'bg-amber-950/40 border border-amber-500/35 text-amber-100', head: 'text-amber-300' },
        'NOTE':      { icon: '📌', title: 'Derinleşme Notu',    cls: 'bg-sky-950/40 border border-sky-500/35 text-sky-100', head: 'text-sky-300' },
        'CAUTION':   { icon: '🛑', title: 'Dikkat',             cls: 'bg-red-950/40 border border-red-500/35 text-red-100', head: 'text-red-300' }
      };

      return html.replace(/<blockquote>\s*<p>\[!(IMPORTANT|TIP|WARNING|NOTE|CAUTION)\]\s*([\s\S]*?)<\/blockquote>/g, (m, kind, body) => {
        const cfg = types[kind] || types['NOTE'];
        return `<div class="callout-card ${cfg.cls}">
          <div class="font-bold mb-1.5 flex items-center gap-2 ${cfg.head}"><span>${cfg.icon}</span><span>${cfg.title}</span></div>
          <div><p>${body}</div>
        </div>`;
      });
    }

    async function renderChapter(idx) {
      currentIdx = idx;
      safeSetStorage('lg_book_chapter', String(idx));
      const ch = CHAPTERS[idx];

      document.getElementById('chapter-part-badge').textContent = ch.part;
      document.getElementById('page-counter').textContent = `Sayfa ${idx + 1} / ${CHAPTERS.length}`;
      document.getElementById('read-badge').textContent = `⏱️ ~${ch.read_min} dk okuma`;
      document.getElementById('progress-label').textContent = `Sayfa: ${idx + 1} / ${CHAPTERS.length}`;
      document.getElementById('completed-label').textContent = `${completedSet.size} tamamlandı`;
      document.getElementById('top-progress').style.width = `${((idx + 1) / CHAPTERS.length) * 100}%`;

      const mermaidBlocks = [];
      let md = ch.markdown;
      if (idx === 0) {
        md = md.replace(/## 📑 İçindekiler[\s\S]*?---\n/, '');
      }

      md = md.replace(/```mermaid\n([\s\S]*?)```/g, (_, code) => {
        const token = `@@MERMAID_${mermaidBlocks.length}@@`;
        mermaidBlocks.push(code.trim());
        return token;
      });

      let html = marked.parse(md);
      html = transformAlerts(html);

      mermaidBlocks.forEach((code, i) => {
        const safe = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        html = html.replace(`<p>@@MERMAID_${i}@@</p>`, `<div class="mermaid-box"><pre class="mermaid">${safe}</pre></div>`);
        html = html.replace(`@@MERMAID_${i}@@`, `<div class="mermaid-box"><pre class="mermaid">${safe}</pre></div>`);
      });

      const container = document.getElementById('chapter-content');
      container.innerHTML = html;

      container.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));

      const mNodes = container.querySelectorAll('.mermaid');
      if (mNodes.length > 0) {
        try {
          await mermaid.run({ nodes: mNodes });
        } catch (e) {
          console.warn('Mermaid render warning:', e);
        }
      }

      const btnPrev = document.getElementById('btn-prev');
      const btnNext = document.getElementById('btn-next');
      if (idx > 0) {
        btnPrev.disabled = false;
        btnPrev.classList.remove('opacity-40', 'pointer-events-none');
        document.getElementById('prev-title').textContent = CHAPTERS[idx - 1].short_title;
      } else {
        btnPrev.disabled = true;
        btnPrev.classList.add('opacity-40', 'pointer-events-none');
        document.getElementById('prev-title').textContent = 'Kitap Başlangıcı';
      }

      if (idx < CHAPTERS.length - 1) {
        btnNext.disabled = false;
        btnNext.classList.remove('opacity-40', 'pointer-events-none');
        document.getElementById('next-title').textContent = CHAPTERS[idx + 1].short_title;
      } else {
        btnNext.disabled = true;
        btnNext.classList.add('opacity-40', 'pointer-events-none');
        document.getElementById('next-title').textContent = 'Kitap Sonu 🎉';
      }

      const btnComp = document.getElementById('btn-complete');
      if (completedSet.has(idx)) {
        btnComp.innerHTML = '<span>✅</span> <span>Tamamlandı (Geri Almak İçin Tıkla)</span>';
      } else {
        btnComp.innerHTML = '<span>✓</span> <span>Bu Bölümü Tamamladım Olarak İşaretle</span>';
      }

      document.getElementById('notes-chapter-label').textContent = ch.short_title;
      document.getElementById('chapter-note-input').value = bookNotes[String(idx)] || '';

      renderTOC(document.getElementById('search-input').value);
      document.getElementById('reader-scroll').scrollTop = 0;
    }

    function renderTOC(query = '') {
      const toc = document.getElementById('toc-list');
      const q = query.trim().toLowerCase();
      const grouped = {};

      CHAPTERS.forEach(ch => {
        if (q && !ch.title.toLowerCase().includes(q) && !ch.markdown.toLowerCase().includes(q)) {
          return;
        }
        if (!grouped[ch.part]) grouped[ch.part] = [];
        grouped[ch.part].push(ch);
      });

      let html = '';
      Object.keys(grouped).forEach(part => {
        html += `<div>
          <div class="px-2.5 mb-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-500">${part}</div>
          <div class="space-y-1">`;
        grouped[part].forEach(ch => {
          const active = ch.id === currentIdx;
          const done = completedSet.has(ch.id);
          const cls = active
            ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 font-semibold'
            : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5';
          html += `<button onclick="renderChapter(${ch.id})" class="w-full text-left px-3 py-2 rounded-xl border text-xs transition flex items-start justify-between gap-2 ${cls}">
            <span class="leading-snug">${ch.short_title}</span>
            <span class="shrink-0 text-[11px]">${done ? '✅' : ''}</span>
          </button>`;
        });
        html += `</div></div>`;
      });

      toc.innerHTML = html || '<p class="text-xs text-slate-500 p-3">Eşleşen bölüm bulunamadı.</p>';
    }

    function filterTOC() {
      renderTOC(document.getElementById('search-input').value);
    }

    function prevChapter() {
      if (currentIdx > 0) renderChapter(currentIdx - 1);
    }

    function nextChapter() {
      if (currentIdx < CHAPTERS.length - 1) renderChapter(currentIdx + 1);
    }

    function markCurrentCompleted() {
      if (completedSet.has(currentIdx)) {
        completedSet.delete(currentIdx);
      } else {
        completedSet.add(currentIdx);
      }
      safeSetStorage('lg_book_completed', JSON.stringify(Array.from(completedSet)));
      renderChapter(currentIdx);
    }

    function changeFontSize(delta) {
      if (delta === 0) fontSize = 18;
      else fontSize = Math.min(24, Math.max(14, fontSize + delta));
      safeSetStorage('lg_book_fontsize', String(fontSize));
      document.documentElement.style.setProperty('--reader-font-size', fontSize + 'px');
    }

    function toggleSidebar() {
      document.getElementById('sidebar').classList.toggle('hidden');
    }

    function toggleNotesDrawer() {
      const dr = document.getElementById('notes-drawer');
      dr.classList.toggle('hidden');
      dr.classList.toggle('flex');
    }

    function autoSaveNote() {
      bookNotes[String(currentIdx)] = document.getElementById('chapter-note-input').value;
      safeSetStorage('lg_book_notes', JSON.stringify(bookNotes));
    }

    function saveCurrentNote() {
      autoSaveNote();
      const msg = document.getElementById('note-save-msg');
      msg.textContent = '✔ Tarayıcıya kaydedildi!';
      msg.className = 'text-[11px] text-emerald-400 font-semibold';
      setTimeout(() => {
        msg.textContent = 'Tarayıcı hafızasında kalıcıdır';
        msg.className = 'text-[11px] text-slate-500';
      }, 2500);
    }

    function exportNotesJson() {
      const dataStr = JSON.stringify(bookNotes, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'langgraph_kitap_notlarim.json';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }

    function importNotesJson(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target.result);
          if (imported && typeof imported === 'object') {
            bookNotes = Object.assign({}, bookNotes, imported);
            safeSetStorage('lg_book_notes', JSON.stringify(bookNotes));
            document.getElementById('chapter-note-input').value = bookNotes[String(currentIdx)] || '';
            saveCurrentNote();
          }
        } catch (err) {
          alert('Geçersiz JSON not yedeği dosyası.');
        }
      };
      reader.readAsText(file, 'utf-8');
    }

    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
      if (e.key === 'ArrowRight') nextChapter();
      if (e.key === 'ArrowLeft') prevChapter();
    });

    window.addEventListener('DOMContentLoaded', async () => {
      if (COCKPIT_URL) {
        const backBtn = document.getElementById('cockpit-back-btn');
        backBtn.href = COCKPIT_URL;
        backBtn.classList.remove('hidden');
        backBtn.classList.add('flex');
      }

      if (PDF_BASE64) {
        try {
          const bin = atob(PDF_BASE64);
          const bytes = new Uint8Array(bin.length);
          for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
          const blob = new Blob([bytes], { type: 'application/pdf' });
          const blobUrl = URL.createObjectURL(blob);
          const pdfBtn = document.getElementById('pdf-download-btn');
          pdfBtn.href = blobUrl;
        } catch (e) {
          console.warn('PDF blob hazirlama uyarisi:', e);
        }
      }

      await renderChapter(currentIdx);
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# YAYIN KALİTESİNDE PDF BASKI ŞABLONU (/print - yalnızca isteğe bağlı PDF üretimi için)
# ==============================================================================
PRINT_HTML = r"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>Zincirlerden Otonom Şirketlere — LangGraph ve Ajan Mimarisi</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;0,7..72,700;1,7..72,400&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4;
      margin: 20mm 18mm 20mm 18mm;
    }
    body {
      font-family: 'Literata', Georgia, serif;
      font-size: 11pt;
      line-height: 1.68;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }
    .cover-page {
      height: 245mm;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 20mm;
      background: linear-gradient(145deg, #0b1120 0%, #0f172a 60%, #064e3b 100%);
      color: #f8fafc;
      border-radius: 16px;
      box-sizing: border-box;
      page-break-after: always;
    }
    .cover-badge {
      display: inline-block;
      font-family: 'JetBrains Mono', monospace;
      font-size: 9pt;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #34d399;
      border: 1px solid rgba(52, 211, 153, 0.4);
      padding: 6px 14px;
      border-radius: 999px;
      margin-bottom: 24px;
      width: fit-content;
    }
    .cover-title {
      font-family: 'Inter', sans-serif;
      font-size: 28pt;
      font-weight: 800;
      line-height: 1.18;
      margin: 0 0 18px 0;
      color: #ffffff;
    }
    .cover-sub {
      font-family: 'Inter', sans-serif;
      font-size: 12.5pt;
      line-height: 1.55;
      color: #cbd5e1;
      margin-bottom: 40px;
    }
    .cover-footer {
      margin-top: auto;
      padding-top: 20px;
      border-top: 1px solid rgba(255,255,255,0.15);
      font-family: 'Inter', sans-serif;
      font-size: 9.5pt;
      color: #94a3b8;
      display: flex;
      justify-content: space-between;
    }
    .chapter-block { page-break-before: always; }
    .part-kicker {
      font-family: 'Inter', sans-serif;
      font-size: 8.5pt;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #059669;
      margin-bottom: 4px;
    }
    h1, h2, h3, h4 {
      font-family: 'Inter', sans-serif;
      color: #0f172a;
      page-break-after: avoid;
    }
    h2 {
      font-size: 17pt;
      font-weight: 800;
      margin-top: 0;
      padding-bottom: 8px;
      border-bottom: 2px solid #e2e8f0;
    }
    h3 { font-size: 13pt; font-weight: 700; color: #0f766e; margin-top: 20px; }
    h4 { font-size: 11pt; font-weight: 700; color: #0369a1; margin-top: 14px; }
    p { margin: 0 0 10px 0; }
    code:not(pre code) {
      font-family: 'JetBrains Mono', monospace;
      font-size: 9pt;
      background: #f1f5f9;
      color: #0f766e;
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid #e2e8f0;
    }
    pre {
      font-family: 'JetBrains Mono', monospace;
      font-size: 8.8pt;
      line-height: 1.5;
      background: #0f172a;
      color: #f8fafc;
      padding: 12px 14px;
      border-radius: 10px;
      overflow-x: auto;
      page-break-inside: avoid;
      margin: 12px 0;
    }
    pre code { background: transparent; color: inherit; border: none; padding: 0; }
    blockquote, .print-callout {
      background: #f8fafc;
      border-left: 4px solid #0ea5e9;
      padding: 10px 14px;
      border-radius: 0 8px 8px 0;
      margin: 12px 0;
      page-break-inside: avoid;
      font-family: 'Inter', sans-serif;
      font-size: 9.8pt;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-family: 'Inter', sans-serif;
      font-size: 9pt;
      page-break-inside: avoid;
    }
    th { background: #0f172a; color: #ffffff; text-align: left; padding: 8px 10px; }
    td { border: 1px solid #cbd5e1; padding: 7px 10px; vertical-align: top; }
    tr:nth-child(even) td { background: #f8fafc; }
    .mermaid-print {
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px;
      margin: 14px 0;
      text-align: center;
      page-break-inside: avoid;
      background: #fcfdff;
    }
    hr { border: 0; border-top: 1px solid #e2e8f0; margin: 16px 0; }
  </style>
</head>
<body>
  <div class="cover-page">
    <div class="cover-badge">VIBE CODER &bull; BAŞMİMAR EDİSYONU</div>
    <h1 class="cover-title">Zincirlerden Otonom Şirketlere:<br>İnsan Dilinde LangGraph ve Ajan Mimarisi</h1>
    <div class="cover-sub">
      Kod hamallığı yapmadan Yapay Zeka Ajanlarını, LangGraph Durum Makinelerini, Kalıcılığı, Human-in-the-Loop Güvenliğini, Çoklu Ajan Ekiplerini ve LangSmith Gözlemlenebilirliğini Uçtan Uca Anlama Rehberi.
    </div>
    <div class="cover-footer">
      <span>LangGraph_Course Canlı Proje Serisi</span>
      <span>12 Bölüm + Mimari Karar Ağacı &amp; Sözlük</span>
    </div>
  </div>

  <div id="print-root"></div>

  <script>
    const CHAPTERS = __CHAPTERS_JSON__;
    mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'loose' });

    window.addEventListener('DOMContentLoaded', async () => {
      const root = document.getElementById('print-root');
      let fullHtml = '';
      const mermaidBlocks = [];

      CHAPTERS.forEach((ch, idx) => {
        let md = ch.markdown;
        if (idx === 0) {
          md = md.replace(/^# .*\n+/, '').replace(/^\*\*Alt Başlık:\*\*.*\n+/, '');
        }
        md = md.replace(/```mermaid\n([\s\S]*?)```/g, (_, code) => {
          const tok = `@@PMERMAID_${mermaidBlocks.length}@@`;
          mermaidBlocks.push(code.trim());
          return tok;
        });

        let html = marked.parse(md);
        html = html.replace(/<blockquote>\s*<p>\[!(IMPORTANT|TIP|WARNING|NOTE|CAUTION)\]\s*([\s\S]*?)<\/blockquote>/g,
          (_, kind, body) => `<div class="print-callout"><strong>[${kind}]</strong> <p>${body}</div>`
        );

        fullHtml += `<section class="${idx === 0 ? '' : 'chapter-block'}">
          <div class="part-kicker">${ch.part}</div>
          ${html}
        </section>`;
      });

      mermaidBlocks.forEach((code, i) => {
        const safe = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        fullHtml = fullHtml.replace(`<p>@@PMERMAID_${i}@@</p>`, `<div class="mermaid-print"><pre class="mermaid">${safe}</pre></div>`);
        fullHtml = fullHtml.replace(`@@PMERMAID_${i}@@`, `<div class="mermaid-print"><pre class="mermaid">${safe}</pre></div>`);
      });

      root.innerHTML = fullHtml;
      const nodes = root.querySelectorAll('.mermaid');
      if (nodes.length > 0) {
        try { await mermaid.run({ nodes }); } catch (e) {}
      }
      document.body.setAttribute('data-ready', 'true');
    });
  </script>
</body>
</html>
"""


def render_standalone_ebook_html(
    pdf_href: str = "./LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.pdf",
    pdf_base64: str = "",
    cockpit_url: str = "",
) -> str:
    """
    Hiçbir Python sunucusuna (daemon) ihtiyaç duymayan %100 bağımsız HTML üretir.
    Hem statik LANGGRAPH_E_KITAP.html dosyası hem de Streamlit harici kitap sayfası
    tarafından tek kaynak olarak kullanılır.
    """
    html = READER_HTML.replace("__CHAPTERS_JSON__", get_chapters_json_str())
    html = html.replace("__PDF_HREF__", pdf_href)
    html = html.replace("__PDF_BASE64__", pdf_base64)
    html = html.replace("__COCKPIT_URL__", cockpit_url)
    return html


def build_static_ebook(output_path: str = STATIC_HTML_PATH) -> str:
    """Statik sunucusuz e-kitap HTML dosyasını diske yazar ve yolunu döndürür."""
    html = render_standalone_ebook_html(
        pdf_href="./LANGGRAPH_VE_OTONOM_AJANLAR_KITABI.pdf",
        pdf_base64="",
        cockpit_url="",
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


class PrintServerHandler(BaseHTTPRequestHandler):
    """Yalnızca --print-server ile PDF yeniden üretmek istendiğinde geçici kullanılır."""
    def log_message(self, format, *args):
        return

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/print":
            html = PRINT_HTML.replace("__CHAPTERS_JSON__", get_chapters_json_str())
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            html = render_standalone_ebook_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)


if __name__ == "__main__":
    args = set(sys.argv[1:])

    if "--print-server" in args:
        port = 8090
        server = ThreadingHTTPServer(("127.0.0.1", port), PrintServerHandler)
        print(f"Geçici PDF baskı şablon sunucusu: http://127.0.0.1:{port}/print")
        server.serve_forever()
    else:
        out_file = build_static_ebook(STATIC_HTML_PATH)
        print(f"✅ Sunucusuz E-Kitap başarıyla derlendi: {out_file}")
        if "--open" in args:
            webbrowser.open(f"file:///{out_file.replace(os.sep, '/')}")
