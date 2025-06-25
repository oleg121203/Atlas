"""
Advanced AI-Driven Thinking Plugin for Atlas

This enhanced version integrates real AI assistant experience with structured thinking,
creating a more sophisticated and human-like analysis approach.

Key improvements based on AI assistant experience:
- Context-aware query decomposition
- Iterative refinement and validation
- Meta-cognitive awareness
- Confidence scoring and uncertainty handling
- Dynamic strategy selection
- Cross-domain knowledge integration
"""

import json
import logging
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Tuple

#Use Atlas platform detection utilities
try:
    from utils.platform_utils import IS_HEADLESS, IS_LINUX, IS_MACOS, get_platform_info
    PLATFORM_UTILS_AVAILABLE = True
except ImportError:
    #Fallback platform detection
    import os
    import platform
    IS_MACOS = platform.system().lower() == "darwin"
    IS_LINUX = platform.system().lower() == "linux"
    IS_HEADLESS = os.environ.get("DISPLAY") is None and IS_LINUX
    PLATFORM_UTILS_AVAILABLE = False

    def get_platform_info():
        return {
            "system": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "is_macos": IS_MACOS,
            "is_linux": IS_LINUX,
            "is_headless": IS_HEADLESS,
        }

#Try to import memory manager components
try:
    from modules.agents.enhanced_memory_manager import MemoryScope, MemoryType
    MEMORY_INTEGRATION_AVAILABLE = True
except ImportError:
    MEMORY_INTEGRATION_AVAILABLE = False
    #Dummy classes for fallback
    class MemoryScope:
        DEPUTY_AGENT = "deputy_agent"
        HELPER_SYSTEM = "helper_system"
        THINKING_ENGINE = "thinking_engine"

    class MemoryType:
        KNOWLEDGE = "knowledge"
        THINKING_PROCESS = "thinking_process"
        STRATEGY_PATTERN = "strategy_pattern"
        CONTEXT_MAPPING = "context_mapping"


class ThinkingStrategy(Enum):
    """Different thinking strategies based on query type and complexity."""
    ANALYTICAL = "analytical"       #Step-by-step logical analysis
    EXPLORATORY = "exploratory"     #Open-ended investigation
    COMPARATIVE = "comparative"     #Compare and contrast approach
    ARCHITECTURAL = "architectural" #System design and structure focus
    TROUBLESHOOTING = "troubleshooting" #Problem identification and solving
    CREATIVE = "creative"           #Innovation and improvement focus
    CONTEXTUAL = "contextual"       #Context-aware situational analysis


@dataclass
class ThoughtProcess:
    """Represents a complete thinking process with metadata."""
    thought_id: str
    original_query: str
    strategy: ThinkingStrategy
    confidence_score: float
    sub_questions: List[str] = field(default_factory=list)
    analyses: List[str] = field(default_factory=list)
    synthesis: str = ""
    meta_insights: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    tool_usage: Dict[str, int] = field(default_factory=dict)
    uncertainty_areas: List[str] = field(default_factory=list)


@dataclass
class AnalysisContext:
    """Context information for more intelligent analysis."""
    domain: str = "general"
    complexity_level: int = 1  #1-5 scale
    requires_code_analysis: bool = False
    requires_system_knowledge: bool = False
    requires_creative_thinking: bool = False
    language_context: str = "en"
    user_expertise_level: str = "intermediate"  #beginner, intermediate, expert


class AdvancedAIThinkingTool:
    """
    Advanced AI-driven thinking tool that mimics sophisticated AI assistant reasoning.
    
    This tool represents the next evolution of helper systems, incorporating:
    - Multi-strategy thinking approaches
    - Meta-cognitive awareness and self-reflection
    - Dynamic confidence assessment
    - Iterative refinement processes
    - Context-aware analysis adaptation
    - Cross-domain knowledge integration
    """

    def __init__(self, llm_manager=None, memory_manager=None, config_manager=None):
        """Initialize the advanced AI thinking tool."""
        self.name = "advanced_ai_thinking"
        self.description = "Advanced AI-driven structured thinking with meta-cognitive awareness"
        self.version = "3.0.0"

        #Core components
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)

        #Platform and compatibility info
        self.platform_info = get_platform_info()
        self.capabilities = self._assess_capabilities()

        #Advanced configuration
        self.config = self._load_advanced_configuration()

        #Strategy patterns learned from experience
        self.strategy_patterns = self._initialize_strategy_patterns()

        #Meta-cognitive tracking
        self.meta_stats = {
            "total_thoughts": 0,
            "strategy_effectiveness": {},
            "confidence_accuracy": [],
            "refinement_improvements": [],
            "cross_domain_connections": 0,
            "uncertainty_resolutions": 0,
        }

        self.logger.info("Advanced AI Thinking Tool initialized")
        self.logger.info(f"Available strategies: {[s.value for s in ThinkingStrategy]}")

    def _assess_capabilities(self) -> Dict[str, bool]:
        """Assess advanced capabilities."""
        capabilities = {
            "llm_generation": self.llm_manager is not None,
            "memory_storage": self.memory_manager is not None and MEMORY_INTEGRATION_AVAILABLE,
            "platform_detection": PLATFORM_UTILS_AVAILABLE,
            "configuration": self.config_manager is not None,
            "headless_operation": IS_HEADLESS,
            "macos_features": IS_MACOS,
            "linux_features": IS_LINUX,
            "meta_cognition": True,  #Advanced feature
            "strategy_selection": True,
            "confidence_assessment": True,
            "iterative_refinement": True,
            "cross_domain_integration": True,
        }

        #Check Python version compatibility
        python_version = sys.version_info
        capabilities["python_312_plus"] = python_version >= (3, 12)
        capabilities["python_313_plus"] = python_version >= (3, 13)

        return capabilities

    def _load_advanced_configuration(self) -> Dict[str, Any]:
        """Load advanced configuration settings."""
        default_config = {
            #Core thinking parameters
            "max_sub_questions": 7,  #Increased for deeper analysis
            "min_sub_questions": 3,
            "max_iterations": 3,     #Allow iterative refinement
            "confidence_threshold": 0.7,

            #Strategy selection
            "auto_strategy_selection": True,
            "allow_strategy_switching": True,
            "meta_analysis_enabled": True,

            #Quality control
            "enable_self_critique": True,
            "enable_uncertainty_tracking": True,
            "enable_cross_validation": True,

            #Performance optimization
            "enable_caching": True,
            "enable_pattern_learning": True,
            "adaptive_depth": True,

            #Integration settings
            "enable_memory_storage": True,
            "enable_tool_integration": True,
            "response_refinement": True,
            "thinking_timeout": 60.0,  #Increased for complex analysis
        }

        if self.config_manager:
            try:
                plugin_config = {}
                if hasattr(self.config_manager, "get"):
                    plugin_config = self.config_manager.get("advanced_ai_thinking", {})
                elif hasattr(self.config_manager, "get_section"):
                    plugin_config = self.config_manager.get_section("advanced_ai_thinking", {})

                if plugin_config:
                    default_config.update(plugin_config)
                    self.logger.info(f"Loaded advanced configuration: {list(plugin_config.keys())}")

            except Exception as e:
                self.logger.debug(f"Could not load configuration (using defaults): {e}")

        return default_config

    def _initialize_strategy_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize strategy patterns based on AI assistant experience."""
        return {
            ThinkingStrategy.ANALYTICAL.value: {
                "keywords": ["analyze", "breakdown", "components", "structure", "logic"],
                "approach": "systematic_decomposition",
                "depth": "deep",
                "validation": "logical_consistency",
            },
            ThinkingStrategy.EXPLORATORY.value: {
                "keywords": ["explore", "investigate", "discover", "understand", "learn"],
                "approach": "broad_scanning",
                "depth": "broad",
                "validation": "completeness_check",
            },
            ThinkingStrategy.COMPARATIVE.value: {
                "keywords": ["compare", "contrast", "difference", "similar", "versus"],
                "approach": "side_by_side_analysis",
                "depth": "focused",
                "validation": "fairness_balance",
            },
            ThinkingStrategy.ARCHITECTURAL.value: {
                "keywords": ["architecture", "design", "system", "structure", "components"],
                "approach": "hierarchical_analysis",
                "depth": "structural",
                "validation": "coherence_check",
            },
            ThinkingStrategy.TROUBLESHOOTING.value: {
                "keywords": ["problem", "issue", "error", "fix", "solution", "debug"],
                "approach": "root_cause_analysis",
                "depth": "diagnostic",
                "validation": "solution_viability",
            },
            ThinkingStrategy.CREATIVE.value: {
                "keywords": ["improve", "enhance", "innovate", "create", "optimize"],
                "approach": "divergent_thinking",
                "depth": "imaginative",
                "validation": "feasibility_assessment",
            },
            ThinkingStrategy.CONTEXTUAL.value: {
                "keywords": ["context", "situation", "environment", "specific", "particular"],
                "approach": "situational_analysis",
                "depth": "contextual",
                "validation": "relevance_check",
            },
        }

    def analyze_query_context(self, query: str) -> AnalysisContext:
        """Analyze the query to determine context and requirements."""
        query_lower = query.lower()

        #Detect language context
        ukrainian_indicators = ["як", "що", "чому", "де", "коли", "який", "пам'ять", "система", "проаналізуй", "покращ"]
        language_context = "uk" if any(word in query_lower for word in ukrainian_indicators) else "en"

        #Enhanced complexity assessment
        complexity_indicators = [
            len(query.split()) > 10,  #Medium query
            len(query.split()) > 20,  #Long query
            "?" in query and query.count("?") > 1,  #Multiple questions
            any(word in query_lower for word in ["архітектур", "система", "комплекс", "інтеграц", "architecture", "system", "complex", "integration"]),
            any(word in query_lower for word in ["аналіз", "детальн", "глибок", "comprehensive", "detailed", "analyze"]),
            any(word in query_lower for word in ["покращ", "удосконал", "оптиміза", "improve", "enhance", "optimize"]),
            any(word in query_lower for word in ["алгоритм", "algorithm", "метод", "method", "підхід", "approach"]),
        ]
        complexity_level = min(5, sum(complexity_indicators) + 1)

        #Enhanced domain detection
        code_indicators = ["код", "функц", "клас", "алгоритм", "програм", "code", "implementation", "function", "class", "algorithm", "programming"]
        system_indicators = ["систем", "архітектур", "пам'ять", "менеджер", "компонент", "модул", "system", "architecture", "memory", "manager", "component", "module"]
        creative_indicators = ["покращ", "удосконал", "оптиміза", "креатив", "інновац", "improve", "enhance", "optimize", "better", "creative", "innovation"]
        analysis_indicators = ["аналіз", "дослід", "вивча", "розгля", "analyze", "study", "examine", "investigate"]

        requires_code_analysis = any(word in query_lower for word in code_indicators)
        requires_system_knowledge = any(word in query_lower for word in system_indicators)
        requires_creative_thinking = any(word in query_lower for word in creative_indicators)
        requires_analysis = any(word in query_lower for word in analysis_indicators)

        #Determine domain with enhanced logic
        if requires_code_analysis and requires_system_knowledge:
            domain = "software_architecture"
        elif requires_code_analysis:
            domain = "software_engineering"
        elif requires_system_knowledge:
            domain = "system_architecture"
        elif requires_creative_thinking:
            domain = "innovation_design"
        elif requires_analysis:
            domain = "analytical_research"
        else:
            domain = "general_analysis"

        #Boost complexity for specific patterns
        if any(word in query_lower for word in ["що не так", "проблем", "trouble", "issue"]):
            complexity_level = max(complexity_level, 3)  #Troubleshooting is complex
        if any(word in query_lower for word in ["архітектур", "architecture"]):
            complexity_level = max(complexity_level, 4)  #Architecture is complex

        return AnalysisContext(
            domain=domain,
            complexity_level=complexity_level,
            requires_code_analysis=requires_code_analysis,
            requires_system_knowledge=requires_system_knowledge,
            requires_creative_thinking=requires_creative_thinking,
            language_context=language_context,
            user_expertise_level="expert",  #Atlas users are typically technical
        )

    def select_thinking_strategy(self, query: str, context: AnalysisContext) -> ThinkingStrategy:
        """Select the most appropriate thinking strategy."""
        query_lower = query.lower()
        strategy_scores = {}

        #Enhanced Ukrainian keyword detection
        ukrainian_keywords = {
            ThinkingStrategy.ARCHITECTURAL.value: ["архітектур", "структур", "систем", "компонент", "дизайн", "побудов"],
            ThinkingStrategy.TROUBLESHOOTING.value: ["проблем", "помилк", "не працює", "не так", "виправ", "налагод", "проблематика"],
            ThinkingStrategy.CREATIVE.value: ["покращ", "удосконал", "інновац", "покращен", "оптиміза", "креатив"],
            ThinkingStrategy.COMPARATIVE.value: ["порівня", "різні", "відмінності", "схожості", "versus", "проти"],
            ThinkingStrategy.EXPLORATORY.value: ["дослід", "вивча", "розглян", "аназ", "з'ясува"],
            ThinkingStrategy.ANALYTICAL.value: ["аналіз", "розбор", "деталь", "компонент", "логік"],
        }

        #Score each strategy based on query content and context
        for strategy_name in [s.value for s in ThinkingStrategy]:
            score = 0
            pattern = self.strategy_patterns.get(strategy_name, {})

            #Enhanced keyword matching (English + Ukrainian)
            english_keywords = pattern.get("keywords", [])
            ukrainian_keywords_list = ukrainian_keywords.get(strategy_name, [])

            #Count English keyword matches
            keyword_matches = sum(1 for keyword in english_keywords if keyword in query_lower)
            score += keyword_matches * 2

            #Count Ukrainian keyword matches
            ukrainian_matches = sum(1 for keyword in ukrainian_keywords_list if keyword in query_lower)
            score += ukrainian_matches * 3  #Higher weight for Ukrainian

            #Context-based scoring with enhanced detection
            if strategy_name == ThinkingStrategy.ARCHITECTURAL.value:
                if context.requires_system_knowledge or any(word in query_lower for word in ["архітектур", "систем", "пам'ят", "структур"]):
                    score += 5  #Higher priority for architecture
            elif strategy_name == ThinkingStrategy.TROUBLESHOOTING.value:
                if any(word in query_lower for word in ["що не так", "проблем", "помилк", "не працює", "виправ"]):
                    score += 5
            elif strategy_name == ThinkingStrategy.CREATIVE.value:
                if context.requires_creative_thinking or any(word in query_lower for word in ["покращ", "удосконал", "як можна"]):
                    #Lower priority if it's primarily architectural
                    arch_score = sum(1 for word in ["архітектур", "систем", "пам'ят"] if word in query_lower)
                    if arch_score == 0:
                        score += 4
                    else:
                        score += 2  #Reduced score if architectural context
            elif strategy_name == ThinkingStrategy.COMPARATIVE.value:
                if any(word in query_lower for word in ["порівня", "різн", "відмінност"]):
                    score += 4
            elif strategy_name == ThinkingStrategy.EXPLORATORY.value:
                if any(word in query_lower for word in ["як", "що", "чому", "дослід"]):
                    score += 2
            elif strategy_name == ThinkingStrategy.ANALYTICAL.value:
                if context.complexity_level > 3 or any(word in query_lower for word in ["проаналіз", "аналіз"]):
                    score += 3

            strategy_scores[strategy_name] = score

        #Select strategy with highest score, fallback to analytical
        if not strategy_scores or max(strategy_scores.values()) == 0:
            return ThinkingStrategy.ANALYTICAL

        best_strategy_name = max(strategy_scores.items(), key=lambda x: x[1])[0]
        return ThinkingStrategy(best_strategy_name)

    def generate_strategic_questions(self, query: str, strategy: ThinkingStrategy, context: AnalysisContext) -> List[str]:
        """Generate questions based on the selected thinking strategy."""
        if not self.capabilities["llm_generation"]:
            return self._heuristic_strategic_breakdown(query, strategy)

        try:
            strategy_guidance = self._get_strategy_guidance(strategy, context)

            prompt = f"""
            As an advanced AI assistant, break down this query using a {strategy.value} thinking approach.
            
            Original query: {query}
            Context: {context.domain} domain, complexity level {context.complexity_level}/5
            Language context: {context.language_context}
            
            Strategy guidance: {strategy_guidance}
            
            Generate {self.config['min_sub_questions']}-{self.config['max_sub_questions']} strategic sub-questions that:
            1. Follow the {strategy.value} approach systematically
            2. Build upon each other logically
            3. Cover all essential aspects of the query
            4. Are specific and actionable
            5. Consider the technical expertise level
            
            Format as numbered list (1. 2. 3. etc.).
            """

            messages = [{"role": "user", "content": prompt}]
            response = self.llm_manager.chat(messages)

            if response and hasattr(response, "content"):
                content = response.content
            elif response and hasattr(response, "response"):
                content = response.response
            else:
                content = str(response)

            #Extract questions with improved parsing
            sub_questions = []
            for line in content.split("\n"):
                line = line.strip()
                if line and len(line) > 5:
                    #Match various numbering patterns
                    match = re.match(r"^(\d+)[.\)\-]\s*(.+)", line)
                    if match:
                        question = match.group(2).strip()
                        if len(question) > 10:
                            if not question.endswith("?"):
                                question += "?"
                            sub_questions.append(question)

            return sub_questions if sub_questions else [query]

        except Exception as e:
            self.logger.error(f"Error generating strategic questions: {e}")
            return self._heuristic_strategic_breakdown(query, strategy)

    def _get_strategy_guidance(self, strategy: ThinkingStrategy, context: AnalysisContext) -> str:
        """Get specific guidance for the chosen strategy."""
        guidance_map = {
            ThinkingStrategy.ANALYTICAL: "Break down into logical components, identify relationships, analyze each part systematically",
            ThinkingStrategy.EXPLORATORY: "Investigate broad aspects, discover connections, explore multiple perspectives",
            ThinkingStrategy.COMPARATIVE: "Identify key dimensions for comparison, analyze similarities and differences",
            ThinkingStrategy.ARCHITECTURAL: "Examine structure, components, interactions, and design principles",
            ThinkingStrategy.TROUBLESHOOTING: "Identify symptoms, investigate root causes, evaluate potential solutions",
            ThinkingStrategy.CREATIVE: "Generate improvements, explore possibilities, think beyond current limitations",
            ThinkingStrategy.CONTEXTUAL: "Consider specific situation, environment, constraints, and stakeholders",
        }

        base_guidance = guidance_map.get(strategy, "Analyze systematically and thoroughly")

        #Add context-specific guidance
        if context.requires_code_analysis:
            base_guidance += ". Focus on code structure, implementation details, and technical aspects."
        if context.requires_system_knowledge:
            base_guidance += ". Consider system architecture, component interactions, and design patterns."
        if context.complexity_level > 3:
            base_guidance += ". Use deep analysis with multiple layers of investigation."

        return base_guidance

    def _heuristic_strategic_breakdown(self, query: str, strategy: ThinkingStrategy) -> List[str]:
        """Fallback strategic breakdown when LLM is not available."""
        query_lower = query.lower()
        is_ukrainian = any(word in query_lower for word in ["як", "що", "чому", "проаналізуй", "покращ", "модул", "систем"])

        if is_ukrainian:
            if strategy == ThinkingStrategy.ANALYTICAL:
                return [
                    f"Які основні компоненти включає: {query}?",
                    f"Як взаємодіють ці компоненти в: {query}?",
                    f"Які принципи лежать в основі: {query}?",
                    f"Які наслідки та результати: {query}?",
                ]
            if strategy == ThinkingStrategy.ARCHITECTURAL:
                return [
                    f"Яка загальна архітектура: {query}?",
                    f"Які ключові компоненти та їх відповідальності в: {query}?",
                    f"Як компоненти взаємодіють та інтегруються в: {query}?",
                    f"Які принципи дизайну використовуються в: {query}?",
                ]
            if strategy == ThinkingStrategy.CREATIVE:
                return [
                    f"Які поточні обмеження: {query}?",
                    f"Які інноваційні підходи могли б покращити: {query}?",
                    f"Які нові технології могли б удосконалити: {query}?",
                    f"Як би виглядала ідеальна версія: {query}?",
                ]
            if strategy == ThinkingStrategy.TROUBLESHOOTING:
                return [
                    f"Які проблеми або недоліки існують з: {query}?",
                    f"Які кореневі причини проблем в: {query}?",
                    f"Які рішення або виправлення могли б вирішити: {query}?",
                    f"Як можна запобігти подібним проблемам з: {query}?",
                ]
            if strategy == ThinkingStrategy.COMPARATIVE:
                return [
                    f"Які різні підходи існують до: {query}?",
                    f"Як порівнюються ці підходи в контексті: {query}?",
                    f"Які переваги та недоліки кожного варіанту для: {query}?",
                    f"Який підхід найкраще підходить для: {query}?",
                ]
            #Default exploratory approach
            return [
                f"Який поточний стан: {query}?",
                f"Як працює {query} внутрішньо?",
                f"Які сильні та слабкі сторони: {query}?",
                f"Які можливості існують для покращення: {query}?",
            ]
        #English questions
        if strategy == ThinkingStrategy.ANALYTICAL:
            return [
                f"What are the core components of: {query}?",
                f"How do these components interact in: {query}?",
                f"What are the underlying principles behind: {query}?",
                f"What are the implications and consequences of: {query}?",
            ]
        if strategy == ThinkingStrategy.ARCHITECTURAL:
            return [
                f"What is the overall architecture of: {query}?",
                f"What are the key components and their responsibilities in: {query}?",
                f"How do the components communicate and integrate in: {query}?",
                f"What are the design patterns and principles used in: {query}?",
            ]
        if strategy == ThinkingStrategy.CREATIVE:
            return [
                f"What are the current limitations of: {query}?",
                f"What innovative approaches could improve: {query}?",
                f"What emerging technologies or patterns could enhance: {query}?",
                f"What would an ideal future version of {query} look like?",
            ]
        if strategy == ThinkingStrategy.TROUBLESHOOTING:
            return [
                f"What problems or issues exist with: {query}?",
                f"What are the root causes of issues in: {query}?",
                f"What solutions or fixes could address: {query}?",
                f"How can we prevent similar issues in the future with: {query}?",
            ]
        if strategy == ThinkingStrategy.COMPARATIVE:
            return [
                f"What different approaches exist for: {query}?",
                f"How do these approaches compare in context of: {query}?",
                f"What are the advantages and disadvantages of each for: {query}?",
                f"Which approach is best suited for: {query}?",
            ]
        #Default exploratory approach
        return [
            f"What is the current state of: {query}?",
            f"How does {query} work internally?",
            f"What are the strengths and weaknesses of: {query}?",
            f"What opportunities exist for improving: {query}?",
        ]

    def analyze_with_meta_cognition(self, sub_question: str, available_tools: Dict[str, Callable], context: AnalysisContext) -> Tuple[str, float, List[str]]:
        """
        Analyze a sub-question with meta-cognitive awareness.
        
        Returns:
            Tuple of (analysis, confidence_score, uncertainty_areas)
        """
        start_time = time.time()

        try:
            #Select relevant tools based on context
            relevant_tools = self._select_contextual_tools(sub_question, available_tools, context)

            #Gather tool results
            tool_results = {}
            for tool_name in relevant_tools:
                try:
                    tool_fn = available_tools[tool_name]
                    result = tool_fn(sub_question)
                    if result:
                        tool_results[tool_name] = str(result)[:self.config.get("max_tool_response_length", 1000)]
                except Exception as e:
                    self.logger.debug(f"Tool {tool_name} failed: {e}")
                    tool_results[tool_name] = f"Tool error: {str(e)[:100]}"

            #Generate analysis with confidence assessment
            if self.capabilities["llm_generation"]:
                analysis, confidence, uncertainties = self._generate_meta_aware_analysis(
                    sub_question, tool_results, context,
                )
            else:
                analysis = self._fallback_analysis(sub_question, tool_results)
                confidence = 0.5  #Medium confidence for fallback
                uncertainties = ["Limited analysis due to LLM unavailability"]

            #Track performance
            processing_time = time.time() - start_time
            self.logger.debug(f"Meta-cognitive analysis completed in {processing_time:.2f}s, confidence: {confidence}")

            return analysis, confidence, uncertainties

        except Exception as e:
            self.logger.error(f"Error in meta-cognitive analysis: {e}")
            return f"Error analyzing: {sub_question}", 0.2, [f"Analysis error: {e!s}"]

    def _select_contextual_tools(self, question: str, available_tools: Dict[str, Callable], context: AnalysisContext) -> List[str]:
        """Select tools based on question content and analysis context."""
        if not available_tools:
            return []

        question_lower = question.lower()
        selected_tools = []

        #Priority-based tool selection
        tool_priorities = {
            "semantic_search": 3 if context.requires_system_knowledge else 1,
            "code_search": 3 if context.requires_code_analysis else 1,
            "file_search": 2 if "file" in question_lower else 1,
            "memory_search": 2 if "memory" in question_lower else 1,
            "grep_search": 2 if context.requires_code_analysis else 1,
        }

        #Add available tools with their priorities
        tool_scores = []
        for tool_name in available_tools:
            base_priority = tool_priorities.get(tool_name, 1)

            #Keyword-based scoring
            keyword_score = 0
            if "search" in tool_name and any(word in question_lower for word in ["find", "search", "locate"]):
                keyword_score += 2
            if "memory" in tool_name and any(word in question_lower for word in ["memory", "remember", "stored"]):
                keyword_score += 2
            if "code" in tool_name and context.requires_code_analysis:
                keyword_score += 2

            total_score = base_priority + keyword_score
            tool_scores.append((tool_name, total_score))

        #Sort by score and select top tools
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        max_tools = min(4, len(tool_scores))  #Limit to prevent overwhelming

        return [tool[0] for tool in tool_scores[:max_tools]]

    def _generate_meta_aware_analysis(self, question: str, tool_results: Dict[str, str], context: AnalysisContext) -> Tuple[str, float, List[str]]:
        """Generate analysis with meta-cognitive awareness and confidence assessment."""
        try:
            #Create a sophisticated analysis prompt
            analysis_prompt = f"""
            As an advanced AI assistant, analyze this question with meta-cognitive awareness.
            
            Question: {question}
            Context: {context.domain} domain, complexity {context.complexity_level}/5
            
            Tool results:
            {json.dumps(tool_results, indent=2) if tool_results else "No tool results available"}
            
            Please provide:
            1. A comprehensive analysis addressing the question
            2. Your confidence level (0.0-1.0) in this analysis
            3. Any areas of uncertainty or limitations
            
            Guidelines:
            - Be specific and actionable
            - Acknowledge limitations and uncertainties honestly
            - Synthesize information from multiple sources
            - Consider the technical context and complexity
            - Provide insights beyond just summarizing tool results
            
            Format your response as:
            ANALYSIS: [your detailed analysis]
            CONFIDENCE: [0.0-1.0 score]
            UNCERTAINTIES: [list any areas of uncertainty]
            """

            messages = [{"role": "user", "content": analysis_prompt}]
            response = self.llm_manager.chat(messages)

            if response and hasattr(response, "content"):
                content = response.content
            elif response and hasattr(response, "response"):
                content = response.response
            else:
                content = str(response)

            #Parse the structured response
            analysis, confidence, uncertainties = self._parse_meta_response(content)

            return analysis, confidence, uncertainties

        except Exception as e:
            self.logger.warning(f"Meta-aware analysis failed: {e}")
            #Fallback to simple analysis
            fallback_analysis = self._fallback_analysis(question, tool_results)
            return fallback_analysis, 0.6, ["LLM analysis failed, using fallback"]

    def _parse_meta_response(self, content: str) -> Tuple[str, float, List[str]]:
        """Parse structured meta-cognitive response."""
        analysis = ""
        confidence = 0.5
        uncertainties = []

        #Split content into sections
        sections = content.split("\n")
        current_section = None

        for line in sections:
            line = line.strip()
            if line.startswith("ANALYSIS:"):
                current_section = "analysis"
                analysis = line[9:].strip()
            elif line.startswith("CONFIDENCE:"):
                current_section = "confidence"
                conf_text = line[11:].strip()
                try:
                    confidence = float(re.findall(r"[0-9.]+", conf_text)[0])
                    confidence = max(0.0, min(1.0, confidence))  #Clamp to valid range
                except:
                    confidence = 0.5
            elif line.startswith("UNCERTAINTIES:"):
                current_section = "uncertainties"
                unc_text = line[13:].strip()
                if unc_text:
                    uncertainties.append(unc_text)
            elif current_section == "analysis" and line:
                analysis += " " + line
            elif current_section == "uncertainties" and line:
                uncertainties.append(line)

        #Ensure we have some analysis
        if not analysis.strip():
            analysis = content[:500] + "..." if len(content) > 500 else content

        return analysis.strip(), confidence, uncertainties

    def _fallback_analysis(self, question: str, tool_results: Dict[str, str]) -> str:
        """Fallback analysis when LLM is not available."""
        if tool_results:
            analysis_parts = [f"Analysis of '{question}':"]
            for tool, result in tool_results.items():
                analysis_parts.append(f"• {tool}: {result[:200]}{'...' if len(result) > 200 else ''}")
            return "\n".join(analysis_parts)
        return f"Analysis of '{question}': This question requires investigation of key technical aspects and system components."

    def synthesize_with_refinement(self, original_query: str, analyses: List[Tuple[str, float, List[str]]], strategy: ThinkingStrategy, context: AnalysisContext) -> str:
        """Synthesize response with iterative refinement capability."""
        if not analyses:
            return "I apologize, but I wasn't able to analyze your question properly."

        #Calculate overall confidence
        confidences = [conf for _, conf, _ in analyses]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        #Collect all uncertainties
        all_uncertainties = []
        for _, _, uncertainties in analyses:
            all_uncertainties.extend(uncertainties)

        if not self.capabilities["llm_generation"]:
            return self._fallback_synthesis(original_query, [analysis for analysis, _, _ in analyses])

        try:
            #First synthesis attempt
            synthesis_prompt = f"""
            As an advanced AI assistant, synthesize a comprehensive response using {strategy.value} thinking approach.
            
            Original query: {original_query}
            Context: {context.domain} domain, complexity {context.complexity_level}/5
            Overall confidence: {overall_confidence:.2f}
            
            Detailed analyses:
            {self._format_analyses_for_synthesis(analyses)}
            
            Key uncertainties to address:
            {chr(10).join([f"- {unc}" for unc in set(all_uncertainties[:5])]) if all_uncertainties else "None identified"}
            
            Instructions:
            1. Create a cohesive, expert-level response following {strategy.value} approach
            2. Integrate insights naturally and logically
            3. Address uncertainties where possible
            4. Use technical depth appropriate for the domain
            5. Provide actionable insights and recommendations
            6. Be honest about limitations while being comprehensive
            7. Structure the response clearly with logical flow
            
            Comprehensive response:
            """

            messages = [{"role": "user", "content": synthesis_prompt}]
            response = self.llm_manager.chat(messages)

            if response and hasattr(response, "content"):
                initial_synthesis = response.content
            elif response and hasattr(response, "response"):
                initial_synthesis = response.response
            else:
                initial_synthesis = str(response)

            #Apply refinement if enabled and confidence is below threshold
            if (self.config["enable_self_critique"] and
                overall_confidence < self.config["confidence_threshold"]):
                return self._refine_with_self_critique(original_query, initial_synthesis, all_uncertainties, context)

            return initial_synthesis

        except Exception as e:
            self.logger.error(f"Error in synthesis with refinement: {e}")
            return self._fallback_synthesis(original_query, [analysis for analysis, _, _ in analyses])

    def _format_analyses_for_synthesis(self, analyses: List[Tuple[str, float, List[str]]]) -> str:
        """Format analyses for synthesis prompt."""
        formatted = []
        for i, (analysis, confidence, uncertainties) in enumerate(analyses, 1):
            formatted.append(f"Analysis {i} (confidence: {confidence:.2f}):")
            formatted.append(analysis)
            if uncertainties:
                formatted.append(f"Uncertainties: {', '.join(uncertainties[:3])}")
            formatted.append("")
        return "\n".join(formatted)

    def _refine_with_self_critique(self, original_query: str, initial_response: str, uncertainties: List[str], context: AnalysisContext) -> str:
        """Apply self-critique and refinement to improve response quality."""
        try:
            critique_prompt = f"""
            As an advanced AI assistant, critique and refine this response to improve its quality.
            
            Original query: {original_query}
            Initial response: {initial_response}
            
            Known uncertainties: {', '.join(set(uncertainties[:5]))}
            Context: {context.domain} domain
            
            Critique guidelines:
            1. Identify gaps or weaknesses in the response
            2. Check for logical consistency and flow
            3. Ensure technical accuracy where possible
            4. Verify that all aspects of the query are addressed
            5. Assess clarity and actionability
            
            Provide an improved version that:
            - Addresses identified weaknesses
            - Fills important gaps
            - Improves clarity and structure
            - Adds valuable insights
            - Maintains honesty about limitations
            
            Refined response:
            """

            messages = [{"role": "user", "content": critique_prompt}]
            response = self.llm_manager.chat(messages)

            if response and hasattr(response, "content"):
                refined_response = response.content
            elif response and hasattr(response, "response"):
                refined_response = response.response
            else:
                refined_response = str(response)

            #Track refinement improvement
            self.meta_stats["refinement_improvements"].append({
                "original_length": len(initial_response),
                "refined_length": len(refined_response),
                "timestamp": time.time(),
            })

            return refined_response

        except Exception as e:
            self.logger.warning(f"Self-critique refinement failed: {e}")
            return initial_response

    def _fallback_synthesis(self, original_query: str, analyses: List[str]) -> str:
        """Enhanced fallback synthesis."""
        response_parts = [
            f"Comprehensive analysis of: {original_query}",
            "",
        ]

        for i, analysis in enumerate(analyses, 1):
            response_parts.append(f"Key Finding {i}:")
            response_parts.append(analysis)
            response_parts.append("")

        response_parts.extend([
            "Summary:",
            "Based on the analysis above, this question involves multiple interconnected aspects that require careful consideration of technical implementation, system architecture, and optimization opportunities.",
            "",
            "Note: This analysis was generated with limited AI assistance and may benefit from additional investigation.",
        ])

        return "\n".join(response_parts)

    def process_with_advanced_thinking(self, query: str, available_tools: Dict[str, Callable] = None) -> str:
        """
        Main processing method with advanced AI thinking capabilities.
        """
        start_time = time.time()

        if available_tools is None:
            available_tools = {}

        #Generate unique thought process ID
        thought_id = self._generate_thought_id()
        self.logger.info(f"Starting advanced thinking process {thought_id}")

        try:
            #Phase 1: Context Analysis and Strategy Selection
            context = self.analyze_query_context(query)
            strategy = self.select_thinking_strategy(query, context)

            self.logger.info(f"Selected {strategy.value} strategy for {context.domain} domain (complexity: {context.complexity_level})")

            #Phase 2: Strategic Question Generation
            sub_questions = self.generate_strategic_questions(query, strategy, context)

            #Phase 3: Meta-Cognitive Analysis
            analyses = []
            for i, sub_question in enumerate(sub_questions):
                self.logger.debug(f"Meta-cognitive analysis {i+1}/{len(sub_questions)}: {sub_question}")
                analysis, confidence, uncertainties = self.analyze_with_meta_cognition(
                    sub_question, available_tools, context,
                )
                analyses.append((analysis, confidence, uncertainties))

            #Phase 4: Synthesis with Refinement
            final_response = self.synthesize_with_refinement(query, analyses, strategy, context)

            #Phase 5: Meta-Statistics Update
            processing_time = time.time() - start_time
            self._update_meta_statistics(thought_id, strategy, analyses, processing_time)

            #Store thought process for learning
            self._store_thought_process(ThoughtProcess(
                thought_id=thought_id,
                original_query=query,
                strategy=strategy,
                confidence_score=sum(conf for _, conf, _ in analyses) / len(analyses),
                sub_questions=sub_questions,
                analyses=[analysis for analysis, _, _ in analyses],
                synthesis=final_response,
                processing_time=processing_time,
            ))

            self.logger.info(f"Advanced thinking process {thought_id} completed in {processing_time:.2f}s")

            return final_response

        except Exception as e:
            error_msg = f"I encountered an error while processing your question with advanced thinking: {e!s}"
            self.logger.error(f"Error in advanced thinking process {thought_id}: {e}")
            return error_msg

    def _generate_thought_id(self) -> str:
        """Generate a unique ID for a thought process."""
        return f"advanced_thought_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    def _update_meta_statistics(self, thought_id: str, strategy: ThinkingStrategy, analyses: List[Tuple[str, float, List[str]]], processing_time: float):
        """Update meta-cognitive statistics for learning."""
        self.meta_stats["total_thoughts"] += 1

        #Track strategy effectiveness
        avg_confidence = sum(conf for _, conf, _ in analyses) / len(analyses) if analyses else 0.5
        if strategy.value not in self.meta_stats["strategy_effectiveness"]:
            self.meta_stats["strategy_effectiveness"][strategy.value] = []
        self.meta_stats["strategy_effectiveness"][strategy.value].append(avg_confidence)

        #Track confidence accuracy (would need user feedback in real implementation)
        self.meta_stats["confidence_accuracy"].append(avg_confidence)

        #Track uncertainty resolution
        total_uncertainties = sum(len(uncertainties) for _, _, uncertainties in analyses)
        if total_uncertainties == 0:
            self.meta_stats["uncertainty_resolutions"] += 1

    def _store_thought_process(self, thought_process: ThoughtProcess):
        """Store thought process for learning and improvement."""
        if not self.capabilities["memory_storage"] or not self.config["enable_memory_storage"]:
            return

        try:
            self.memory_manager.add_memory_for_agent(
                agent_type=MemoryScope.THINKING_ENGINE,
                memory_type=MemoryType.THINKING_PROCESS,
                content=json.dumps({
                    "thought_id": thought_process.thought_id,
                    "query": thought_process.original_query,
                    "strategy": thought_process.strategy.value,
                    "confidence": thought_process.confidence_score,
                    "processing_time": thought_process.processing_time,
                    "sub_questions_count": len(thought_process.sub_questions),
                    "success": True,
                }),
                metadata={
                    "thought_type": "advanced_ai_thinking",
                    "strategy": thought_process.strategy.value,
                    "confidence": thought_process.confidence_score,
                    "timestamp": time.time(),
                },
            )
        except Exception as e:
            self.logger.warning(f"Failed to store thought process: {e}")

    #Integration methods for Atlas
    def __call__(self, query: str, available_tools: Dict[str, Callable] = None) -> str:
        """Main entry point for the advanced thinking tool."""
        return self.process_with_advanced_thinking(query, available_tools)

    def process_help_request(self, message: str, available_tools: Dict[str, Callable] = None) -> str:
        """Process help request with advanced thinking."""
        return self.process_with_advanced_thinking(message, available_tools)

    def integrate_with_atlas_help_mode(self, main_app) -> bool:
        """Integrate with Atlas help mode using intelligent mode detection."""
        try:
            if not hasattr(main_app, "_handle_help_mode"):
                self.logger.warning("Atlas app does not have _handle_help_mode method")
                return False

            #Import intelligent mode detector
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from intelligent_mode_detector import ChatMode, IntelligentModeDetector
                mode_detector = IntelligentModeDetector()
                self.logger.info("Intelligent mode detector loaded successfully")
            except ImportError as e:
                self.logger.warning(f"Could not load intelligent mode detector: {e}")
                #Fallback to simple keyword-based detection
                mode_detector = None

            original_handler = main_app._handle_help_mode

            def advanced_help_mode_handler(message: str, context) -> str:
                """Advanced help mode handler with intelligent mode detection."""

                if mode_detector:
                    #Use intelligent detection
                    detection_result = mode_detector.detect_chat_mode(message, context)

                    if detection_result.should_use_advanced:
                        self.logger.info(f"Using Advanced AI Thinking: {detection_result.reasoning}")

                        #Prepare enhanced tools
                        available_tools = {}
                        if hasattr(main_app, "code_reader"):
                            available_tools.update({
                                "semantic_search": lambda q: getattr(main_app.code_reader, "semantic_search", lambda x: f"Semantic search: {x}")(q),
                                "file_search": lambda q: getattr(main_app.code_reader, "search_in_files", lambda x: f"File search: {x}")(q),
                                "read_file": lambda f: getattr(main_app.code_reader, "read_file", lambda x: f"Read file: {x}")(f),
                                "grep_search": lambda q: getattr(main_app.code_reader, "search_in_files", lambda x: f"Grep search: {x}")(q),
                            })

                        if hasattr(main_app, "agent_manager") and hasattr(main_app.agent_manager, "memory_manager"):
                            memory_manager = main_app.agent_manager.memory_manager
                            available_tools["memory_analysis"] = lambda: f"Memory system analysis using {memory_manager.__class__.__name__}"

                        try:
                            return self.process_with_advanced_thinking(message, available_tools)
                        except Exception as e:
                            self.logger.error(f"Error in advanced thinking: {e}")
                            if detection_result.fallback_to_simple:
                                self.logger.info("Falling back to simple handler")
                                return original_handler(message, context)
                            return f"Sorry, I encountered an error while processing your advanced request: {e!s}"
                    else:
                        self.logger.debug(f"Using simple handler: {detection_result.reasoning}")
                        return original_handler(message, context)

                else:
                    #Fallback to simple keyword-based detection
                    message_lower = message.lower()

                    #Enhanced simple command detection
                    simple_commands = [
                        "read file", "show file", "list directory", "show tree", "tree",
                        "search for", "find functions", "info about", "metrics", "stats",
                        "search functions", "search classes", "usage of", "where is",
                    ]

                    #Check for exact simple commands first
                    is_simple_command = any(message_lower.startswith(cmd) for cmd in simple_commands)

                    if is_simple_command:
                        return original_handler(message, context)

                    #Enhanced advanced thinking triggers
                    advanced_keywords = [
                        "проаналізуй", "analyze", "що не так", "what's wrong", "what is wrong",
                        "як можна покращи", "how can improve", "як покращи", "how to improve",
                        "архітектур", "architecture", "як працює", "how does", "how it works",
                        "чому", "why", "порівня", "compare", "покращення", "improvement",
                        "проблематика", "problems", "міркування", "reasoning", "оптимізація", "optimization",
                    ]

                    #Check for advanced keywords
                    if any(keyword in message_lower for keyword in advanced_keywords):
                        self.logger.info("Using Advanced AI Thinking (fallback detection)")

                        #Prepare enhanced tools
                        available_tools = {}
                        if hasattr(main_app, "code_reader"):
                            available_tools.update({
                                "semantic_search": lambda q: getattr(main_app.code_reader, "semantic_search", lambda x: f"Semantic search: {x}")(q),
                                "file_search": lambda q: getattr(main_app.code_reader, "search_in_files", lambda x: f"File search: {x}")(q),
                                "read_file": lambda f: getattr(main_app.code_reader, "read_file", lambda x: f"Read file: {x}")(f),
                                "grep_search": lambda q: getattr(main_app.code_reader, "search_in_files", lambda x: f"Grep search: {x}")(q),
                            })

                        if hasattr(main_app, "agent_manager") and hasattr(main_app.agent_manager, "memory_manager"):
                            memory_manager = main_app.agent_manager.memory_manager
                            available_tools["memory_analysis"] = lambda: f"Memory system analysis using {memory_manager.__class__.__name__}"

                        try:
                            return self.process_with_advanced_thinking(message, available_tools)
                        except Exception as e:
                            self.logger.error(f"Error in advanced thinking (fallback): {e}")
                            return original_handler(message, context)

                    #Default to simple handler
                    return original_handler(message, context)

            #Replace the handler
            main_app._handle_help_mode = advanced_help_mode_handler
            main_app.advanced_ai_thinking_integration = True

            self.logger.info("Successfully integrated Advanced AI Thinking with Atlas help mode")
            return True

        except Exception as e:
            self.logger.error(f"Failed to integrate with Atlas help mode: {e}")
            return False


#Registration function for Atlas plugin system
def register(llm_manager=None, atlas_app=None, **kwargs):
    """Register the Advanced AI Thinking tool with Atlas."""
    try:
        #Get additional components
        memory_manager = None
        config_manager = None

        if "agent_manager" in kwargs:
            agent_manager = kwargs["agent_manager"]
            if hasattr(agent_manager, "memory_manager"):
                memory_manager = agent_manager.memory_manager

        try:
            from config_manager import ConfigManager
            config_manager = ConfigManager()
        except ImportError:
            pass

        #Create the advanced tool
        tool = AdvancedAIThinkingTool(
            llm_manager=llm_manager,
            memory_manager=memory_manager,
            config_manager=config_manager,
        )

        #Attempt integration
        integration_success = False
        if atlas_app:
            integration_success = tool.integrate_with_atlas_help_mode(atlas_app)

        logging.info("Advanced AI Thinking Tool registered successfully")
        logging.info(f"Available strategies: {[s.value for s in ThinkingStrategy]}")

        if integration_success:
            logging.info("Successfully integrated with Atlas help mode - Advanced thinking enabled")
        else:
            logging.info("Plugin registered but not integrated with help mode")

        return {
            "tools": [tool],
            "agents": [],
            "metadata": {
                "version": "3.0.0",
                "name": "Advanced AI Thinking",
                "description": "Sophisticated AI-driven thinking with meta-cognitive awareness",
                "capabilities": tool.capabilities,
                "strategies": [s.value for s in ThinkingStrategy],
                "platform_info": tool.platform_info,
                "integration_status": integration_success,
            },
        }

    except Exception as e:
        logging.exception(f"Failed to register Advanced AI Thinking plugin: {e}")
        import traceback
        logging.exception(f"Traceback: {traceback.format_exc()}")
        return {
            "tools": [],
            "agents": [],
            "metadata": {"error": str(e)},
        }


#Backward compatibility alias
EnhancedHelperSyncTellTool = AdvancedAIThinkingTool
