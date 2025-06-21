#!/usr/bin/env python3
"""
Professional Code Analyzer for Atlas System Help Mode
Advanced problem detection and solution recommendation system
"""

import re
import ast
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IssueType(Enum):
    """Types of issues that can be detected."""
    PERFORMANCE = "performance"
    SECURITY = "security" 
    COMPATIBILITY = "compatibility"
    MEMORY_LEAK = "memory_leak"
    CODE_QUALITY = "code_quality"
    DEPENDENCY = "dependency"
    ARCHITECTURE = "architecture"
    ERROR_HANDLING = "error_handling"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Issue:
    """Represents a detected issue."""
    type: IssueType
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    code_snippet: Optional[str]
    suggested_fix: str
    confidence: float
    tags: List[str]

@dataclass
class AnalysisResult:
    """Results of code analysis."""
    issues: List[Issue]
    metrics: Dict[str, Any]
    recommendations: List[str]
    summary: str

class ProfessionalCodeAnalyzer:
    """Advanced code analyzer for professional problem detection."""
    
    def __init__(self) -> None:
        self.patterns = self._initialize_patterns()
        self.metrics_cache: Dict[str, Any] = {}
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize detection patterns for various issues."""
        return {
            'security_issues': {
                'patterns': [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'subprocess\..*shell=True',
                    r'os\.system\(',
                    r'input\(\).*exec',
                    r'pickle\.loads?\(',
                    r'yaml\.load\(',
                ],
                'severity': Severity.HIGH,
                'description': 'Potential security vulnerability detected'
            },
            
            'performance_issues': {
                'patterns': [
                    r'for\s+\w+\s+in\s+range\(len\(',
                    r'\.append\(.*\)\s*$',  #In loops
                    r'time\.sleep\(\d+\)',
                    r'requests\.get\(.*timeout=None',
                    r'while\s+True:(?!\s*#\s*break)',
                ],
                'severity': Severity.MEDIUM,
                'description': 'Performance optimization opportunity'
            },
            
            'memory_issues': {
                'patterns': [
                    r'global\s+\w+\s*=\s*\[',
                    r'cache\s*=\s*\{\}',
                    r'\.read\(\)(?!\s*\.close)',
                    r'open\(.*\)(?!\s*with)',
                ],
                'severity': Severity.MEDIUM,
                'description': 'Potential memory leak or resource management issue'
            },
            
            'error_handling': {
                'patterns': [
                    r'except:(?!\s*#)',
                    r'except\s+Exception:(?!\s*#)',
                    r'pass(?!\s*#)',
                    r'try:.*\n.*except.*:\s*pass',
                ],
                'severity': Severity.HIGH,
                'description': 'Poor error handling detected'
            },
            
            'code_quality': {
                'patterns': [
                    r'def\s+\w+\(.*\):(?:\s*\n){3,}',  #Empty functions
                    r'TODO|FIXME|HACK|XXX',
                    r'print\(',  #Debug prints
                    r'import\s+\*',
                    r'lambda.*:.*lambda',  #Complex lambdas
                ],
                'severity': Severity.LOW,
                'description': 'Code quality improvement opportunity'
            }
        }
    
    async def analyze_codebase(self, root_path: str, focus_areas: Optional[List[str]] = None) -> AnalysisResult:
        """Perform comprehensive codebase analysis."""
        issues: List[Issue] = []
        metrics: Dict[str, Any] = {}
        
        #1. File-level analysis
        python_files = self._find_python_files(root_path)
        
        for file_path in python_files:
            if focus_areas and not any(area in str(file_path) for area in focus_areas):
                continue
                
            file_issues = await self._analyze_file(file_path)
            issues.extend(file_issues)
        
        #2. Architecture analysis
        arch_issues = await self._analyze_architecture(root_path)
        issues.extend(arch_issues)
        
        #3. Dependency analysis
        dep_issues = await self._analyze_dependencies(root_path)
        issues.extend(dep_issues)
        
        #4. Calculate metrics
        metrics = self._calculate_metrics(python_files, issues)
        
        #5. Generate recommendations
        recommendations = self._generate_recommendations(issues, metrics)
        
        #6. Create summary
        summary = self._create_summary(issues, metrics)
        
        return AnalysisResult(
            issues=sorted(issues, key=lambda x: (x.severity.value, -x.confidence)),
            metrics=metrics,
            recommendations=recommendations,
            summary=summary
        )
    
    async def _analyze_file(self, file_path: Path) -> List[Issue]:
        """Analyze a single Python file for issues."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            #Pattern-based analysis
            for category, config in self.patterns.items():
                for pattern in config['patterns']:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            issue = Issue(
                                type=IssueType(category.split('_')[0].lower()),
                                severity=config['severity'],
                                title=f"{category.replace('_', ' ').title()} detected",
                                description=config['description'],
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                suggested_fix=self._suggest_fix(pattern, line),
                                confidence=0.8,
                                tags=[category]
                            )
                            issues.append(issue)
            
            #AST-based analysis
            ast_issues = self._analyze_ast(file_path, content)
            issues.extend(ast_issues)
            
        except Exception as e:
            logger.warning(f"Could not analyze {file_path}: {e}")
        
        return issues
    
    def _analyze_ast(self, file_path: Path, content: str) -> List[Issue]:
        """Perform AST-based analysis for deeper insights."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            #Complexity analysis
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:
                        issues.append(Issue(
                            type=IssueType.CODE_QUALITY,
                            severity=Severity.MEDIUM,
                            title=f"High complexity function: {node.name}",
                            description=f"Function has complexity of {complexity}, consider refactoring",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            code_snippet=f"def {node.name}(...)",
                            suggested_fix="Break down into smaller functions",
                            confidence=0.9,
                            tags=["complexity", "refactoring"]
                        ))
        
        except SyntaxError as e:
            issues.append(Issue(
                type=IssueType.CODE_QUALITY,
                severity=Severity.CRITICAL,
                title="Syntax Error",
                description=f"Syntax error in file: {e}",
                file_path=str(file_path),
                line_number=e.lineno,
                code_snippet="",
                suggested_fix="Fix syntax error",
                confidence=1.0,
                tags=["syntax"]
            ))
        
        return issues
    
    async def _analyze_architecture(self, root_path: str) -> List[Issue]:
        """Analyze overall architecture patterns."""
        issues: List[Issue] = []
        
        #Check for circular imports
        #Check for proper separation of concerns
        #Check for design pattern violations
        
        return issues
    
    async def _analyze_dependencies(self, root_path: str) -> List[Issue]:
        """Analyze dependency issues."""
        issues = []
        
        req_files = [
            Path(root_path) / "requirements.txt",
            Path(root_path) / "requirements-linux.txt", 
            Path(root_path) / "requirements-macos.txt"
        ]
        
        for req_file in req_files:
            if req_file.exists():
                dep_issues = self._check_dependencies(req_file)
                issues.extend(dep_issues)
        
        return issues
    
    def _check_dependencies(self, req_file: Path) -> List[Issue]:
        """Check for dependency issues."""
        issues = []
        
        try:
            content = req_file.read_text()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                #Check for pinned versions
                if '==' not in line and '>=' not in line:
                    issues.append(Issue(
                        type=IssueType.DEPENDENCY,
                        severity=Severity.MEDIUM,
                        title="Unpinned dependency",
                        description=f"Dependency {line} should have version specification",
                        file_path=str(req_file),
                        line_number=line_num,
                        code_snippet=line,
                        suggested_fix=f"Pin version: {line}>=x.x.x",
                        confidence=0.7,
                        tags=["dependencies", "versioning"]
                    ))
        
        except Exception as e:
            logger.warning(f"Could not analyze dependencies in {req_file}: {e}")
        
        return issues
    
    def _suggest_fix(self, pattern: str, code_line: str) -> str:
        """Suggest a fix for detected pattern."""
        fixes = {
            r'eval\s*\(': "Use ast.literal_eval() for safe evaluation",
            r'exec\s*\(': "Avoid exec(), use alternative approaches",
            r'subprocess\..*shell=True': "Use shell=False and pass command as list",
            r'for\s+\w+\s+in\s+range\(len\(': "Use enumerate() or iterate directly",
            r'except:': "Catch specific exceptions instead of bare except",
            r'print\(': "Use logging instead of print statements",
        }
        
        for pat, fix in fixes.items():
            if re.search(pat, pattern):
                return fix
        
        return "Review and improve this code pattern"
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  #Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _find_python_files(self, root_path: str) -> List[Path]:
        """Find all Python files in the project."""
        root = Path(root_path)
        python_files = []
        
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        
        for file_path in root.rglob("*.py"):
            if not any(excluded in file_path.parts for excluded in exclude_dirs):
                python_files.append(file_path)
        
        return python_files
    
    def _calculate_metrics(self, files: List[Path], issues: List[Issue]) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        total_lines = sum(len(f.read_text().split('\n')) for f in files if f.exists())
        
        metrics: Dict[str, Any] = {
            'total_files': len(files),
            'total_lines': total_lines,
            'issues_per_file': len(issues) / len(files) if files else 0,
            'critical_issues': len([i for i in issues if i.severity == Severity.CRITICAL]),
            'high_issues': len([i for i in issues if i.severity == Severity.HIGH]),
            'medium_issues': len([i for i in issues if i.severity == Severity.MEDIUM]),
            'low_issues': len([i for i in issues if i.severity == Severity.LOW]),
            'issue_types': {},
            'quality_score': 0
        }
        
        #Count issue types
        issue_types: Dict[str, int] = {}
        for issue in issues:
            issue_type = issue.type.value
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        metrics['issue_types'] = issue_types
        
        #Calculate quality score (0-100)
        base_score = 100
        critical_count = int(metrics['critical_issues'])
        high_count = int(metrics['high_issues'])
        medium_count = int(metrics['medium_issues'])
        low_count = int(metrics['low_issues'])
        
        base_score -= critical_count * 20
        base_score -= high_count * 10
        base_score -= medium_count * 5
        base_score -= low_count * 1
        
        metrics['quality_score'] = max(0, base_score)
        
        return metrics
    
    def _generate_recommendations(self, issues: List[Issue], metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        #Critical issues first
        critical_count = metrics['critical_issues']
        if critical_count > 0:
            recommendations.append(f"🚨 URGENT: Fix {critical_count} critical issues immediately")
        
        #High priority issues
        high_count = metrics['high_issues']
        if high_count > 0:
            recommendations.append(f"⚠️ HIGH PRIORITY: Address {high_count} high-priority issues")
        
        #Most common issue types
        issue_types = metrics['issue_types']
        if issue_types:
            most_common = max(issue_types.items(), key=lambda x: x[1])
            recommendations.append(f"📊 Focus on {most_common[0]} issues ({most_common[1]} found)")
        
        #Quality score based recommendations
        quality_score = metrics['quality_score']
        if quality_score < 50:
            recommendations.append("🔧 Consider major refactoring - quality score is low")
        elif quality_score < 75:
            recommendations.append("⭐ Good foundation, focus on medium-priority improvements")
        else:
            recommendations.append("✨ Excellent code quality! Focus on optimization")
        
        return recommendations
    
    def _create_summary(self, issues: List[Issue], metrics: Dict[str, Any]) -> str:
        """Create analysis summary."""
        total_issues = len(issues)
        quality_score = metrics['quality_score']
        
        summary = f"""
📋 ANALYSIS SUMMARY
==================
🔍 Total Issues Found: {total_issues}
📊 Quality Score: {quality_score}/100
📁 Files Analyzed: {metrics['total_files']}
📝 Lines of Code: {metrics['total_lines']}

🚨 Critical: {metrics['critical_issues']}
⚠️ High: {metrics['high_issues']}  
📋 Medium: {metrics['medium_issues']}
💡 Low: {metrics['low_issues']}

💼 PROFESSIONAL ASSESSMENT:
{self._get_professional_assessment(quality_score, total_issues)}
"""
        return summary.strip()
    
    def _get_professional_assessment(self, quality_score: int, total_issues: int) -> str:
        """Provide professional assessment of code quality."""
        if quality_score >= 90 and total_issues < 5:
            return "Exceptional code quality. Ready for production deployment."
        elif quality_score >= 75:
            return "Good code quality with minor improvements needed."
        elif quality_score >= 50:
            return "Moderate quality. Requires significant improvements before production."
        else:
            return "Poor code quality. Major refactoring required before deployment."

#Integration functions for Chat Context Manager
def create_professional_analysis_prompt(focus_area: str, user_question: str) -> str:
    """Create prompt for professional code analysis."""
    return f"""You are Atlas Professional Code Analyzer - an expert system for deep codebase investigation.

User's question: "{user_question}"
Focus area: {focus_area}

PROFESSIONAL ANALYSIS PROTOCOL:

1. 🔍 DEEP INVESTIGATION:
   - Use ProfessionalCodeAnalyzer to scan the entire codebase
   - Focus on {focus_area} if specified
   - Identify issues by severity: Critical, High, Medium, Low
   - Calculate quality metrics and scores

2. 🎯 PROBLEM DETECTION:
   - Security vulnerabilities 
   - Performance bottlenecks
   - Memory leaks and resource issues
   - Code quality problems
   - Architecture violations
   - Dependency conflicts

3. 💡 SOLUTION RECOMMENDATIONS:
   - Provide specific, actionable fixes
   - Include code examples where helpful
   - Prioritize by impact and effort
   - Reference exact file locations and line numbers

4. 📊 PROFESSIONAL REPORT:
   - Executive summary of findings
   - Technical details with evidence
   - Risk assessment
   - Implementation roadmap

Start your analysis immediately using the code analysis tools. Be thorough, professional, and solution-oriented."""
