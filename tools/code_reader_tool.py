"""
Advanced code reader tool for Atlas Help mode - provides comprehensive code analysis.
"""

import os
import ast
import json
import time
import hashlib
import logging
import fnmatch
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


import re


@dataclass
class CodeElement:
    """Represents a code element (function, class, variable, etc.)"""
    name: str
    type: str  # 'function', 'class', 'method', 'variable', 'import'
    file_path: str
    line_number: int
    end_line: int
    signature: str
    docstring: Optional[str]
    parent_class: Optional[str] = None
    decorators: List[str] = None
    complexity: int = 0
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class FileAnalysis:
    """Represents analysis of a single file"""
    path: str
    hash: str
    size: int
    lines: int
    last_modified: float
    elements: List[CodeElement]
    imports: List[str]
    dependencies: List[str]
    complexity: int
    encoding: str = 'utf-8'


class CodeIndex:
    """Maintains an index of all code elements for fast searching"""
    
    def __init__(self, cache_file: str = None):
        self.elements: Dict[str, List[CodeElement]] = defaultdict(list)
        self.files: Dict[str, FileAnalysis] = {}
        self.cache_file = cache_file or ".atlas_code_cache.json"
        self.load_cache()
    
    def add_file_analysis(self, analysis: FileAnalysis):
        """Add file analysis to index"""
        self.files[analysis.path] = analysis
        
        # Index all elements
        for element in analysis.elements:
            self.elements[element.name.lower()].append(element)
    
    def search_elements(self, query: str, element_type: str = None) -> List[CodeElement]:
        """Search for code elements by name"""
        query = query.lower()
        results = []
        
        for name, elements in self.elements.items():
            if query in name:
                for element in elements:
                    if element_type is None or element.type == element_type:
                        results.append(element)
        
        return sorted(results, key=lambda x: x.name.lower().find(query))
    
    def get_file_elements(self, file_path: str, element_type: str = None) -> List[CodeElement]:
        """Get all elements from a specific file"""
        if file_path not in self.files:
            return []
        
        elements = self.files[file_path].elements
        if element_type:
            elements = [e for e in elements if e.type == element_type]
        
        return elements
    
    def save_cache(self):
        """Save index to cache file"""
        try:
            cache_data = {
                'files': {path: asdict(analysis) for path, analysis in self.files.items()},
                'timestamp': time.time()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")
    
    def load_cache(self):
        """Load index from cache file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                for path, file_data in cache_data.get('files', {}).items():
                    # Convert dict back to dataclass
                    elements = [CodeElement(**elem) for elem in file_data['elements']]
                    file_data['elements'] = elements
                    analysis = FileAnalysis(**file_data)
                    self.add_file_analysis(analysis)
        except Exception as e:
            logging.error(f"Failed to load cache: {e}")


class CodeReaderTool:
    """Advanced tool for reading and analyzing Atlas codebase in Help mode."""
    
    def __init__(self, root_path: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root_path = Path(root_path) if root_path else Path(__file__).parent.parent
        self.allowed_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml'}
        # Розширений список виключених директорій для macOS
        self.excluded_dirs = {
            '__pycache__', '.git', '.venv', 'venv', 'venv-macos', 'venv-linux', 
            'node_modules', '.pytest_cache', 'build', 'dist', '.mypy_cache',
            'site-packages', 'lib', 'include', 'Scripts', 'bin', 'share',
            '.DS_Store', 'unused', 'monitoring/logs'
        }
        
        # Initialize code index for advanced analysis
        self.index = CodeIndex(cache_file=str(self.root_path / ".atlas_code_cache.json"))
        self._last_index_update = 0
        self._index_update_interval = 300  # 5 minutes
        
        # Запускаємо індексацію в фоні, щоб не блокувати запуск
        # Можна відключити через змінну середовища
        if os.getenv('ATLAS_DISABLE_CODE_INDEXING', '').lower() not in ('true', '1', 'yes'):
            import threading
            self._indexing_thread = threading.Thread(target=self._ensure_index_updated, daemon=True)
            self._indexing_thread.start()
        else:
            self.logger.info("Code indexing disabled via ATLAS_DISABLE_CODE_INDEXING")
        
    def get_file_tree(self, max_depth: int = 3) -> str:
        """Get a tree view of the Atlas codebase structure."""
        try:
            tree_lines = []
            tree_lines.append("📁 Atlas Codebase Structure:")
            tree_lines.append("")
            
            def build_tree(path: Path, prefix: str = "", depth: int = 0):
                if depth >= max_depth:
                    return
                    
                items = []
                try:
                    for item in sorted(path.iterdir()):
                        if item.name.startswith('.'):
                            continue
                        if item.is_dir() and item.name in self.excluded_dirs:
                            continue
                        items.append(item)
                except PermissionError:
                    return
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    
                    if item.is_dir():
                        tree_lines.append(f"{prefix}{current_prefix}📁 {item.name}/")
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        build_tree(item, next_prefix, depth + 1)
                    else:
                        icon = self._get_file_icon(item)
                        tree_lines.append(f"{prefix}{current_prefix}{icon} {item.name}")
            
            build_tree(self.root_path)
            return "\n".join(tree_lines)
            
        except Exception as e:
            self.logger.error(f"Error building file tree: {e}")
            return f"❌ Error reading file tree: {str(e)}"
    
    def read_file(self, file_path: str) -> str:
        """Read a specific file from the Atlas codebase."""
        try:
            # Normalize and validate path
            normalized_path = Path(file_path)
            if not normalized_path.is_absolute():
                full_path = self.root_path / normalized_path
            else:
                full_path = normalized_path
                
            # Security check - ensure path is within root
            try:
                full_path.resolve().relative_to(self.root_path.resolve())
            except ValueError:
                return "❌ Access denied: Path outside Atlas codebase"
            
            # Check if file exists and is readable
            if not full_path.exists():
                return f"❌ File not found: {file_path}"
                
            if not full_path.is_file():
                return f"❌ Not a file: {file_path}"
                
            # Check file extension
            if full_path.suffix not in self.allowed_extensions:
                return f"❌ File type not allowed: {full_path.suffix}. Allowed: {', '.join(self.allowed_extensions)}"
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add file info header
            file_size = len(content)
            line_count = content.count('\n') + 1
            relative_path = full_path.relative_to(self.root_path)
            
            header = f"""📄 **{relative_path}**
📊 Size: {file_size} bytes | Lines: {line_count} | Type: {full_path.suffix}

```{self._get_language_hint(full_path)}
{content}
```"""
            
            return header
            
        except UnicodeDecodeError:
            return f"❌ Cannot read file: {file_path} (binary or unsupported encoding)"
        except PermissionError:
            return f"❌ Permission denied: {file_path}"
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return f"❌ Error reading file: {str(e)}"
    
    def search_in_files(self, search_term: str, file_pattern: str = "**/*.py", max_results: int = 20) -> str:
        """Search for text across Atlas codebase files."""
        try:
            results = []
            search_count = 0
            
            # Use glob to find matching files
            for file_path in self.root_path.glob(file_pattern):
                if search_count >= max_results:
                    break
                    
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                    continue
                    
                # Skip non-allowed extensions
                if file_path.suffix not in self.allowed_extensions:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                    # Search for term in file
                    matches = []
                    for line_num, line in enumerate(lines, 1):
                        if search_term.lower() in line.lower():
                            matches.append(f"  Line {line_num}: {line.strip()}")
                            
                    if matches:
                        relative_path = file_path.relative_to(self.root_path)
                        results.append(f"📄 **{relative_path}**:")
                        results.extend(matches[:5])  # Limit matches per file
                        if len(matches) > 5:
                            results.append(f"  ... and {len(matches) - 5} more matches")
                        results.append("")
                        search_count += 1
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if not results:
                return f"🔍 No results found for '{search_term}' in pattern '{file_pattern}'"
                
            header = f"🔍 **Search Results for '{search_term}'**\n\nFound {search_count} files with matches:\n\n"
            return header + "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return f"❌ Error searching files: {str(e)}"
    
    def get_file_info(self, file_path: str) -> str:
        """Get information about a specific file."""
        try:
            normalized_path = Path(file_path)
            if not normalized_path.is_absolute():
                full_path = self.root_path / normalized_path
            else:
                full_path = normalized_path
                
            # Security check
            try:
                full_path.resolve().relative_to(self.root_path.resolve())
            except ValueError:
                return "❌ Access denied: Path outside Atlas codebase"
            
            if not full_path.exists():
                return f"❌ File not found: {file_path}"
                
            relative_path = full_path.relative_to(self.root_path)
            stat = full_path.stat()
            
            info = f"""📄 **File Information: {relative_path}**

**Type:** {'Directory' if full_path.is_dir() else 'File'}
**Size:** {stat.st_size} bytes
**Extension:** {full_path.suffix or 'None'}
**Last Modified:** {stat.st_mtime}

**Path Details:**
- Absolute: {full_path}
- Relative: {relative_path}
- Readable: {'✅' if os.access(full_path, os.R_OK) else '❌'}
"""
            
            if full_path.is_file() and full_path.suffix in self.allowed_extensions:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    line_count = content.count('\n') + 1
                    info += f"**Lines:** {line_count}\n"
                    
                    # Add first few lines as preview
                    lines = content.split('\n')[:10]
                    info += f"\n**Preview (first 10 lines):**\n```{self._get_language_hint(full_path)}\n"
                    info += '\n'.join(lines)
                    if len(content.split('\n')) > 10:
                        info += "\n... (truncated)"
                    info += "\n```"
                    
                except (UnicodeDecodeError, PermissionError):
                    info += "**Preview:** Not available (binary or permission denied)"
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return f"❌ Error getting file info: {str(e)}"
    
    def list_directory(self, dir_path: str = "") -> str:
        """List contents of a directory."""
        try:
            if not dir_path:
                target_path = self.root_path
            else:
                normalized_path = Path(dir_path)
                if not normalized_path.is_absolute():
                    target_path = self.root_path / normalized_path
                else:
                    target_path = normalized_path
            
            # Security check
            try:
                target_path.resolve().relative_to(self.root_path.resolve())
            except ValueError:
                return "❌ Access denied: Path outside Atlas codebase"
            
            if not target_path.exists():
                return f"❌ Directory not found: {dir_path}"
                
            if not target_path.is_dir():
                return f"❌ Not a directory: {dir_path}"
            
            relative_path = target_path.relative_to(self.root_path)
            items = []
            
            for item in sorted(target_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                if item.is_dir() and item.name in self.excluded_dirs:
                    continue
                    
                icon = self._get_file_icon(item)
                size_info = ""
                if item.is_file():
                    size = item.stat().st_size
                    size_info = f" ({size} bytes)"
                    
                items.append(f"  {icon} {item.name}{size_info}")
            
            header = f"📁 **Directory: /{relative_path}**\n\nContents ({len(items)} items):\n\n"
            return header + "\n".join(items) if items else header + "  (empty directory)"
            
        except PermissionError:
            return f"❌ Permission denied: {dir_path}"
        except Exception as e:
            self.logger.error(f"Error listing directory {dir_path}: {e}")
            return f"❌ Error listing directory: {str(e)}"
    
    # =================== ADVANCED CODE ANALYSIS METHODS ===================
    
    def _ensure_index_updated(self):
        """Ensure code index is up to date"""
        try:
            # Спочатку спробуємо завантажити існуючий кеш
            cache_file = self.root_path / ".atlas_code_cache.json"
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < self._index_update_interval:
                    self.logger.info("Using existing code index cache")
                    return
            
            current_time = time.time()
            if current_time - self._last_index_update > self._index_update_interval:
                self.rebuild_index()
        except Exception as e:
            self.logger.error(f"Error updating index: {e}")
    
    def rebuild_index(self):
        """Rebuild the entire code index from scratch"""
        self.logger.info("Rebuilding code index...")
        start_time = time.time()
        max_indexing_time = 30  # Максимум 30 секунд на індексацію
        
        # Clear existing index
        self.index = CodeIndex(cache_file=str(self.root_path / ".atlas_code_cache.json"))
        
        # Index only Atlas Python files (not venv)
        python_files = []
        for pattern in ["*.py", "agents/*.py", "tools/*.py", "ui/*.py", "utils/*.py", "tests/*.py"]:
            python_files.extend(self.root_path.glob(pattern))
        
        # Обмежуємо кількість файлів
        python_files = python_files[:200]  # Максимум 200 файлів
        
        files_processed = 0
        for file_path in python_files:
            # Перевірка таймауту
            if time.time() - start_time > max_indexing_time:
                self.logger.info(f"Indexing timeout reached, processed {files_processed} files")
                break
                
            if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                continue
            
            try:
                analysis = self._analyze_python_file(file_path)
                if analysis:
                    self.index.add_file_analysis(analysis)
                    files_processed += 1
            except Exception as e:
                self.logger.error(f"Error analyzing file {file_path}: {e}")
                continue
        
        self.index.save_cache()
        self._last_index_update = time.time()
        
        elapsed = time.time() - start_time
        file_count = len(self.index.files)
        element_count = sum(len(elements) for elements in self.index.elements.values())
        
        self.logger.info(f"Index rebuilt: {file_count} files, {element_count} elements in {elapsed:.2f}s")
    
    def _analyze_python_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a Python file using AST and extract code elements"""
        try:
            # Перевірка на виключені директорії
            if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                return None
                
            # Перевірка розміру файлу (максимум 1MB)
            stat = file_path.stat()
            max_size = 1024 * 1024  # 1MB
            if stat.st_size > max_size:
                self.logger.warning(f"Skipping large file {file_path} ({stat.st_size} bytes)")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Перевірка кількості рядків (максимум 10000)
            lines = content.count('\n') + 1
            if lines > 10000:
                self.logger.warning(f"Skipping large file {file_path} ({lines} lines)")
                return None
            
            # Basic file info
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Parse AST з обмеженням глибини рекурсії
            try:
                import sys
                old_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(500)  # Обмежуємо рекурсію
                tree = ast.parse(content, filename=str(file_path))
                sys.setrecursionlimit(old_limit)
            except (SyntaxError, RecursionError) as e:
                self.logger.warning(f"Cannot parse {file_path}: {e}")
                return None
            
            # Extract elements
            analyzer = ASTAnalyzer(str(file_path))
            analyzer.visit(tree)
            
            # Calculate dependencies
            dependencies = self._extract_dependencies(content)
            
            # Calculate file complexity
            complexity = self._calculate_file_complexity(analyzer.elements)
            
            return FileAnalysis(
                path=str(file_path.relative_to(self.root_path)),
                hash=file_hash,
                size=stat.st_size,
                lines=lines,
                last_modified=stat.st_mtime,
                elements=analyzer.elements,
                imports=analyzer.imports,
                dependencies=dependencies,
                complexity=complexity
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
    
    def search_functions(self, query: str = "", class_name: str = None) -> str:
        """Search for functions and methods in the codebase"""
        self._ensure_index_updated()
        
        if query:
            elements = self.index.search_elements(query, 'function')
            elements.extend(self.index.search_elements(query, 'method'))
        else:
            elements = []
            for file_analysis in self.index.files.values():
                elements.extend([e for e in file_analysis.elements if e.type in ['function', 'method']])
        
        # Filter by class if specified
        if class_name:
            elements = [e for e in elements if e.parent_class and class_name.lower() in e.parent_class.lower()]
        
        if not elements:
            return f"🔍 No functions found" + (f" for query '{query}'" if query else "") + (f" in class '{class_name}'" if class_name else "")
        
        # Group by file
        by_file = defaultdict(list)
        for element in elements[:50]:  # Limit results
            by_file[element.file_path].append(element)
        
        result = []
        result.append(f"🔍 **Found {len(elements)} functions/methods**" + (f" matching '{query}'" if query else "") + "\n")
        
        for file_path, file_elements in by_file.items():
            result.append(f"📄 **{file_path}:**")
            for element in file_elements:
                icon = "🔧" if element.type == 'method' else "⚙️"
                parent_info = f" (in {element.parent_class})" if element.parent_class else ""
                complexity_info = f" [complexity: {element.complexity}]" if element.complexity > 0 else ""
                result.append(f"  {icon} `{element.signature}`{parent_info} - Line {element.line_number}{complexity_info}")
                if element.docstring:
                    # Show first line of docstring
                    first_line = element.docstring.split('\n')[0].strip()
                    if first_line:
                        result.append(f"    💬 {first_line}")
            result.append("")
        
        return "\n".join(result)
    
    def search_classes(self, query: str = "") -> str:
        """Search for classes in the codebase"""
        self._ensure_index_updated()
        
        if query:
            elements = self.index.search_elements(query, 'class')
        else:
            elements = []
            for file_analysis in self.index.files.values():
                elements.extend([e for e in file_analysis.elements if e.type == 'class'])
        
        if not elements:
            return f"🔍 No classes found" + (f" for query '{query}'" if query else "")
        
        # Group by file
        by_file = defaultdict(list)
        for element in elements[:30]:  # Limit results
            by_file[element.file_path].append(element)
        
        result = []
        result.append(f"🔍 **Found {len(elements)} classes**" + (f" matching '{query}'" if query else "") + "\n")
        
        for file_path, file_elements in by_file.items():
            result.append(f"📄 **{file_path}:**")
            for element in file_elements:
                decorators_info = ""
                if element.decorators:
                    decorators_info = f" @{', @'.join(element.decorators)}"
                result.append(f"  📦 `{element.name}`{decorators_info} - Line {element.line_number}")
                if element.docstring:
                    # Show first line of docstring
                    first_line = element.docstring.split('\n')[0].strip()
                    if first_line:
                        result.append(f"    💬 {first_line}")
                
                # Show methods in this class
                methods = [e for e in self.index.get_file_elements(file_path, 'method') 
                          if e.parent_class == element.name]
                if methods:
                    method_names = [m.name for m in methods[:5]]
                    more_info = f" + {len(methods) - 5} more" if len(methods) > 5 else ""
                    result.append(f"    🔧 Methods: {', '.join(method_names)}{more_info}")
            result.append("")
        
        return "\n".join(result)
    
    def analyze_file_structure(self, file_path: str) -> str:
        """Provide detailed structural analysis of a Python file"""
        self._ensure_index_updated()
        
        # Normalize path
        normalized_path = Path(file_path)
        if not normalized_path.is_absolute():
            full_path = self.root_path / normalized_path
        else:
            full_path = normalized_path
        
        relative_path = str(full_path.relative_to(self.root_path))
        
        # Check if file is in index
        if relative_path not in self.index.files:
            # Try to analyze it now
            if full_path.suffix == '.py':
                analysis = self._analyze_python_file(full_path)
                if analysis:
                    self.index.add_file_analysis(analysis)
                else:
                    return f"❌ Could not analyze file: {file_path}"
            else:
                return f"❌ File analysis only available for Python files"
        
        analysis = self.index.files[relative_path]
        
        result = []
        result.append(f"📊 **Structural Analysis: {relative_path}**\n")
        result.append(f"**📈 Statistics:**")
        result.append(f"  • Size: {analysis.size} bytes")
        result.append(f"  • Lines: {analysis.lines}")
        result.append(f"  • Complexity: {analysis.complexity}")
        result.append(f"  • Elements: {len(analysis.elements)}")
        result.append("")
        
        # Group elements by type
        by_type = defaultdict(list)
        for element in analysis.elements:
            by_type[element.type].append(element)
        
        # Show imports
        if analysis.imports:
            result.append("📦 **Imports:**")
            for imp in analysis.imports[:10]:
                result.append(f"  • {imp}")
            if len(analysis.imports) > 10:
                result.append(f"  • ... and {len(analysis.imports) - 10} more")
            result.append("")
        
        # Show dependencies
        if analysis.dependencies:
            result.append("🔗 **Dependencies:**")
            for dep in analysis.dependencies[:10]:
                result.append(f"  • {dep}")
            if len(analysis.dependencies) > 10:
                result.append(f"  • ... and {len(analysis.dependencies) - 10} more")
            result.append("")
        
        # Show classes and their methods
        if 'class' in by_type:
            result.append("📦 **Classes:**")
            for cls in by_type['class']:
                result.append(f"  • `{cls.name}` (Line {cls.line_number})")
                if cls.docstring:
                    first_line = cls.docstring.split('\n')[0].strip()
                    if first_line:
                        result.append(f"    💬 {first_line}")
                
                # Show methods for this class
                methods = [e for e in analysis.elements if e.type == 'method' and e.parent_class == cls.name]
                if methods:
                    result.append(f"    🔧 Methods ({len(methods)}):")
                    for method in methods[:5]:
                        result.append(f"      - `{method.name}` (Line {method.line_number})")
                    if len(methods) > 5:
                        result.append(f"      - ... and {len(methods) - 5} more")
            result.append("")
        
        # Show standalone functions
        standalone_functions = [e for e in by_type.get('function', []) if not e.parent_class]
        if standalone_functions:
            result.append("⚙️ **Functions:**")
            for func in standalone_functions:
                complexity_info = f" [complexity: {func.complexity}]" if func.complexity > 0 else ""
                result.append(f"  • `{func.signature}` (Line {func.line_number}){complexity_info}")
                if func.docstring:
                    first_line = func.docstring.split('\n')[0].strip()
                    if first_line:
                        result.append(f"    💬 {first_line}")
            result.append("")
        
        # Show variables/constants
        if 'variable' in by_type:
            result.append("🔤 **Variables/Constants:**")
            for var in by_type['variable'][:10]:
                result.append(f"  • `{var.name}` (Line {var.line_number})")
            if len(by_type['variable']) > 10:
                result.append(f"  • ... and {len(by_type['variable']) - 10} more")
        
        return "\n".join(result)
    
    def find_usage_patterns(self, symbol: str) -> str:
        """Find usage patterns of a symbol across the codebase"""
        self._ensure_index_updated()
        
        results = []
        total_matches = 0
        
        # Search in indexed elements
        elements = self.index.search_elements(symbol)
        if elements:
            results.append(f"🎯 **Symbol Definitions for '{symbol}':**\n")
            for element in elements[:10]:
                icon_map = {'function': '⚙️', 'method': '🔧', 'class': '📦', 'variable': '🔤'}
                icon = icon_map.get(element.type, '📄')
                parent_info = f" (in {element.parent_class})" if element.parent_class else ""
                results.append(f"  {icon} `{element.name}` - {element.file_path}:{element.line_number}{parent_info}")
            results.append("")
        
        # Search for usage in file contents
        usage_results = self.search_in_files(symbol, "**/*.py", max_results=15)
        if "No results found" not in usage_results:
            results.append(f"🔍 **Usage Patterns:**\n")
            results.append(usage_results)
        
        if not results:
            return f"❌ No definitions or usage found for symbol '{symbol}'"
        
        return "\n".join(results)
    
    def get_code_metrics(self) -> str:
        """Get comprehensive code metrics for the entire codebase"""
        self._ensure_index_updated()
        
        if not self.index.files:
            return "❌ No files indexed. Run rebuild_index() first."
        
        # Calculate metrics
        total_files = len(self.index.files)
        total_lines = sum(f.lines for f in self.index.files.values())
        total_size = sum(f.size for f in self.index.files.values())
        
        # Count elements by type
        element_counts = defaultdict(int)
        total_complexity = 0
        
        for file_analysis in self.index.files.values():
            total_complexity += file_analysis.complexity
            for element in file_analysis.elements:
                element_counts[element.type] += 1
        
        # Find most complex files
        complex_files = sorted(self.index.files.values(), 
                             key=lambda f: f.complexity, reverse=True)[:5]
        
        # Find largest files
        large_files = sorted(self.index.files.values(), 
                           key=lambda f: f.lines, reverse=True)[:5]
        
        result = []
        result.append("📊 **Atlas Codebase Metrics**\n")
        
        result.append("**📈 Overall Statistics:**")
        result.append(f"  • Total Files: {total_files}")
        result.append(f"  • Total Lines: {total_lines:,}")
        result.append(f"  • Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        result.append(f"  • Average File Size: {total_lines/total_files:.0f} lines")
        result.append(f"  • Total Complexity: {total_complexity}")
        result.append("")
        
        result.append("**🧩 Code Elements:**")
        for element_type, count in sorted(element_counts.items()):
            icon_map = {'function': '⚙️', 'method': '🔧', 'class': '📦', 'variable': '🔤', 'import': '📦'}
            icon = icon_map.get(element_type, '📄')
            result.append(f"  {icon} {element_type.title()}s: {count}")
        result.append("")
        
        if complex_files:
            result.append("**🔥 Most Complex Files:**")
            for file_analysis in complex_files:
                if file_analysis.complexity > 0:
                    result.append(f"  • {file_analysis.path}: {file_analysis.complexity} complexity")
            result.append("")
        
        if large_files:
            result.append("**📏 Largest Files:**")
            for file_analysis in large_files:
                result.append(f"  • {file_analysis.path}: {file_analysis.lines} lines")
        
        return "\n".join(result)
    
    def smart_search(self, query: str, search_type: str = "all") -> str:
        """Intelligent search that combines multiple search strategies"""
        self._ensure_index_updated()
        
        results = []
        
        if search_type in ["all", "definitions"]:
            # Search for symbol definitions
            elements = self.index.search_elements(query)
            if elements:
                results.append(f"🎯 **Symbol Definitions for '{query}':**\n")
                
                # Group by type
                by_type = defaultdict(list)
                for element in elements[:20]:
                    by_type[element.type].append(element)
                
                for element_type, type_elements in by_type.items():
                    icon_map = {'function': '⚙️', 'method': '🔧', 'class': '📦', 'variable': '🔤'}
                    icon = icon_map.get(element_type, '📄')
                    results.append(f"**{icon} {element_type.title()}s:**")
                    
                    for element in type_elements:
                        parent_info = f" (in {element.parent_class})" if element.parent_class else ""
                        results.append(f"  • `{element.name}` - {element.file_path}:{element.line_number}{parent_info}")
                
                results.append("")
        
        if search_type in ["all", "content"]:
            # Search in file contents
            content_results = self.search_in_files(query, "**/*.py", max_results=10)
            if "No results found" not in content_results:
                results.append(content_results)
                results.append("")
        
        if search_type in ["all", "files"]:
            # Search for files with matching names
            file_matches = []
            for file_path in self.root_path.glob("**/*"):
                if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                    continue
                if query.lower() in file_path.name.lower():
                    relative_path = file_path.relative_to(self.root_path)
                    icon = self._get_file_icon(file_path)
                    file_matches.append(f"  {icon} {relative_path}")
            
            if file_matches:
                results.append(f"📁 **Files matching '{query}':**\n")
                results.extend(file_matches[:10])
                if len(file_matches) > 10:
                    results.append(f"  ... and {len(file_matches) - 10} more")
                results.append("")
        
        if not results:
            return f"❌ No results found for '{query}' with search type '{search_type}'"
        
        return "\n".join(results)
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from import statements"""
        dependencies = set()
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract module name
                if line.startswith('import '):
                    module = line[7:].split()[0].split('.')[0]
                elif line.startswith('from '):
                    module = line[5:].split()[0].split('.')[0]
                
                # Filter out local imports (starting with .)
                if not module.startswith('.'):
                    dependencies.add(module)
        
        return sorted(list(dependencies))
    
    def _calculate_file_complexity(self, elements: List[CodeElement]) -> int:
        """Calculate file complexity based on elements"""
        complexity = 0
        for element in elements:
            if element.type in ['function', 'method']:
                complexity += max(1, element.complexity)
            elif element.type == 'class':
                complexity += 2
        return complexity


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code structure"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.elements: List[CodeElement] = []
        self.imports: List[str] = []
        self.current_class = None
        self.class_stack = []
    
    def visit_Import(self, node):
        """Visit import statements"""
        for alias in node.names:
            self.imports.append(f"import {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from...import statements"""
        module = node.module or ''
        names = ', '.join(alias.name for alias in node.names)
        self.imports.append(f"from {module} import {names}")
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Create class element
        element = CodeElement(
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            signature=f"class {node.name}",
            docstring=docstring,
            decorators=decorators
        )
        self.elements.append(element)
        
        # Push class to stack for nested analysis
        self.class_stack.append(node.name)
        self.current_class = node.name
        
        self.generic_visit(node)
        
        # Pop class from stack
        self.class_stack.pop()
        self.current_class = self.class_stack[-1] if self.class_stack else None
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Build signature
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        signature = f"{node.name}({', '.join(args)})"
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(node)
        
        # Determine if it's a method or function
        element_type = 'method' if self.current_class else 'function'
        
        element = CodeElement(
            name=node.name,
            type=element_type,
            file_path=self.file_path,
            line_number=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            signature=signature,
            docstring=docstring,
            parent_class=self.current_class,
            decorators=decorators,
            complexity=complexity
        )
        self.elements.append(element)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        # Treat async functions the same as regular functions
        self.visit_FunctionDef(node)
    
    def visit_Assign(self, node):
        """Visit variable assignments"""
        # Only capture module-level and class-level variables
        if len(self.class_stack) <= 1:  # Module level or class level
            for target in node.targets:
                if isinstance(target, ast.Name):
                    element = CodeElement(
                        name=target.id,
                        type='variable',
                        file_path=self.file_path,
                        line_number=node.lineno,
                        end_line=getattr(node, 'end_lineno', node.lineno),
                        signature=f"{target.id} = ...",
                        docstring=None,
                        parent_class=self.current_class
                    )
                    self.elements.append(element)
        
        self.generic_visit(node)
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return "unknown"
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        
        return complexity
