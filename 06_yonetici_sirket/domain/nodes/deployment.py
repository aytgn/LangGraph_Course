"""
Deployment Gate Node (HITL Packaging & Disk Export).
Uses ToolRegistry disk operations for physical project packaging.
"""

from rich.console import Console
from domain.state import CompanyState
from domain.utils import append_log
from tools.registry import ToolRegistry

console = Console(force_terminal=False, legacy_windows=False)


def deployment_gate_node(state: CompanyState) -> dict:
    """
    Final node in pipeline: exports source code, documentation, and 1-click
    runner (.bat) to physical disk via ToolRegistry.
    """
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
        "app_folder": app_folder,
        "run_command_hint": run_hint,
        "transition_log": append_log(
            state, "Deployment_Gate", f"Paketlendi: {app_folder}", "Studio_Director"
        )
    }
