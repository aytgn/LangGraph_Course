"""
================================================================================
🤖 OTONOM YAZILIM MÜHENDİSİ (SWE-AGENT LANGGRAPH GRAFI)
================================================================================
Devin ve Claude Engineer standartlarında;
- Kod tabanını analiz eden Mimar (Architect),
- Kodu eksiksiz üreten Kıdemli Mühendis (Senior Developer),
- AST ve derleme denetimi yapan Doğrulayıcı (Verifier),
- Sentaks hatası anında devreye giren Kendi Kendini Onarma (Self-Healing) döngüsü.
================================================================================
"""

import os
import sys
import re
from typing import Optional, Dict, Any, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END

# Model fabrikası ve kod araçları
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_factory import get_gemini_llm
from meta_katman.kod_araclari import (
    WorkspaceSecurity,
    CodeSnapshotManager,
    CodeQualityEngine,
    CodeInspector
)


# ==============================================================================
# 1. SWE-Agent Graf Durumu (State)
# ==============================================================================
class SWEState(TypedDict):
    instruction: str              # Kullanıcı emri ("CSS'i Linear tarzına çevir")
    target_file: str              # İncelenecek ve değiştirilecek dosya
    original_content: str         # Orijinal dosya içeriği
    proposed_content: str         # Üretilen yeni dosya içeriği
    diff: str                     # Renkli unified diff
    syntax_valid: bool            # Sözdizimi geçerli mi?
    syntax_error: Optional[str]   # Hata detayları (varsa)
    iteration: int                # Onarma deneme sayısı
    summary: str                  # Yapılan değişikliğin teknik özeti
    status: str                   # "ANALYZED", "GENERATED", "SYNTAX_PASSED", "SELF_HEALED", "FAILED"


# ==============================================================================
# 2. Pydantic Yapılandırılmış Çıktı Şeması
# ==============================================================================
class CodeGenerationOutput(BaseModel):
    """Mühendisin ürettiği tam ve eksiksiz kod çıktısı."""
    full_code: str = Field(description="Dosyanın tüm içeriğini içeren, eksiksiz, çalışan, hiçbir kısmı atlanmamış Python veya CSS/HTML kodu.")
    change_summary: str = Field(description="Nelerin değiştirildiğini, eklenen/silinen ana bileşenleri açıklayan 2-3 cümlelik teknik özet.")


# ==============================================================================
# 3. Graf Düğümleri (Nodes)
# ==============================================================================

def analyze_node(state: SWEState) -> Dict[str, Any]:
    """1. Adım: Hedef dosyayı okur ve orijinal içeriği duruma kaydeder."""
    target_file = state["target_file"]
    content, total_lines = CodeInspector.read_workspace_file(target_file)
    
    return {
        "original_content": content,
        "iteration": 0,
        "status": "ANALYZED"
    }


def generate_patch_node(state: SWEState) -> Dict[str, Any]:
    """2. Adım: Kıdemli mühendis LLM'i dosyayı ve kullanıcı emrini inceleyip yeni kodu üretir."""
    target_file = state["target_file"]
    instruction = state["instruction"]
    orig_code = state["original_content"]
    iteration = state.get("iteration", 0)
    syntax_err = state.get("syntax_error")

    system_prompt = (
        "Sen Dünya Çapında Kıdemli bir Otonom Yazılım Mühendisisin (Senior SWE-Agent / Staff Software Engineer).\n"
        "Görevin: Verilen kaynak kodu ve kullanıcının direktifini analiz ederek, hedeflenen dosyanın "
        "TAM ve EKSİKSİZ yeni halini üretmektir.\n\n"
        "ÇOK KRİTİK KURALLAR:\n"
        "1. KODDA ASLA YARIM BIRAKMA, 'burası aynı kalacak', '...', '# kodun geri kalanı' GİBİ KISALTMALAR YAPMA! "
        "Dosyayı 1. satırından son satırına kadar eksiksiz ve çalışır vaziyette yaz.\n"
        "2. Python dosyalarında sözdizimi ve girintileme (indentation) kurallarına %100 uy. "
        "Eksik parantez veya kapanmamış tırnak bırakma.\n"
        "3. Mevcut iş mantığını ve fonksiyonellikleri bozma; sadece istenen iyileştirmeyi/eklemeyi yap."
    )

    if syntax_err and iteration > 0:
        # Self-Healing: Hatayı açıkça gösterip tamir etmesini iste
        user_prompt = (
            f"DİKKAT: Bir önceki denemende sözdizimi hatası (SyntaxError) oluştu!\n"
            f"--- HATA DETAYI ---\n{syntax_err}\n\n"
            f"KULLANICI DİREKTİFİ: {instruction}\n"
            f"HEDEF DOSYA: {target_file}\n\n"
            f"Lütfen yukarıdaki hatayı dikkatle incele, eksik parantez/girintiyi düzelt ve dosyanın "
            f"HATASIZ ve EKSİKSİZ TAM KODUNU tekrar üret."
        )
    else:
        user_prompt = (
            f"KULLANICI DİREKTİFİ:\n{instruction}\n\n"
            f"HEDEF DOSYA: {target_file}\n"
            f"--- MEVCUT DOSYA İÇERİĞİ ---\n{orig_code}\n\n"
            f"Görevin: Direktife göre bu dosyayı baştan sona eksiksiz olarak güncelle ve 'full_code' olarak teslim et."
        )

    llm = get_gemini_llm(temperature=0.1).with_structured_output(CodeGenerationOutput)
    result: CodeGenerationOutput = llm.invoke(f"{system_prompt}\n\n{user_prompt}")

    new_code = result.full_code.strip()
    
    # Eğer model kodu markdown kod blokları içine sarmışsa temizle
    if new_code.startswith("```python"):
        new_code = new_code[len("```python"):].strip()
    elif new_code.startswith("```"):
        new_code = new_code[len("```"):].strip()
    if new_code.endswith("```"):
        new_code = new_code[:-3].strip()

    return {
        "proposed_content": new_code,
        "summary": result.change_summary,
        "status": "GENERATED"
    }


def verify_syntax_node(state: SWEState) -> Dict[str, Any]:
    """3. Adım: Üretilen kodun AST ve derleme geçerliliğini denetler ve Diff üretir."""
    target_file = state["target_file"]
    new_code = state["proposed_content"]
    orig_code = state["original_content"]

    diff_text = CodeQualityEngine.generate_unified_diff(
        old_content=orig_code,
        new_content=new_code,
        file_name=os.path.basename(target_file)
    )

    # Yalnızca .py dosyalarında AST sözdizimi denetlenir
    if target_file.endswith(".py"):
        is_valid, err = CodeQualityEngine.verify_python_syntax(new_code)
        if is_valid:
            return {
                "diff": diff_text,
                "syntax_valid": True,
                "syntax_error": None,
                "status": "SYNTAX_PASSED"
            }
        else:
            return {
                "diff": diff_text,
                "syntax_valid": False,
                "syntax_error": err,
                "iteration": state["iteration"] + 1,
                "status": "SYNTAX_ERROR"
            }
    else:
        # CSS, JSON, Markdown vb. dosyalar için doğrudan geçerli
        return {
            "diff": diff_text,
            "syntax_valid": True,
            "syntax_error": None,
            "status": "SYNTAX_PASSED"
        }


def route_after_verification(state: SWEState) -> str:
    """Doğrulama sonucuna göre yönlendirir (Self-Healing döngüsü)."""
    if state["syntax_valid"]:
        return END
    
    # 3 defaya kadar kendi kendini tamir etmeyi dener
    if state["iteration"] <= 3:
        return "generate_patch_node"
    
    return END


# ==============================================================================
# 4. LangGraph Grafının İnşası ve Derlenmesi
# ==============================================================================
builder = StateGraph(SWEState)

builder.add_node("analyze_node", analyze_node)
builder.add_node("generate_patch_node", generate_patch_node)
builder.add_node("verify_syntax_node", verify_syntax_node)

builder.add_edge(START, "analyze_node")
builder.add_edge("analyze_node", "generate_patch_node")
builder.add_edge("generate_patch_node", "verify_syntax_node")

builder.add_conditional_edges(
    "verify_syntax_node",
    route_after_verification,
    {
        "generate_patch_node": "generate_patch_node",
        END: END
    }
)

swe_app = builder.compile()


# ==============================================================================
# 5. Dışarıya Açık Yüksek Seviye API Fonksiyonları
# ==============================================================================

def plan_and_generate_code_patch(instruction: str, target_file: str) -> Dict[str, Any]:
    """
    Kullanıcı direktifine göre dosyayı analiz eder, kodu üretir, sözdizimini doğrular
    ve renkli Diff üretir. DİKKAT: Henüz diske yazmaz! Kullanıcı onayı için hazır bekletir.
    """
    # Güvenlik ön kontrolü
    WorkspaceSecurity.validate_path(target_file)

    initial_state = {
        "instruction": instruction,
        "target_file": target_file,
        "original_content": "",
        "proposed_content": "",
        "diff": "",
        "syntax_valid": False,
        "syntax_error": None,
        "iteration": 0,
        "summary": "",
        "status": "STARTING"
    }

    final_state = swe_app.invoke(initial_state)

    return {
        "success": final_state["syntax_valid"],
        "target_file": target_file,
        "summary": final_state["summary"],
        "diff": final_state["diff"],
        "proposed_content": final_state["proposed_content"],
        "original_content": final_state["original_content"],
        "syntax_valid": final_state["syntax_valid"],
        "syntax_error": final_state["syntax_error"],
        "iterations_taken": final_state["iteration"]
    }


def execute_approved_code_patch(target_file: str, new_content: str) -> Dict[str, Any]:
    """
    Kullanıcının onayladığı kodu atomik olarak diske yazar ve otomatik yedek alır.
    """
    return CodeQualityEngine.apply_atomic_write(
        target_path=target_file,
        new_content=new_content,
        take_backup=True
    )


def rollback_code_change(target_file: str, snapshot_path: Optional[str] = None) -> bool:
    """Hedef dosyadaki değişikliği geri alır."""
    if snapshot_path:
        return CodeSnapshotManager.restore_snapshot(snapshot_path, target_file)
    
    # En son alınan yedeği bul
    snaps = CodeSnapshotManager.list_snapshots()
    base_name = os.path.basename(target_file)
    matching = [s for s in snaps if base_name in s["filename"]]
    if not matching:
        raise FileNotFoundError(f"'{target_file}' için geri yüklenecek bir yedek (.bak) bulunamadı.")
    
    latest_snapshot = matching[0]["path"]
    return CodeSnapshotManager.restore_snapshot(latest_snapshot, target_file)
