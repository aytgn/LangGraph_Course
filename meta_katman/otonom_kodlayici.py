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
# 2. Pydantic Yapılandırılmış Çıktı Şemaları
# ==============================================================================
class CodeGenerationOutput(BaseModel):
    """Mühendisin ürettiği tam ve eksiksiz kod çıktısı."""
    full_code: str = Field(description="Dosyanın tüm içeriğini içeren, eksiksiz, çalışan, hiçbir kısmı atlanmamış Python veya CSS/HTML kodu.")
    change_summary: str = Field(description="Nelerin değiştirildiğini, eklenen/silinen ana bileşenleri açıklayan 2-3 cümlelik teknik özet.")


class CodebaseScanOutput(BaseModel):
    """Kullanıcının teknik olmayan direktifini inceleyip etkilenecek dosyaları ve planı belirleyen Baş Mimar çıktısı."""
    relevant_files: List[str] = Field(description="Bu direktifi eksiksiz yerine getirmek için değiştirilmesi gereken dosya yollarının listesi.")
    architectural_plan: str = Field(description="Kullanıcıya yönelik, hangi dosyada nelerin değiştirileceğini anlatan sade yönetici özeti.")
    estimated_impact: str = Field(description="Değişikliğin sistem üzerindeki etkisi (örn: 'Yüksek - Tüm UI teması ve CSS yenileniyor').")


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


# ==============================================================================
# 6. Çoklu Dosya ve Kod Tabanı Genelinde Otonom Orkestrasyon (Codebase-Wide)
# ==============================================================================

def discover_relevant_files_for_task(instruction: str) -> CodebaseScanOutput:
    """
    Kullanıcı kodlama bilmese ve dosya adı vermese bile; verilen direktifi
    inceleyerek hangi proje dosyalarının değiştirilmesi gerektiğini otonom tespit eder.
    """
    all_files = CodeInspector.list_project_files()
    
    prompt = (
        "Sen Baş Yazılım Mimarı ve Otonom Proje Orkestratörüsün (Principal Software Architect).\n"
        "Kullanıcı kodlama ve dosya isimlerinden anlamayan bir Yönetim Kurulu Başkanıdır.\n"
        f"Kullanıcının Direktifi: '{instruction}'\n\n"
        f"Projedeki Düzenlenebilir Mevcut Dosyalar:\n{all_files}\n\n"
        "GÖREVİN:\n"
        "1. Kullanıcının bu hedefini eksiksiz gerçekleştirmek için hangi dosya veya dosyaların "
        "değiştirilmesi gerektiğini belirle. (Örn: Arayüz/tema/CSS isteği ise 'yonetici_masasi.py' ve "
        "ilgili arayüz sayfalarını seç; arka plan mantığı ise motor dosyalarını seç).\n"
        "2. En az 1, en fazla 4 en kritik dosyayı seç.\n"
        "3. Kullanıcıya sade, teknik jargona boğulmamış bir mimari plan hazırla."
    )

    llm = get_gemini_llm(temperature=0.1).with_structured_output(CodebaseScanOutput)
    scan_result: CodebaseScanOutput = llm.invoke(prompt)

    # Güvenlik doğrulaması: Var olmayan dosya üretilmişse temizle
    valid_selected = [f for f in scan_result.relevant_files if f in all_files]
    if not valid_selected:
        # Fallback: Eğer model eşleştiremediyse ana arayüz dosyasını seç
        valid_selected = ["yonetici_masasi.py"] if "yonetici_masasi.py" in all_files else [all_files[0]]
    scan_result.relevant_files = valid_selected

    return scan_result


def plan_and_generate_codebase_patch(instruction: str, specific_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Tüm kod tabanında (Codebase-Wide) çoklu dosya analiz ve patch döngüsü:
    1. İlgili dosyaları otomatik tespit eder (kullanıcı dosya seçmediyse).
    2. Her dosya için AST doğrulamalı kod üretir ve self-healing uygular.
    3. Tüm dosyaların diff'lerini tek bir kurumsal raporda toplar.
    DİKKAT: Henüz diske yazmaz! Kullanıcı onayı için hazır bekletir.
    """
    if specific_files and len(specific_files) > 0:
        target_files = specific_files
        plan_desc = f"Seçilen {len(specific_files)} adet dosya üzerinde cerrahi refactoring uygulanıyor."
        impact = "Belirli dosyalara hedeflenmiş müdahale."
    else:
        scan_result = discover_relevant_files_for_task(instruction)
        target_files = scan_result.relevant_files
        plan_desc = scan_result.architectural_plan
        impact = scan_result.estimated_impact

    file_patches = []
    all_success = True

    for fpath in target_files:
        try:
            patch_data = plan_and_generate_code_patch(instruction, fpath)
            file_patches.append(patch_data)
            if not patch_data["syntax_valid"]:
                all_success = False
        except Exception as e:
            file_patches.append({
                "success": False,
                "target_file": fpath,
                "summary": f"İşlem sırasında hata oluştu: {str(e)}",
                "diff": "",
                "proposed_content": "",
                "original_content": "",
                "syntax_valid": False,
                "syntax_error": str(e),
                "iterations_taken": 0
            })
            all_success = False

    return {
        "success": all_success,
        "instruction": instruction,
        "architectural_plan": plan_desc,
        "estimated_impact": impact,
        "target_files": target_files,
        "file_patches": file_patches,
        "total_files": len(file_patches)
    }


def execute_approved_codebase_patch(codebase_patch_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Onaylanan çoklu dosya değişikliğini atomik olarak diske yazar.
    Tüm dosyalar için toplu (batch) snapshot alır; herhangi bir hata durumunda
    tüm dosyaları anında eski haline geri döndürür.
    """
    patches = codebase_patch_result.get("file_patches", [])
    target_paths = [p["target_file"] for p in patches if p.get("syntax_valid")]

    if not target_paths:
        raise ValueError("Diske yazılacak geçerli bir kod yaması bulunamadı.")

    # 1. Toplu Snapshot Al
    batch_id, backups = CodeSnapshotManager.create_batch_snapshot(target_paths)

    written_files = []
    try:
        for p in patches:
            if p.get("syntax_valid") and p.get("proposed_content"):
                CodeQualityEngine.apply_atomic_write(
                    target_path=p["target_file"],
                    new_content=p["proposed_content"],
                    take_backup=False  # Toplu snapshot zaten alındı
                )
                written_files.append(p["target_file"])
    except Exception as e:
        # Hata anında tüm grubu geri al (Toplu Rollback)
        CodeSnapshotManager.restore_batch_snapshot(batch_id)
        raise IOError(f"Yazım sırasında hata oluştu! Tüm değişiklikler geri alındı. Hata: {e}")

    return {
        "status": "SUCCESS",
        "batch_id": batch_id,
        "written_files": written_files,
        "backup_count": len(backups)
    }


def rollback_codebase_batch(batch_id: str) -> List[str]:
    """Toplu snapshot paketini geri yükler."""
    return CodeSnapshotManager.restore_batch_snapshot(batch_id)

