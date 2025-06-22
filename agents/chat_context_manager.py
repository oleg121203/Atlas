#!/usr/bin/env python3
"""
Chat Context Manager for Atlas

Manages different conversation modes and provides context-aware responses.
"""

import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .enhanced_memory_manager import EnhancedMemoryManager

logger = logging.getLogger(__name__)

class ChatMode(Enum):
    """Different modes of conversation with Atlas."""
    CASUAL_CHAT = "casual_chat"      #General conversation
    SYSTEM_HELP = "system_help"      #System assistance
    GOAL_SETTING = "goal_setting"    #Task specification
    TOOL_INQUIRY = "tool_inquiry"    #Tool-related questions
    STATUS_CHECK = "status_check"    #Status checking
    CONFIGURATION = "configuration"   #System configuration
    DEVELOPMENT = "development"      #Development mode (manual switching only)

class ModeControl(Enum):
    """Mode control types."""
    AUTO = "auto"         #Automatic detection
    MANUAL = "manual"     #Manual switching

@dataclass
class ChatContext:
    """Context information for a chat message."""
    mode: ChatMode
    confidence: float
    suggested_response_type: str
    context_keywords: List[str]
    requires_system_integration: bool
    control_type: ModeControl = ModeControl.AUTO  #How the mode was selected

class ChatContextManager:
    """Manages chat context and determines appropriate response modes."""

    def __init__(self, memory_manager: Optional[EnhancedMemoryManager] = None, llm_manager=None):
        self.conversation_history: List[Dict] = []
        self.current_session_context = {}

        #Enhanced memory integration
        self.memory_manager = memory_manager
        #Note: If no memory_manager is provided, some features will be disabled

        #LLM integration for intelligent mode detection
        self.llm_manager = llm_manager
        self.llm_mode_detection_enabled = llm_manager is not None

        #Mode control settings
        self.auto_mode_enabled = True
        self.manual_override_mode = None
        self.last_auto_detected_mode = None

        #Development mode settings
        self.development_mode_features = {
            "debug_logging": True,
            "backup_on_changes": True,
            "error_self_check": True,
            "capability_expansion": True,
            "experimental_features": True,
        }

        #Mode-specific memory settings
        self.mode_memory_config = {
            ChatMode.CASUAL_CHAT: {"ttl_days": 7, "max_context": 20},
            ChatMode.SYSTEM_HELP: {"ttl_days": 30, "max_context": 50},
            ChatMode.GOAL_SETTING: {"ttl_days": 90, "max_context": 100},
            ChatMode.TOOL_INQUIRY: {"ttl_days": 14, "max_context": 30},
            ChatMode.STATUS_CHECK: {"ttl_days": 3, "max_context": 10},
            ChatMode.CONFIGURATION: {"ttl_days": 365, "max_context": 50},
            ChatMode.DEVELOPMENT: {"ttl_days": 180, "max_context": 200},
        }

        #Initialize patterns and templates
        self._initialize_patterns()
        self._initialize_templates()

    # ------------------------------------------------------------------
    # Manual / auto mode helpers (legacy API expected by tests)
    # ------------------------------------------------------------------

    def set_manual_mode(self, mode: ChatMode) -> None:
        """Disable auto detection and force *mode* until toggled.

        Mirrors the behaviour expected by older unit-tests.
        """
        self.auto_mode_enabled = False
        self.manual_override_mode = mode

    def toggle_auto_mode(self) -> None:
        """Toggle auto-mode on/off (re-enabling clears manual override)."""
        self.auto_mode_enabled = not self.auto_mode_enabled
        if self.auto_mode_enabled:
            self.manual_override_mode = None

    @property
    def is_auto_mode(self) -> bool:
        """Check if auto mode is enabled."""
        return self.auto_mode_enabled

    @property
    def current_mode(self) -> ChatMode:
        """Get current active mode."""
        if not self.auto_mode_enabled and self.manual_override_mode:
            return self.manual_override_mode
        return self.last_auto_detected_mode or ChatMode.CASUAL_CHAT

    def _initialize_patterns(self):
        """Initialize mode detection patterns."""
        #Patterns for different modes
        self.mode_patterns = {
            ChatMode.CASUAL_CHAT: {
                "keywords": [
                    "hello", "hi", "hey", "good morning", "good evening", "good day",
                    "how are you", "how is it going", "what's up", "thanks", "thank you",
                    "please", "sorry", "excuse me", "nice", "good", "great", "awesome",
                    "weather", "today", "yesterday", "tomorrow", "weekend", "holiday",
                    "chat", "talk", "conversation", "discuss", "opinion", "think",
                    "like", "love", "enjoy", "favorite", "interesting", "cool",
                    "funny", "joke", "laugh", "smile", "happy", "sad", "excited",
                    "tired", "busy", "free", "time", "day", "night", "morning",
                    "afternoon", "evening", "week", "month", "year", "life",
                    "work", "job", "study", "learn", "read", "watch", "listen",
                    "music", "movie", "book", "food", "coffee", "tea", "drink",
                    "eat", "sleep", "rest", "relax", "travel", "vacation",
                ],
                "patterns": [
                    r"\b(hello|hi|hey|good\s+(?:morning|evening|day))\b",
                    r"\b(how\s+are\s+you|how\s+is\s+it\s+going|what\'?s\s+up)\b",
                    r"\b(thanks?|thank\s+you|please|sorry|excuse\s+me)\b",
                    r"\b(nice|good|great|awesome|cool|interesting)\b",
                    r"\b(weather|today|yesterday|tomorrow|weekend)\b",
                    r"\b(like|love|enjoy|favorite|think|opinion)\b",
                    r"\b(happy|sad|excited|tired|busy|free)\b",
                    r"\b(music|movie|book|food|coffee|tea|travel)\b",
                ],
            },

            ChatMode.SYSTEM_HELP: {
                "keywords": [
                    "help", "explain", "tutorial", "guide", "documentation",
                    "capabilities", "modes", "mode", "atlas", "system",
                    "tell me about", "what are", "show me", "describe",
                    "atlas capabilities", "atlas features", "atlas modes",
                    "about atlas", "atlas system", "development mode",
                    "your memory", "organized memory", "about yourself",
                    "your capabilities", "your features", "provider",
                    "memory system", "long-term memory", "short-term memory",
                    "how do you remember", "do you forget", "memory management",
                    "memory", "remember", "storage", "recall", "memorize",
                    "provided", "supported", "long-term", "organized", "direction",
                    "interested", "curious", "want to know", "wondering",
                    #Problem analysis keywords
                    "problem", "issue", "error", "bug", "fix", "solve", "investigate",
                    "analyze", "check", "review", "find problems", "find issues",
                    "code quality", "quality check", "find errors", "find bugs",
                    "debug", "troubleshoot", "examine", "inspect",
                    #Performance analysis keywords
                    "performance", "bottleneck", "optimization", "optimize",
                    "slow", "fast", "speed", "memory usage", "cpu usage",
                    "performance issues", "performance problems", "profiling",
                    "profile code", "analyze performance", "check performance",
                    #Dependency analysis keywords
                    "dependency", "dependencies", "architecture", "structure",
                    "dependency conflicts", "architectural problems", "imports",
                    "circular dependencies", "dependency graph", "modules",
                    "component dependencies", "architecture analysis",
                    #Technical implementation keywords
                    "implementation", "how implemented", "where implemented",
                    "code structure", "architecture", "how works", "how does it work",
                    "realized", "implemented", "possibilities", "software",
                    #Code analysis keywords - most specific ones only
                    "rebuild index", "update index", "show file", "analyze file",
                    "code analysis", "structure analysis",
                ],
                "patterns": [
                    r"\b(explain\s+(?:atlas|system)|help\s+(?:with|me)\s+(?:atlas|system))\b",
                    r"\b(atlas\s+(?:capabilities|features|modes|system))\b",
                    r"\b(tell\s+me\s+about\s+(?:atlas|system|yourself))\b",
                    r"\b(what\s+(?:are|is)\s+(?:atlas|your)\s+(?:capabilities|features|modes))\b",
                    r"\b(development\s+mode|your\s+memory|organized\s+memory)\b",
                    r"\b(rebuild\s+index|analyze\s+file|code\s+analysis)\b",
                    r"\b(about\s+(?:atlas|system|yourself))\b",
                    r"\b(memory\s+system|long-term\s+memory|how\s+(?:do\s+)?you\s+remember)\b",
                    r"\b(how\s+(?:is|does)\s+(?:your|atlas)\s+memory\s+(?:work|organized))\b",
                    r"\b((?:do\s+you\s+have|is\s+there)\s+(?:memory|storage))\b",
                    r"\b(long-term\s+(?:memory|storage)|organized\s+by\s+(?:direction|context))\b",
                    r"\b(how\s+(?:implemented|realized|works)|where\s+implemented)\b",
                    r"\b((?:software|program)\s+(?:possibilities|capabilities))\b",
                    r"\b(find\s+(?:problems|issues|errors|bugs)|check\s+(?:quality|code))\b",
                    r"\b(analyze\s+code|review\s+code|investigate\s+(?:problems|issues))\b",
                    #Performance analysis patterns
                    r"\b(performance\s+(?:issues|problems|analysis|check))\b",
                    r"\b(check\s+(?:for\s+)?performance|analyze\s+performance)\b",
                    r"\b((?:memory|cpu)\s+usage|bottleneck|optimization|profile)\b",
                    #Dependency analysis patterns
                    r"\b(dependency\s+(?:conflicts|analysis|graph))\b",
                    r"\b(architectural?\s+(?:problems|analysis|issues))\b",
                    r"\b(investigate\s+(?:dependency|dependencies|architecture))\b",
                    r"\b(circular\s+(?:dependency|dependencies|imports))\b",
                ],
            },

            ChatMode.GOAL_SETTING: {
                "keywords": [
                    "take screenshot", "click on", "open", "run", "execute",
                    "find", "search", "copy", "paste", "type", "press",
                    "create", "delete", "move", "automation", "automate",
                    "do", "make", "perform", "complete", "finish", "start",
                    "stop", "close", "launch", "capture", "screenshot",
                ],
                "patterns": [
                    r"\b(take\s+a?\s*screenshot|click\s+(?:on|at)|open\s+\w+|run\s+\w+)\b",
                    r"\b(do\s+(?:this|that)|make\s+(?:this|that)|perform\s+(?:this|that))\b",
                    r"\b(automate\s+\w+|execute\s+\w+|launch\s+\w+)\b",
                ],
            },

            ChatMode.TOOL_INQUIRY: {
                "keywords": [
                    "tools", "available", "list", "what tools", "functions",
                    "instruments", "commands", "capabilities", "features",
                    "what can", "show tools", "list tools", "available functions",
                    "show me", "what functions", "tool list",
                    "what tools", "tools available", "functions available", "what functions",
                    "show tools", "what do you have", "what can you do", "possibilities",
                ],
                "patterns": [
                    r"\b(what\s+tools|available\s+tools|list\s+(?:of\s+)?tools)\b",
                    r"\b(show\s+(?:me\s+)?(?:tools|functions|capabilities))\b",
                    r"\b(what\s+(?:can\s+)?(?:functions|tools|commands))\b",
                    r"\b(what\s+tools|tools\s+(?:do\s+)?you\s+have|what\s+can\s+you\s+do)\b",
                    r"\b(show\s+tools|what\s+functions|possibilities)\b",
                ],
            },

            ChatMode.STATUS_CHECK: {
                "keywords": [
                    "status", "running", "working", "progress", "state",
                    "health", "performance", "current state", "how is",
                    "what is happening", "what is going on", "system status",
                    "is everything", "all good", "working properly",
                    "functioning", "operational", "active", "idle",
                    "your status", "system health", "how are you working",
                ],
                "patterns": [
                    r"\b(what(?:\'s|\s+is)\s+(?:the\s+)?status|how\s+(?:is|are)\s+things)\b",
                    r"\b(is\s+(?:everything|atlas|system)\s+(?:working|running|ok))\b",
                    r"\b(current\s+(?:status|state)|system\s+health)\b",
                    r"\b(what\s+is\s+your\s+status|how\s+are\s+you\s+(?:working|running))\b",
                ],
            },

            ChatMode.CONFIGURATION: {
                "keywords": [
                    "settings", "configure", "setup", "options", "preferences",
                    "config", "api key", "provider", "change settings",
                    "modify", "adjust", "customize", "configuration",
                    "parameters", "set up", "installation", "initialization",
                ],
                "patterns": [
                    r"\b(change\s+settings|configure\s+\w+|setup\s+\w+)\b",
                    r"\b(modify\s+(?:settings|config)|adjust\s+\w+)\b",
                    r"\b(api\s+key|provider\s+setup|installation)\b",
                ],
            },
        }

    def _initialize_templates(self):
        """Initialize response templates."""
        #Response templates
        self.response_templates = {
            ChatMode.SYSTEM_HELP: self._generate_help_response,
            ChatMode.GOAL_SETTING: self._generate_goal_response,
            ChatMode.TOOL_INQUIRY: self._generate_tool_response,
            ChatMode.STATUS_CHECK: self._generate_status_response,
            ChatMode.CONFIGURATION: self._generate_config_response,
            ChatMode.CASUAL_CHAT: self._generate_casual_response,
            ChatMode.DEVELOPMENT: self._generate_development_response,
        }

    def analyze_message(self, message: str, user_context: Dict = None) -> ChatContext:
        """Analyze a message and determine its context using intelligent LLM classification."""
        # First check if user wants to manually switch modes
        if self.set_mode_by_intent(message):
            # Return context with the manually set mode
            return ChatContext(
                mode=self.manual_override_mode,
                confidence=1.0,
                suggested_response_type=self._get_response_type(self.manual_override_mode),
                context_keywords=[],
                requires_system_integration=self.manual_override_mode in [
                    ChatMode.GOAL_SETTING,
                    ChatMode.STATUS_CHECK,
                    ChatMode.TOOL_INQUIRY,
                    ChatMode.DEVELOPMENT,
                ],
                control_type=ModeControl.MANUAL,
            )
        
        #If in manual mode, use the override mode
        if not self.auto_mode_enabled and self.manual_override_mode:
            return ChatContext(
                mode=self.manual_override_mode,
                confidence=1.0,  #Manual mode has 100% confidence
                suggested_response_type=self._get_response_type(self.manual_override_mode),
                context_keywords=[],
                requires_system_integration=self.manual_override_mode in [
                    ChatMode.GOAL_SETTING,
                    ChatMode.STATUS_CHECK,
                    ChatMode.TOOL_INQUIRY,
                    ChatMode.DEVELOPMENT,
                ],
                control_type=ModeControl.MANUAL,
            )

        # Primary method: Try LLM-based intelligent classification first
        if self.llm_mode_detection_enabled:
            llm_mode, llm_confidence = self._classify_message_with_llm(message)
            if llm_mode and llm_confidence > 0.4:  # Use LLM result if confident enough
                self.last_auto_detected_mode = llm_mode
                
                # Extract context keywords using traditional method for the detected mode
                message_lower = message.lower()
                context_keywords = []
                if llm_mode in self.mode_patterns:
                    patterns = self.mode_patterns[llm_mode]
                    context_keywords = [kw for kw in patterns["keywords"]
                                      if kw.lower() in message_lower]
                
                requires_integration = llm_mode in [
                    ChatMode.GOAL_SETTING,
                    ChatMode.STATUS_CHECK,
                    ChatMode.TOOL_INQUIRY,
                ]
                
                return ChatContext(
                    mode=llm_mode,
                    confidence=llm_confidence,
                    suggested_response_type=self._get_response_type(llm_mode),
                    context_keywords=context_keywords,
                    requires_system_integration=requires_integration,
                    control_type=ModeControl.AUTO,
                )

        # Fallback: Use traditional keyword/pattern-based detection
        return self._analyze_message_traditional(message, user_context)
        
    def _analyze_message_traditional(self, message: str, user_context: Dict = None) -> ChatContext:

        #Auto mode - translate to English for analysis if needed
        message_for_analysis = self._simple_translate_to_english(message)
        message_lower = message_for_analysis.lower()
        scores = {}

        #Calculate scores for each mode (except DEVELOPMENT which is manual-only)
        analyzable_modes = [mode for mode in self.mode_patterns.keys()
                           if mode != ChatMode.DEVELOPMENT]

        for mode in analyzable_modes:
            patterns = self.mode_patterns[mode]
            score = 0.0

            #Check keywords with higher weight for exact matches
            keyword_matches = 0
            for keyword in patterns["keywords"]:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    #Bonus for exact word boundaries
                    if f" {keyword.lower()} " in f" {message_lower} ":
                        score += 0.1

            if keyword_matches > 0:
                #Equal weight for all modes - no special preference for SYSTEM_HELP
                score += (keyword_matches / len(patterns["keywords"])) * 0.6

            #Check regex patterns with equal weight
            pattern_matches = sum(1 for pattern in patterns["patterns"]
                                if re.search(pattern, message_lower, re.IGNORECASE))
            if pattern_matches > 0:
                score += (pattern_matches / len(patterns["patterns"])) * 0.4

            scores[mode] = score

        #Find the best match
        best_mode = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_mode]

        #Special handling for memory-related questions - boost confidence
        memory_indicators = ["memory", "remember", "storage", "recall", "organized", "long-term", "provided"]
        if any(indicator in message_lower for indicator in memory_indicators):
            if best_mode == ChatMode.SYSTEM_HELP:
                confidence = min(0.9, confidence + 0.3)  #Boost confidence for memory questions

        #Special handling for casual greetings and short messages
        if len(message.strip()) <= 20 and any(greeting in message_lower for greeting in [
            "hi", "hello", "hey", "good", "morning", "evening",
        ]):
            best_mode = ChatMode.CASUAL_CHAT
            confidence = 0.8

        #Default to casual chat if confidence is too low
        if confidence < 0.15:  #Lowered threshold
            best_mode = ChatMode.CASUAL_CHAT
            confidence = 0.5

        #Store last auto-detected mode
        self.last_auto_detected_mode = best_mode

        #Determine context keywords
        context_keywords = []
        for mode, patterns in self.mode_patterns.items():
            if mode == best_mode:
                context_keywords = [kw for kw in patterns["keywords"]
                                  if kw.lower() in message_lower]
                break

        #Determine if system integration is required
        requires_integration = best_mode in [
            ChatMode.GOAL_SETTING,
            ChatMode.STATUS_CHECK,
            ChatMode.TOOL_INQUIRY,
        ]

        return ChatContext(
            mode=best_mode,
            confidence=confidence,
            suggested_response_type=self._get_response_type(best_mode),
            context_keywords=context_keywords,
            requires_system_integration=requires_integration,
            control_type=ModeControl.AUTO,
        )

    def get_current_mode_info(self) -> Dict:
        """Get current mode control information."""
        return {
            "auto_enabled": self.auto_mode_enabled,
            "manual_override": self.manual_override_mode.value if self.manual_override_mode else None,
            "last_auto_mode": self.last_auto_detected_mode.value if self.last_auto_detected_mode else None,
            "development_features": self.development_mode_features if self.manual_override_mode == ChatMode.DEVELOPMENT else None,
        }

    def update_conversation_history(self, message: str, response: str, context: "ChatContext"):
        """
        Update the conversation history.

        This is a placeholder implementation. In a real scenario, this would
        interact with a more sophisticated memory or logging system.
        """
        #This is a simplified implementation. A more robust solution would involve
        #a dedicated memory manager, as hinted at in the class's docstrings.
        history_entry = {
            "timestamp": time.time(),
            "message": message,
            "response": response,
            "mode": context.mode.value,
            "confidence": context.confidence,
        }
        self.conversation_history.append(history_entry)

        #Optional: Limit history size
        if len(self.conversation_history) > 100: #Keep last 100 exchanges
            self.conversation_history.pop(0)

    def analyze_message_with_mode_control(self, message: str, system_info: Dict = None) -> ChatContext:
        """Analyze message respecting mode control settings."""
        if not self.auto_mode_enabled and self.manual_override_mode:
            #Manual mode is active
            if self.manual_override_mode == ChatMode.DEVELOPMENT:
                return self._create_development_context(message)
            return self._create_manual_context(message, self.manual_override_mode)
        #Auto mode - use normal analysis
        context = self.analyze_message(message, system_info)
        self.last_auto_detected_mode = context.mode
        return context

    def _create_development_context(self, message: str) -> ChatContext:
        """Create context for development mode."""
        return ChatContext(
            mode=ChatMode.DEVELOPMENT,
            confidence=1.0,
            suggested_response_type="development_focused",
            context_keywords=["development", "debug", "experimental"],
            requires_system_integration=True,
            control_type=ModeControl.MANUAL,
        )

    def _create_manual_context(self, message: str, mode: ChatMode) -> ChatContext:
        """Create context for manual mode override."""
        return ChatContext(
            mode=mode,
            confidence=1.0,
            suggested_response_type=self._get_response_type(mode),
            context_keywords=[],
            requires_system_integration=mode in [ChatMode.GOAL_SETTING, ChatMode.STATUS_CHECK, ChatMode.TOOL_INQUIRY],
            control_type=ModeControl.MANUAL,
        )

    def _get_response_type(self, mode: ChatMode) -> str:
        """Get the appropriate response type for a mode."""
        response_types = {
            ChatMode.CASUAL_CHAT: "conversational",
            ChatMode.SYSTEM_HELP: "informational",
            ChatMode.GOAL_SETTING: "action_oriented",
            ChatMode.TOOL_INQUIRY: "technical_list",
            ChatMode.STATUS_CHECK: "status_report",
            ChatMode.CONFIGURATION: "guidance",
            ChatMode.DEVELOPMENT: "development_focused",
        }
        return response_types.get(mode, "conversational")

    def generate_response_prompt(self, context: ChatContext, message: str,
                               system_info: Dict = None) -> str:
        """Generate an appropriate system prompt based on context."""
        return self.response_templates[context.mode](context, message, system_info)

    def _generate_help_response(self, context: ChatContext, message: str,
                              system_info: Dict = None) -> str:
        """Generate help-focused response prompt."""
        #Use translated message for detection
        message_for_analysis = self._simple_translate_to_english(message)
        message_lower = message_for_analysis.lower()

        #Detect specific question patterns for direct answers
        memory_keywords = ["memory", "remember", "memorize", "store", "recall",
                          "storage", "long-term", "organized", "direction", "interested"]
        tools_keywords = ["tools", "instruments", "functions", "capabilities"]
        modes_keywords = ["modes", "mode"]

        #Direct memory question detection
        if any(word in message_lower for word in memory_keywords):
            return f"""You are Atlas in System Help mode. The user is asking about the memory system implementation.

User's question: "{message}"

Use your COMPREHENSIVE ANALYSIS TOOLS to investigate the memory implementation:

1. **Core Analysis Tools:**
   - `code_reader_tool`: Analyze memory-related files with AST analysis
   - `professional_analyzer`: Detect memory issues and patterns
   - `dependency_analyzer`: Check memory component dependencies and architecture
   - `performance_profiler`: Analyze memory performance and bottlenecks
   - `semantic_search`: Find memory-related code
   - `file_search`: Locate memory implementation files
   - `grep_search`: Search for memory patterns

2. **Focus your investigation on:**
   - Find `enhanced_memory_manager.py` and analyze its structure
   - Locate ChromaDB integration code
   - Check memory configuration files
   - Analyze memory retention policies
   - Review memory categorization logic
   - Check for memory performance issues and bottlenecks

3. **Provide specific technical details:**
   - Exact file paths and line numbers
   - Class names and method signatures
   - Memory storage mechanisms
   - Configuration options and defaults
   - Code snippets showing implementation
   - Dependency analysis and architectural insights
   - Performance characteristics and optimization opportunities

Start by using `code_reader_tool` to analyze the memory manager files, then use `professional_analyzer` and `dependency_analyzer` to identify any potential issues."""

        #Direct tools question detection
        if any(word in message_lower for word in tools_keywords):
            return f"""You are Atlas in System Help mode. The user is asking about tools/functions implementation.

User's question: "{message}"

Use your COMPREHENSIVE ANALYSIS ARSENAL to investigate tool implementation:

1. **Advanced Analysis Tools:**
   - `code_reader_tool`: Analyze tool structure with AST and metrics
   - `professional_analyzer`: Detect tool quality issues and improvements
   - `dependency_analyzer`: Analyze tool dependencies and architecture
   - `performance_profiler`: Check tool performance and optimization opportunities
   - `file_search`: Find tool files in tools/ and plugins/ directories
   - `semantic_search`: Search for tool patterns and usage

2. **Investigation focus:**
   - Explore `tools/` directory structure and dependencies
   - Analyze `plugins/` directory for plugin tools
   - Check agent tools in `agents/` directory
   - Review tool registration and management code
   - Assess tool performance characteristics
   - Identify architectural patterns and dependencies

3. **Provide comprehensive technical details:**
   - Tool categories and their file locations
   - Implementation patterns and architectures
   - Tool registration mechanisms
   - Performance analysis and bottlenecks
   - Dependency graphs and architectural insights
   - Usage examples from codebase
   - Any issues or improvements identified

Start by using `file_search` to explore tool directories, then `code_reader_tool` and `dependency_analyzer` to analyze key tool implementations."""

        #Direct modes question detection
        if any(word in message_lower for word in modes_keywords):
            return f"""You are Atlas. The user is asking about your operating modes.

User's question: "{message}"

Explain the different conversation modes directly:
- 💬 Casual Chat - General conversation
- ❓ System Help - Information about Atlas
- 🎯 Goal Setting - Task execution
- � Tool Inquiry - Available functions
- 📊 Status Check - System monitoring  
- ⚙️ Configuration - Settings management
- 🔧 Development Mode - Advanced access

Be direct and focused on modes only."""

        #General help - use professional code analysis for comprehensive understanding
        #Check if this is a problem analysis or investigation request
        investigation_keywords = ["problem", "issue", "error", "bug", "fix", "solve", "investigate", "analyze", "check", "review", "find"]
        is_investigation = any(keyword in message_lower for keyword in investigation_keywords)

        if is_investigation:
            return f"""You are Atlas Professional Code Analyzer. The user needs expert investigation and problem-solving.

User's question: "{message}"

ACTIVATE PROFESSIONAL ANALYSIS MODE:

1. 🔍 COMPREHENSIVE INVESTIGATION:
   - Use semantic_search to understand the problem domain
   - Use file_search to locate relevant code files
   - Use grep_search to find error patterns or issues
   - Use read_file to examine code implementation details

2. 🎯 ADVANCED PROBLEM DETECTION PROTOCOL:
   - Use `professional_analyzer`: Scan for security vulnerabilities and code quality issues
   - Use `dependency_analyzer`: Identify dependency conflicts and architectural violations
   - Use `performance_profiler`: Find performance bottlenecks and memory issues
   - Use `code_reader_tool`: Deep AST analysis for complex patterns
   - Detect resource leaks and optimization opportunities
   - Check architecture compliance and best practices

3. 💡 SOLUTION ENGINEERING:
   - Provide specific, actionable fixes with code examples
   - Prioritize solutions by impact and effort
   - Reference exact file locations and line numbers
   - Include risk assessment for each recommendation
   - Provide performance optimization strategies
   - Suggest architectural improvements

4. 📊 PROFESSIONAL REPORTING:
   - Executive summary of findings
   - Technical details with evidence
   - Dependency analysis and architectural insights
   - Performance metrics and optimization recommendations
   - Implementation roadmap with priorities
   - Quality metrics and improvement suggestions

Begin immediate analysis using ALL AVAILABLE advanced code investigation tools. Be thorough, professional, and solution-oriented."""

        return f"""You are Atlas in System Help mode. The user is asking for information about the system.

User's question: "{message}"

As a System Help expert, you have FULL ACCESS to analyze the entire Atlas codebase with ADVANCED TOOLS. Your role is to:

1. INVESTIGATE the codebase using your comprehensive toolkit:
   - Use `semantic_search` to find relevant code patterns
   - Use `file_search` to locate specific files and directories
   - Use `read_file` to examine implementations in detail
   - Use `grep_search` to find specific patterns and usage
   - Use `code_reader_tool` for deep AST analysis and code metrics
   - Use `professional_analyzer` for issue detection and quality assessment
   - Use `dependency_analyzer` for architectural and dependency analysis
   - Use `performance_profiler` for performance analysis and optimization

2. PROVIDE COMPREHENSIVE TECHNICAL EXPERTISE:
   - Analyze code structure and implementation details with AST analysis
   - Identify potential issues, vulnerabilities, and improvements
   - Explain architectural dependencies and component interactions
   - Assess performance characteristics and optimization opportunities
   - Reference specific files, classes, and methods with evidence
   - Provide metrics, complexity analysis, and quality assessments

3. ANSWER WITH PROFESSIONAL AUTHORITY:
   - Give specific file locations with line numbers
   - Show actual code snippets when relevant
   - Explain implementation details with technical depth
   - Provide architectural insights and dependency analysis
   - Include performance analysis and optimization recommendations
   - Deliver professional-grade code analysis and insights

Start by analyzing the relevant parts of the codebase using your FULL ARSENAL of advanced analysis tools to answer the user's question comprehensively and professionally."""

    def _generate_goal_response(self, context: ChatContext, message: str,
                              system_info: Dict = None) -> str:
        """Generate goal-oriented response prompt."""
        available_tools = system_info.get("tools", []) if system_info else []
        available_agents = system_info.get("agents", []) if system_info else []

        return f"""You are Atlas, an autonomous computer assistant. The user wants to accomplish a task.

User's goal: "{message}"
Context keywords: {', '.join(context.context_keywords)}

This appears to be a task request. Respond by:
1. Acknowledging that you understand this as a goal
2. Briefly explaining how you'll approach it
3. Mentioning which tools/agents you'll likely use
4. Asking for clarification if needed

Available tools: {', '.join(available_tools[:10])}{'...' if len(available_tools) > 10 else ''}
Available agents: {', '.join(available_agents)}

Format your response to be encouraging and action-oriented. Start with "🎯 I understand you want to..." """

    def _generate_tool_response(self, context: ChatContext, message: str,
                              system_info: Dict = None) -> str:
        """Generate tool inquiry response prompt."""
        #Use translated message for better detection
        message_for_analysis = self._simple_translate_to_english(message)
        message_lower = message_for_analysis.lower()

        #Check if this is a technical implementation question about tools
        implementation_keywords = ["implemented", "realized", "where", "how", "code", "files"]
        is_technical_question = any(keyword in message_lower for keyword in implementation_keywords)

        if is_technical_question:
            return f"""You are Atlas in Tool Inquiry mode with comprehensive analysis capabilities. The user is asking about tool implementation details.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

ACTIVATE COMPREHENSIVE TOOL ANALYSIS using your advanced arsenal:

1. **Advanced Analysis Tools Available:**
   - `code_reader_tool`: Deep AST analysis and code metrics
   - `professional_analyzer`: Quality assessment and issue detection
   - `dependency_analyzer`: Architectural and dependency analysis
   - `performance_profiler`: Performance analysis and optimization
   - `semantic_search`: Intelligent code pattern search
   - `file_search`: Structured file exploration
   - `grep_search`: Pattern-based code search

2. **Investigation Protocol:**
   - Search for tool-related files and structures in tools/ directory
   - Find agent files in agents/ directory that implement tools
   - Analyze plugin systems and tool creators with AST analysis
   - Check tool registration and management code
   - Assess tool performance characteristics and dependencies
   - Map tool architecture and component relationships

3. **Provide COMPREHENSIVE technical details:**
   - Exact file locations where tools are defined
   - Class names and method signatures with complexity analysis
   - Tool dependency graphs and architectural patterns
   - Performance characteristics and optimization opportunities
   - How tools are registered and integrated
   - Tool categories and their organizational structure
   - Quality assessment and potential improvements

Use your FULL ARSENAL of analysis tools to gather comprehensive information. Provide professional-grade technical details with actual code references, performance insights, and architectural analysis."""

        #Standard tool list for non-technical questions
        available_tools = system_info.get("tools", []) if system_info else []
        return f"""You are Atlas, an autonomous computer assistant. The user is asking about your available tools.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

**ATLAS TOOLBOX**

**System Tools:** {', '.join(available_tools) if available_tools else 'Standard system tools available'}

**Advanced Analysis Arsenal:**
- 🔍 **code_reader_tool**: Deep code analysis with AST parsing and metrics
- 🛡️ **professional_analyzer**: Quality assessment and issue detection
- 🔧 **dependency_analyzer**: Architectural and dependency analysis
- ⚡ **performance_profiler**: Performance bottlenecks and optimization
- 🔎 **semantic_search**: Intelligent codebase exploration
- 📁 **file_search**: Structured file system navigation
- 🔍 **grep_search**: Pattern-based code searching

**Capabilities:**
- Comprehensive code analysis and quality assessment
- Architectural investigation and dependency mapping
- Performance profiling and optimization recommendations
- Security vulnerability detection
- Professional-grade technical documentation

If you need specific tool information or want to see tools in action, just ask! I can provide detailed technical analysis using these advanced capabilities."""

    def _generate_status_response(self, context: ChatContext, message: str,
                                  system_info: Dict = None) -> str:
        """Generate status check response prompt."""
        system_health = system_info.get("health", {}) if system_info else {}
        active_processes = system_info.get("processes", []) if system_info else []

        return f"""You are Atlas, an autonomous computer assistant. The user is asking for a status update.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

**ATLAS STATUS REPORT**

**System Health:**
- **CPU Usage:** {system_health.get('cpu_usage', 'N/A')}
- **Memory Usage:** {system_health.get('memory_usage', 'N/A')}
- **Disk Space:** {system_health.get('disk_space', 'N/A')}

**Active Processes:**
{', '.join(active_processes) if active_processes else 'No major processes active.'}

Provide a concise summary of the current system status. Be reassuring and clear.
"""

    def _generate_config_response(self, context: ChatContext, message: str,
                                system_info: Dict = None) -> str:
        """Generate configuration guidance response prompt."""
        return f"""You are Atlas. The user is asking about configuration or settings.

User's query: "{message}"
Provide guidance on how to configure the requested settings.
"""

    def _generate_casual_response(self, context: ChatContext, message: str,
                                system_info: Dict = None) -> str:
        """Generate a casual conversational response."""
        return f"""You are Atlas, a friendly autonomous computer assistant. The user is having a casual conversation.

User's message: "{message}"

Respond naturally and conversationally. Be warm, friendly, and personable. Don't mention tools or capabilities unless directly asked. Focus on the human connection and respond to what they're actually saying.

If they're greeting you or asking your name, introduce yourself briefly and warmly. If they're sharing something about themselves, show interest and respond appropriately."""

    def _generate_development_response(self, context: ChatContext, message: str,
                                     system_info: Dict = None) -> str:
        """Generate a development-focused response."""
        return f"""You are Atlas in Development Mode.

User's command: "{message}"
Acknowledge the development command and proceed with execution.
"""

    def _simple_translate_to_english(self, message: str) -> str:
        """Simple translation for testing purposes."""
        #Basic translation mapping for common phrases
        translations = {
            "привіт": "hello",
            "привет": "hello",
            "друже": "friend",
            "як тебе звати": "what is your name",
            "як справи": "how are you",
            "мене звати": "my name is",
            "мене цікавить": "i am interested",
            "мене": "me",
            "розкажи": "tell me about explain",
            "розкажи про": "tell me about explain",
            "чи забезпечена": "is there provided",
            "забезпечена": "provided supported",
            "в тебе": "do you have",
            "у тебе": "do you have",
            "пам'ять": "memory storage",
            "памяті": "memory storage",
            "довгострокова": "long-term",
            "довгостроковій": "long-term",
            "які у тебе": "what do you have what tools",
            "інструменти": "tools instruments",
            "які інструменти": "what tools what instruments",
            "що можеш": "what can you do",
            "можливості": "capabilities possibilities features",
            "даного": "this software",
            "програмного забезпечення": "software system",
            "по": "about",
            "де": "where implemented",
            "як": "how implemented",
            "реалізовано": "implemented realized",
            "реалізовані": "implemented realized",
            "і": "and",
            "ПО": "software system",
            "працює": "works how does it work",
            "система": "system implementation",
            "atlas": "atlas system",
            "проблема": "problem issue",
            "помилка": "error bug",
            "виправити": "fix solve",
            "дослідити": "investigate analyze",
            "перевірити": "check review",

            "проблеми": "problems issues",
            "рішення": "solutions fixes",
            "перевір": "check analyze review investigate",
            "якість": "quality",
            "коду": "code",
            "код": "code analyze",
            "помилки": "errors bugs issues problems",
            #Problem investigation keywords
            "проблеми": "problems issues",
            "проблема": "problem issue",
            "помилки": "errors bugs",
            "помилка": "error bug",
            "виправити": "fix solve",
            "знайти": "find analyze",
            "дослідити": "investigate analyze",
            "перевірити": "check review",
            "аналізувати": "analyze investigate",
            "чому не працює": "why not working",
            "не працює": "not working",
            "баг": "bug error",
        }

        message_lower = message.lower()
        translated = message_lower

        #Apply translations in order of specificity (longer phrases first)
        sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)

        for ukrainian, english in sorted_translations:
            translated = translated.replace(ukrainian, english)

        return translated

    def format_bold(self, text: str) -> str:
        """
        Format text as bold
        
        Args:
            text: Text to format
            
        Returns:
            Text formatted as bold (wrapped in ** markdown)
        """
        return f"**{text}**"

    def format_italic(self, text: str) -> str:
        """
        Format text as italic
        
        Args:
            text: Text to format
            
        Returns:
            Text formatted as italic (wrapped in * markdown)
        """
        return f"*{text}*"

    def format_underline(self, text: str) -> str:
        """
        Format text as underlined
        
        Args:
            text: Text to format
            
        Returns:
            Text formatted as underlined (wrapped in __ markdown)
        """
        return f"__{text}__"

    def format_code(self, text: str) -> str:
        """
        Format text as inline code
        
        Args:
            text: Text to format
            
        Returns:
            Text formatted as inline code (wrapped in ` markdown)
        """
        return f"`{text}`"

    def format_code_block(self, text: str, language: str = "") -> str:
        """
        Format text as a code block
        
        Args:
            text: Text to format
            language: Optional language for syntax highlighting
            
        Returns:
            Text formatted as a code block (wrapped in ``` markdown)
        """
        return f"```{language}\n{text}\n```"

    def format_list(self, items: List[str], ordered: bool = False) -> str:
        """
        Format items as a list
        
        Args:
            items: List of items to format
            ordered: If True, create an ordered list, otherwise unordered
            
        Returns:
            Formatted list as markdown
        """
        result = []
        for i, item in enumerate(items, 1):
            if ordered:
                result.append(f"{i}. {item}")
            else:
                result.append(f"- {item}")
        return "\n".join(result)

    def format_quote(self, text: str) -> str:
        """
        Format text as a quote
        
        Args:
            text: Text to format
            
        Returns:
            Text formatted as a quote (prefixed with > markdown)
        """
        lines = text.split("\n")
        return "\n".join([f"> {line}" for line in lines])

    def format_link(self, text: str, url: str) -> str:
        """
        Format text as a hyperlink
        
        Args:
            text: Display text for the link
            url: URL for the link
            
        Returns:
            Text formatted as a markdown link
        """
        return f"[{text}]({url})"

    def _classify_message_with_llm(self, message: str) -> tuple[ChatMode, float]:
        """Use LLM to intelligently classify message intent and determine chat mode."""
        if not self.llm_manager:
            return None, 0.0
            
        try:
            classification_prompt = f'''
Analyze the following user message and determine its intent for classifying the conversation mode with AI assistant Atlas.

Message: "{message}"

Available modes:
1. CASUAL_CHAT - general conversation, greetings, small talk, mood questions
2. SYSTEM_HELP - requests about Atlas capabilities, help, instructions, "how does it work" questions
3. GOAL_SETTING - tasks to execute, commands, requests to do something specific
4. TOOL_INQUIRY - questions about tools, plugins, functions
5. STATUS_CHECK - status verification, monitoring, diagnostics
6. CONFIGURATION - settings, configuration, parameter changes

Analyze the context and motive of the message. Special attention:
- Requests to switch modes (help mode requests, assistant queries, etc.) = SYSTEM_HELP
- Tasks to execute actions (open, do, execute, perform actions, find, search, navigate) = GOAL_SETTING
- Questions about finding, searching, or navigating to something = GOAL_SETTING
- General conversations, emotions, greetings = CASUAL_CHAT

Key words for GOAL_SETTING: open, find, search, navigate, go to, show, display, get, fetch, download, upload, create, delete, run, execute

Respond with only the following JSON structure:
{
    "mode": "GOAL_SETTING",
    "confidence": 0.95,
    "reasoning": "This is a task request to perform a specific action"
}'''

            messages = [{"role": "user", "content": classification_prompt}]
            result = self.llm_manager.chat(messages)
            
            if result and result.response_text:
                import json
                import re
                
                try:
                    # Clean and normalize the response text
                    response_text = result.response_text.strip()
                    logger.debug(f"LLM response: {response_text[:200]}...")
                    
                    # Extract JSON using a simpler but effective regex
                    json_pattern = r'\{[^{}]*\}'
                    json_matches = re.finditer(json_pattern, response_text, re.DOTALL)
                    
                    # Try different JSON candidates
                    for match in json_matches:
                        try:
                            json_text = match.group(0)
                            classification = json.loads(json_text)
                            
                            # Validate required fields
                            if all(key in classification for key in ['mode', 'confidence']):
                                mode_name = classification['mode'].strip().upper()
                                confidence = float(classification['confidence'])
                                
                                # Map mode name to ChatMode enum
                                mode_mappings = {
                                    'CASUAL_CHAT': ChatMode.CASUAL_CHAT,
                                    'SYSTEM_HELP': ChatMode.SYSTEM_HELP,
                                    'GOAL_SETTING': ChatMode.GOAL_SETTING,
                                    'TOOL_INQUIRY': ChatMode.TOOL_INQUIRY,
                                    'STATUS_CHECK': ChatMode.STATUS_CHECK,
                                    'CONFIGURATION': ChatMode.CONFIGURATION,
                                }
                                
                                # Try direct mapping first
                                if mode_name in mode_mappings:
                                    return mode_mappings[mode_name], confidence
                                    
                                # Try partial matching
                                for key, mode in mode_mappings.items():
                                    if key.replace('_', '') in mode_name.replace('_', ''):
                                        return mode, confidence
                                        
                        except (json.JSONDecodeError, ValueError):
                            continue
                            
                    logger.warning(f"Could not parse valid classification from LLM response")
                    return None, 0.0
                    
                except Exception as e:
                    logger.error(f"Error parsing LLM classification: {str(e)}")
                    return None, 0.0
            
        except Exception as e:
            logger.error(f"Error in LLM message classification: {str(e)}")
            
        return None, 0.0

    def set_mode_by_intent(self, message: str) -> bool:
        """Detect intent to switch modes and set appropriate mode manually."""
        message_lower = message.lower()
        
        # Intent patterns for mode switching
        mode_switch_patterns = {
            ChatMode.SYSTEM_HELP: [
                r"\b(режим\s+хелп|режим\s+help|хелпер|helper|помощник|допомога)\b",
                r"\b(system\s+help|системная\s+помощь|системна\s+допомога)\b",
                r"\b(перейди\s+в\s+режим\s+помощи|switch\s+to\s+help)\b",
            ],
            ChatMode.GOAL_SETTING: [
                r"\b(режим\s+задач|режим\s+целей|task\s+mode|goal\s+mode)\b",
                r"\b(перейди\s+в\s+режим\s+задач|switch\s+to\s+task\s+mode)\b",
            ],
            ChatMode.TOOL_INQUIRY: [
                r"\b(режим\s+инструментов|режим\s+інструментів|tool\s+mode)\b",
                r"\b(покажи\s+инструменты|покажи\s+інструменти|show\s+tools)\b",
            ],
            ChatMode.DEVELOPMENT: [
                r"\b(режим\s+разработки|режим\s+розробки|dev\s+mode|development\s+mode)\b",
                r"\b(перейди\s+в\s+dev|switch\s+to\s+dev)\b",
            ],
            ChatMode.CASUAL_CHAT: [
                r"\b(режим\s+чата|режим\s+розмови|chat\s+mode|casual\s+mode)\b",
                r"\b(обычный\s+режим|звичайний\s+режим|normal\s+mode)\b",
            ],
        }
        
        for mode, patterns in mode_switch_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    self.set_manual_mode(mode)
                    logger.info(f"Mode switched to {mode.value} based on user intent")
                    return True
                    
        return False
