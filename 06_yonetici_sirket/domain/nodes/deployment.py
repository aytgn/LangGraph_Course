"""
Deployment Gate Node (HITL Packaging & Disk Export).
Uses ToolRegistry disk operations for physical project packaging.
"""

from domain.state import CompanyState
from domain.utils import append_log, console
from tools.registry import ToolRegistry


def deployment_gate_node(state: CompanyState) -> dict:
    """
    Final node in pipeline: exports source code, documentation, and 1-click
    runner (.bat) to physical disk via ToolRegistry unless rejected or revised.
    """
    if state.get("is_rejected"):
        reason = state.get("rejection_reason") or "Kurucu tarafından reddedildi."
        console.print(f"\n[bold red]❌ [DAĞITIM İPTAL]:[/bold red] {reason}")
        return {
            "is_deployed": False,
            "transition_log": append_log(state, "Deployment_Gate", f"Dağıtım reddedildi: {reason}", "Studio_Director"),
        }

    if (state.get("founder_feedback") or "").strip():
        console.print("\n[bold yellow]🔄 [REVİZYON TALEBİ]:[/bold yellow] Fiziksel dağıtım yerine revizyon döngüsüne dönülüyor...")
        return {
            "is_deployed": False,
            "transition_log": append_log(state, "Deployment_Gate", "Kurucu revizyon talep etti -> Direktöre dönülüyor.", "Studio_Director"),
        }

    console.print("\n[bold green]🚀 [DAĞITIM & PAKETLEME] Uygulama fiziksel diske inşa ediliyor...[/bold green]")

    disk_tool = ToolRegistry.get_tool("disk_export_tool")
    if disk_tool:
        app_folder, run_hint = disk_tool.run(state)
    else:
        app_folder, run_hint = "", ""

    console.print(f"  [green]✔ Uygulama başarıyla paketlendi:[/green] {app_folder}")
    console.print(f"  [cyan]✔ Çalıştırma İpucu:[/cyan] {run_hint}")

    return {
        "is_deployed": True,
        "is_rejected": False,
        "app_folder": app_folder,
        "run_command_hint": run_hint,
        "transition_log": append_log(
            state, "Deployment_Gate", f"Fiziksel diske paketlendi: {app_folder}", "Studio_Director"
        ),
    }
