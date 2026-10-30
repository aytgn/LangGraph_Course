"""
Code Verification Tools - AST Parsing & Cross-Module Import Validation.
"""

import ast
from typing import Dict, List, Optional
from tools.base import StudioTool
from tools.registry import ToolRegistry


class ASTSyntaxCheckerTool(StudioTool):
    """Deterministic AST parser checking for Python syntax errors."""

    def __init__(self):
        super().__init__(
            name="ast_syntax_checker",
            description="Tüm üretilen Python dosyalarını ast.parse ile sözdizimi hatalarına karşı denetler.",
            department="QA_Security_Lead",
            category="Verification",
            parameters_schema={"code_files": "Dict[str, str]"}
        )

    def run(self, code_files: Dict[str, str]) -> List[str]:
        errors = []
        for filename, content in code_files.items():
            if filename.endswith(".py"):
                try:
                    ast.parse(content, filename=filename)
                except SyntaxError as e:
                    errors.append(f"{filename} [Satır {e.lineno}, Sütun {e.offset}]: Sözdizimi hatası: {e.msg}")
                except Exception as e:
                    errors.append(f"{filename}: Ayrıştırma hatası: {str(e)}")
        return errors


class CrossModuleImportValidatorTool(StudioTool):
    """Validates that internal symbols imported across generated files actually exist."""

    def __init__(self):
        super().__init__(
            name="cross_module_import_validator",
            description="Modüller arası 'from modül import sembol' çağrılarının hedef dosyada tanımlı olduğunu doğrular.",
            department="QA_Security_Lead",
            category="Verification",
            parameters_schema={"code_files": "Dict[str, str]"}
        )

    def run(self, code_files: Dict[str, str]) -> List[str]:
        errors = []
        
        # 1. Map all defined top-level symbols in each module
        module_symbols: Dict[str, set] = {}
        parsed_trees: Dict[str, ast.AST] = {}

        for filename, content in code_files.items():
            if not filename.endswith(".py"):
                continue
            mod_name = filename[:-3]
            try:
                tree = ast.parse(content, filename=filename)
                parsed_trees[filename] = tree
                symbols = set()
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        symbols.add(node.name)
                    elif isinstance(node, ast.AsyncFunctionDef):
                        symbols.add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        symbols.add(node.name)
                    elif isinstance(node, ast.Assign):
                        for tgt in node.targets:
                            if isinstance(tgt, ast.Name):
                                symbols.add(tgt.id)
                module_symbols[mod_name] = symbols
            except Exception:
                continue

        # 2. Inspect import calls
        for filename, tree in parsed_trees.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imported_mod = node.module
                    if imported_mod and imported_mod in module_symbols:
                        defined = module_symbols[imported_mod]
                        for alias in node.names:
                            sym = alias.name
                            if sym == "*":
                                continue
                            if sym not in defined:
                                errors.append(
                                    f"{filename}: '{imported_mod}.py' içinden '{sym}' import edilmeye çalışılıyor ancak "
                                    f"'{imported_mod}.py' içinde böyle bir sınıf/fonksiyon/değişken tanımlı değil! "
                                    f"(Mevcut olanlar: {sorted(list(defined))})"
                                )
        return errors


class DeterministicASTSuiteTool(StudioTool):
    """Comprehensive AST and Cross-Import Suite runner."""

    def __init__(self):
        super().__init__(
            name="deterministic_ast_suite",
            description="AST sözdizimi ve modüller arası import sözleşmelerini tek seferde denetler.",
            department="QA_Security_Lead",
            category="Verification",
            parameters_schema={"code_files": "Dict[str, str]", "entrypoint": "str"}
        )
        self.syntax_checker = ASTSyntaxCheckerTool()
        self.import_validator = CrossModuleImportValidatorTool()

    def run(self, code_files: Dict[str, str], entrypoint: str = "app.py") -> List[str]:
        errors = []
        if not code_files:
            return ["Üretilmiş kod dosyası bulunamadı!"]

        if entrypoint not in code_files and any(f.endswith(".py") for f in code_files):
            py_files = [f for f in code_files if f.endswith(".py")]
            if py_files:
                entrypoint = py_files[0]
            else:
                errors.append(f"Ana giriş dosyası '{entrypoint}' dosya listesinde bulunamadı!")

        # Run syntax check
        errors.extend(self.syntax_checker.run(code_files))

        # Run import validation
        errors.extend(self.import_validator.run(code_files))

        return errors


# Register tools in central registry
ToolRegistry.register(ASTSyntaxCheckerTool())
ToolRegistry.register(CrossModuleImportValidatorTool())
ToolRegistry.register(DeterministicASTSuiteTool())
