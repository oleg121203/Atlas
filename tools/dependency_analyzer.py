#!/usr/bin/env python3
"""
Dependency Analyzer Tool for Atlas

This script analyzes the codebase to identify import dependencies and detect potential circular imports.
"""

import ast
import logging
import os
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

@dataclass
class DependencyInfo:
    """Information about a dependency relationship."""
    source_file: str
    target_module: str
    import_type: str  #'import', 'from_import', 'relative_import'
    line_number: int
    is_external: bool
    is_relative: bool
    dependency_level: int = 0  #0=direct, 1=indirect, etc.

@dataclass
class ModuleInfo:
    """Information about a module/file."""
    file_path: str
    module_name: str
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    dependencies: List[str]
    dependents: List[str]
    complexity_score: int = 0

@dataclass
class ArchitecturalAnalysis:
    """Results of architectural analysis."""
    modules: Dict[str, ModuleInfo]
    dependency_graph: Dict[str, List[str]]
    circular_dependencies: List[List[str]]
    external_dependencies: Set[str]
    internal_dependencies: Set[str]
    dependency_layers: Dict[int, List[str]]
    metrics: Dict[str, Any]

class DependencyAnalyzer:
    """Advanced dependency and architectural analyzer for Atlas codebase."""

    def __init__(self, root_path: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root_path = Path(root_path) if root_path else Path(__file__).parent.parent
        self.excluded_dirs = {
            "__pycache__", ".git", ".venv", "venv", "venv-macos", "venv-linux",
            "node_modules", ".pytest_cache", "build", "dist", ".mypy_cache",
            "site-packages", "lib", "include", "Scripts", "bin", "share",
            ".DS_Store", "unused", "monitoring/logs",
        }

        #Initialize dependency graph
        self.dependency_graph = defaultdict(list)
        self.modules = {}

    def analyze_project_architecture(self) -> ArchitecturalAnalysis:
        """Perform comprehensive architectural analysis."""
        self.logger.info("Starting architectural analysis...")

        #1. Discover all Python modules
        python_files = self._find_python_files()

        #2. Analyze each module
        for file_path in python_files:
            module_info = self._analyze_module(file_path)
            if module_info:
                self.modules[module_info.module_name] = module_info

        #3. Build dependency graph
        self._build_dependency_graph()

        #4. Detect circular dependencies
        circular_deps = self._find_circular_dependencies()

        #5. Categorize dependencies
        external_deps, internal_deps = self._categorize_dependencies()

        #6. Calculate dependency layers
        dependency_layers = self._calculate_dependency_layers()

        #7. Calculate metrics
        metrics = self._calculate_architectural_metrics()

        return ArchitecturalAnalysis(
            modules=self.modules,
            dependency_graph=self.dependency_graph,
            circular_dependencies=circular_deps,
            external_dependencies=external_deps,
            internal_dependencies=internal_deps,
            dependency_layers=dependency_layers,
            metrics=metrics,
        )

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []

        for file_path in self.root_path.rglob("*.py"):
            if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                continue
            python_files.append(file_path)

        return python_files

    def _analyze_module(self, file_path: Path) -> Optional[ModuleInfo]:
        """Analyze a single Python module."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            relative_path = file_path.relative_to(self.root_path)
            module_name = str(relative_path).replace("/", ".").replace(".py", "")

            analyzer = ModuleASTAnalyzer(str(file_path), module_name)
            analyzer.visit(tree)

            return ModuleInfo(
                file_path=str(relative_path),
                module_name=module_name,
                imports=analyzer.imports,
                exports=analyzer.exports,
                classes=analyzer.classes,
                functions=analyzer.functions,
                dependencies=analyzer.dependencies,
                dependents=[],  #Will be filled later
                complexity_score=len(analyzer.classes) + len(analyzer.functions),
            )

        except Exception as e:
            self.logger.warning(f"Could not analyze module {file_path}: {e}")
            return None

    def _build_dependency_graph(self):
        """Build dependency graph."""
        #Add all modules as nodes
        for module_name, module_info in self.modules.items():
            self.dependency_graph[module_name] = module_info.dependencies

        #Add dependency edges
        for module_name, module_info in self.modules.items():
            for dependency in module_info.dependencies:
                if dependency in self.modules:
                    #Add to dependents list
                    self.modules[dependency].dependents.append(module_name)

    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the project."""
        try:
            circular_deps = []
            visited = set()
            path = set()

            def dfs(module, current_path):
                visited.add(module)
                path.add(module)
                current_path.append(module)
                for dep in self.dependency_graph[module]:
                    if dep not in visited:
                        if dfs(dep, current_path):
                            if current_path[-1] == current_path[0]:
                                circular_deps.append(current_path[:])
                    elif dep in path:
                        cycle_start = current_path.index(dep)
                        circular_deps.append(current_path[cycle_start:])
                path.remove(module)
                current_path.pop()
                return False

            for module in self.dependency_graph:
                if module not in visited:
                    dfs(module, [])
            return circular_deps
        except Exception as e:
            self.logger.error(f"Error finding circular dependencies: {e}")
            return []

    def _categorize_dependencies(self) -> Tuple[Set[str], Set[str]]:
        """Categorize dependencies as external or internal."""
        external_deps = set()
        internal_deps = set()

        for module_info in self.modules.values():
            for dep in module_info.dependencies:
                if dep in self.modules:
                    internal_deps.add(dep)
                #Check if it's a standard library or external package
                elif self._is_external_dependency(dep):
                    external_deps.add(dep)

        return external_deps, internal_deps

    def _is_external_dependency(self, module_name: str) -> bool:
        """Check if a module is an external dependency."""
        #Standard library modules (simplified check)
        stdlib_modules = {
            "os", "sys", "json", "time", "datetime", "collections", "typing",
            "pathlib", "dataclasses", "logging", "re", "subprocess", "threading",
            "asyncio", "functools", "itertools", "operator", "copy", "pickle",
            "uuid", "hashlib", "base64", "urllib", "http", "html", "xml", "sqlite3", "csv", "configparser", "argparse", "tempfile",
        }

        root_module = module_name.split(".")[0]
        return root_module not in stdlib_modules and root_module not in self.modules

    def _calculate_dependency_layers(self) -> Dict[int, List[str]]:
        """Calculate dependency layers (architectural levels)."""
        layers = defaultdict(list)

        try:
            #Calculate topological sort to determine layers
            topo_order = []
            visited = set()
            temp_visited = set()

            def dfs(module):
                if module in temp_visited:
                    raise ValueError("Circular dependency detected")
                if module in visited:
                    return
                temp_visited.add(module)
                for dep in self.dependency_graph[module]:
                    dfs(dep)
                temp_visited.remove(module)
                visited.add(module)
                topo_order.append(module)

            for module in self.dependency_graph:
                dfs(module)

            #Assign layers based on longest path from nodes with no dependencies
            for node in topo_order:
                predecessors = self.dependency_graph[node]
                if not predecessors:
                    layers[0].append(node)
                else:
                    max_pred_layer = max(
                        self._get_node_layer(pred, layers) for pred in predecessors
                    )
                    layers[max_pred_layer + 1].append(node)

        except Exception as e:
            #If graph has cycles, fall back to simple approach
            for node in self.dependency_graph:
                in_degree = len(self.dependency_graph[node])
                layers[in_degree].append(node)

        return dict(layers)

    def _get_node_layer(self, node: str, layers: Dict[int, List[str]]) -> int:
        """Get the layer of a node."""
        for layer, nodes in layers.items():
            if node in nodes:
                return layer
        return 0

    def _calculate_architectural_metrics(self) -> Dict[str, Any]:
        """Calculate various architectural metrics."""
        total_modules = len(self.modules)
        total_dependencies = sum(len(m.dependencies) for m in self.modules.values())

        #Coupling metrics
        afferent_coupling = {}  #Ca - incoming dependencies
        efferent_coupling = {}  #Ce - outgoing dependencies

        for module_name, module_info in self.modules.items():
            afferent_coupling[module_name] = len(module_info.dependents)
            efferent_coupling[module_name] = len(module_info.dependencies)

        #Instability metrics (I = Ce / (Ca + Ce))
        instability = {}
        for module_name in self.modules:
            ca = afferent_coupling[module_name]
            ce = efferent_coupling[module_name]
            if ca + ce > 0:
                instability[module_name] = ce / (ca + ce)
            else:
                instability[module_name] = 0

        #Calculate complexity distribution
        complexity_scores = [m.complexity_score for m in self.modules.values()]
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0

        return {
            "total_modules": total_modules,
            "total_dependencies": total_dependencies,
            "average_dependencies_per_module": total_dependencies / total_modules if total_modules > 0 else 0,
            "afferent_coupling": afferent_coupling,
            "efferent_coupling": efferent_coupling,
            "instability": instability,
            "average_complexity": avg_complexity,
            "max_complexity": max(complexity_scores) if complexity_scores else 0,
            "dependency_density": total_dependencies / (total_modules * total_modules) if total_modules > 0 else 0,
            "cyclomatic_complexity_distribution": self._calculate_complexity_distribution(),
        }

    def _calculate_complexity_distribution(self) -> Dict[str, int]:
        """Calculate complexity distribution."""
        complexity_ranges = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for module_info in self.modules.values():
            complexity = module_info.complexity_score
            if complexity <= 5:
                complexity_ranges["low"] += 1
            elif complexity <= 15:
                complexity_ranges["medium"] += 1
            elif complexity <= 30:
                complexity_ranges["high"] += 1
            else:
                complexity_ranges["very_high"] += 1

        return complexity_ranges

    def generate_dependency_report(self) -> str:
        """Generate a comprehensive dependency analysis report."""
        analysis = self.analyze_project_architecture()

        report = []
        report.append("🏗️ **Atlas Architectural Analysis Report**\n")

        #Overview
        report.append("## 📊 **Project Overview**")
        report.append(f"- **Total Modules**: {analysis.metrics['total_modules']}")
        report.append(f"- **Total Dependencies**: {analysis.metrics['total_dependencies']}")
        report.append(f"- **Average Dependencies per Module**: {analysis.metrics['average_dependencies_per_module']:.2f}")
        report.append(f"- **Dependency Density**: {analysis.metrics['dependency_density']:.3f}")
        report.append("")

        #Circular Dependencies
        if analysis.circular_dependencies:
            report.append("## 🔄 **Circular Dependencies** ⚠️")
            for i, cycle in enumerate(analysis.circular_dependencies, 1):
                report.append(f"**Cycle {i}**: {' → '.join(cycle)} → {cycle[0]}")
            report.append("")
        else:
            report.append("## ✅ **No Circular Dependencies Found**\n")

        #Dependency Layers
        report.append("## 🏢 **Architectural Layers**")
        for layer, modules in sorted(analysis.dependency_layers.items()):
            report.append(f"**Layer {layer}** ({len(modules)} modules):")
            for module in sorted(modules)[:10]:  #Show first 10
                report.append(f"  - `{module}`")
            if len(modules) > 10:
                report.append(f"  - ... and {len(modules) - 10} more")
            report.append("")

        #Most Connected Modules
        report.append("## 🔗 **Most Connected Modules**")
        coupling_data = [(name, analysis.metrics["afferent_coupling"][name] + analysis.metrics["efferent_coupling"][name])
                        for name in analysis.modules.keys()]
        coupling_data.sort(key=lambda x: x[1], reverse=True)

        for module, total_coupling in coupling_data[:10]:
            ca = analysis.metrics["afferent_coupling"][module]
            ce = analysis.metrics["efferent_coupling"][module]
            instability = analysis.metrics["instability"][module]
            report.append(f"- **`{module}`**: {total_coupling} connections (Ca:{ca}, Ce:{ce}, I:{instability:.2f})")
        report.append("")

        #External Dependencies
        if analysis.external_dependencies:
            report.append("## 📦 **External Dependencies**")
            for dep in sorted(analysis.external_dependencies)[:20]:
                report.append(f"- `{dep}`")
            if len(analysis.external_dependencies) > 20:
                report.append(f"- ... and {len(analysis.external_dependencies) - 20} more")
            report.append("")

        #Complexity Analysis
        complexity_dist = analysis.metrics["cyclomatic_complexity_distribution"]
        report.append("## 📈 **Complexity Distribution**")
        report.append(f"- **Low Complexity** (≤5): {complexity_dist['low']} modules")
        report.append(f"- **Medium Complexity** (6-15): {complexity_dist['medium']} modules")
        report.append(f"- **High Complexity** (16-30): {complexity_dist['high']} modules")
        report.append(f"- **Very High Complexity** (>30): {complexity_dist['very_high']} modules")
        report.append("")

        #Recommendations
        report.append("## 💡 **Architectural Recommendations**")
        if analysis.circular_dependencies:
            report.append("- 🚨 **Critical**: Resolve circular dependencies to improve maintainability")

        high_instability = [(name, inst) for name, inst in analysis.metrics["instability"].items() if inst > 0.8]
        if high_instability:
            report.append("- ⚠️ **High Instability Modules**: Consider stabilizing highly unstable modules")
            for name, inst in sorted(high_instability, key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"  - `{name}` (I: {inst:.2f})")

        if complexity_dist["very_high"] > 0:
            report.append(f"- 🔧 **Refactoring**: {complexity_dist['very_high']} modules have very high complexity")

        if analysis.metrics["dependency_density"] > 0.3:
            report.append("- 📊 **Architecture**: Consider reducing dependency density for better modularity")

        return "\n".join(report)

class ModuleASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing module structure and dependencies."""

    def __init__(self, file_path: str, module_name: str):
        self.file_path = file_path
        self.module_name = module_name
        self.imports = []
        self.exports = []
        self.classes = []
        self.functions = []
        self.dependencies = []

    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(f"import {alias.name}")
            self.dependencies.append(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        if node.module:
            module = node.module
            names = ", ".join(alias.name for alias in node.names)
            self.imports.append(f"from {module} import {names}")
            self.dependencies.append(module.split(".")[0])
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append(node.name)
        self.exports.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.functions.append(node.name)
        self.exports.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions."""
        self.functions.append(node.name)
        self.exports.append(node.name)
        self.generic_visit(node)

def analyze_imports(file_path):
    """Analyze imports in a given Python file."""
    # Avoid conflict with standard library 'email' module
    # by renaming the local email tool directory to email_tool
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    return imports

def build_dependency_graph(root_dir):
    """Build a dependency graph for all Python files in the root directory."""
    dependency_graph = defaultdict(list)
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module_name = os.path.relpath(file_path, root_dir).replace(os.sep, '.')[:-3]
                imports = analyze_imports(file_path)
                dependency_graph[module_name] = imports
    return dependency_graph

def detect_circular_dependencies(dependency_graph):
    """Detect circular dependencies in the dependency graph."""
    visited = set()
    path = set()
    cycles = []

    def dfs(module, current_path):
        visited.add(module)
        path.add(module)
        current_path.append(module)
        # Create a copy of dependencies to avoid runtime modification issues
        deps = list(dependency_graph.get(module, []))
        for dep in deps:
            if dep not in visited:
                if dfs(dep, current_path):
                    if current_path[-1] == current_path[0]:
                        cycles.append(current_path[:])
            elif dep in path:
                cycle_start = current_path.index(dep)
                cycles.append(current_path[cycle_start:])
        path.remove(module)
        current_path.pop()
        return False

    # Create a list of keys to avoid runtime modification issues
    modules = list(dependency_graph.keys())
    for module in modules:
        if module not in visited:
            dfs(module, [])
    return cycles

def find_circular_dependencies() -> str:
    """Find and report circular dependencies."""
    analyzer = DependencyAnalyzer()
    analysis = analyzer.analyze_project_architecture()

    if not analysis.circular_dependencies:
        return "✅ **No circular dependencies found** in the Atlas codebase."

    report = ["🔄 **Circular Dependencies Detected** ⚠️\n"]
    for i, cycle in enumerate(analysis.circular_dependencies, 1):
        report.append(f"**Cycle {i}**: {' → '.join(cycle)} → {cycle[0]}")
        report.append("")

        #Suggest how to break the cycle
        report.append(f"**💡 Suggestion for Cycle {i}**:")
        report.append("- Consider using dependency injection")
        report.append("- Extract common functionality to a shared module")
        report.append("- Use interfaces/protocols to break direct dependencies")
        report.append("")

    return "\n".join(report)

if __name__ == '__main__':
    root_directory = Path(__file__).parent.parent
    print(f"Analyzing dependencies in {root_directory}")
    dep_graph = build_dependency_graph(root_directory)
    print("Dependency Graph:")
    for module, deps in dep_graph.items():
        if deps:
            print(f"  {module}: {', '.join(deps)}")
    print("\nDetecting Circular Dependencies...")
    circular_deps = detect_circular_dependencies(dep_graph)
    if circular_deps:
        print("Circular Dependencies Detected:")
        for cycle in circular_deps:
            print("  -> ".join(cycle) + " -> " + cycle[0])
    else:
        print("No Circular Dependencies Detected.")
