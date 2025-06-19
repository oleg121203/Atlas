#!/usr/bin/env python3
"""
Chat Context Manager for Atlas

Manages different conversation modes and provides context-aware responses.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType

logger = logging.getLogger(__name__)

class ChatMode(Enum):
    """Different modes of conversation with Atlas."""
    CASUAL_CHAT = "casual_chat"      # General conversation
    SYSTEM_HELP = "system_help"      # System assistance
    GOAL_SETTING = "goal_setting"    # Task specification
    TOOL_INQUIRY = "tool_inquiry"    # Tool-related questions
    STATUS_CHECK = "status_check"    # Status checking
    CONFIGURATION = "configuration"   # System configuration
    DEVELOPMENT = "development"      # Development mode (manual switching only)

class ModeControl(Enum):
    """Mode control types."""
    AUTO = "auto"         # Automatic detection
    MANUAL = "manual"     # Manual switching

@dataclass
class ChatContext:
    """Context information for a chat message."""
    mode: ChatMode
    confidence: float
    suggested_response_type: str
    context_keywords: List[str]
    requires_system_integration: bool
    control_type: ModeControl = ModeControl.AUTO  # How the mode was selected

class ChatContextManager:
    """Manages chat context and determines appropriate response modes."""
    
    def __init__(self, memory_manager: Optional[EnhancedMemoryManager] = None):
        self.conversation_history: List[Dict] = []
        self.current_session_context = {}
        
        # Enhanced memory integration
        self.memory_manager = memory_manager
        # Note: If no memory_manager is provided, some features will be disabled
        
        # Mode control settings
        self.auto_mode_enabled = True
        self.manual_override_mode = None
        self.last_auto_detected_mode = None
        
        # Development mode settings
        self.development_mode_features = {
            'debug_logging': True,
            'backup_on_changes': True,
            'error_self_check': True,
            'capability_expansion': True,
            'experimental_features': True
        }
        
        # Mode-specific memory settings
        self.mode_memory_config = {
            ChatMode.CASUAL_CHAT: {'ttl_days': 7, 'max_context': 20},
            ChatMode.SYSTEM_HELP: {'ttl_days': 30, 'max_context': 50},
            ChatMode.GOAL_SETTING: {'ttl_days': 90, 'max_context': 100},
            ChatMode.TOOL_INQUIRY: {'ttl_days': 14, 'max_context': 30},
            ChatMode.STATUS_CHECK: {'ttl_days': 3, 'max_context': 10},
            ChatMode.CONFIGURATION: {'ttl_days': 365, 'max_context': 50},
            ChatMode.DEVELOPMENT: {'ttl_days': 180, 'max_context': 200}
        }
        
        # Initialize patterns and templates
        self._initialize_patterns()
        self._initialize_templates()
        
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
        # Patterns for different modes
        self.mode_patterns = {
            ChatMode.CASUAL_CHAT: {
                'keywords': [
                    'hello', 'hi', 'hey', 'good morning', 'good evening', 'good day',
                    'how are you', 'how is it going', 'what\'s up', 'thanks', 'thank you',
                    'please', 'sorry', 'excuse me', 'nice', 'good', 'great', 'awesome',
                    'weather', 'today', 'yesterday', 'tomorrow', 'weekend', 'holiday',
                    'chat', 'talk', 'conversation', 'discuss', 'opinion', 'think',
                    'like', 'love', 'enjoy', 'favorite', 'interesting', 'cool',
                    'funny', 'joke', 'laugh', 'smile', 'happy', 'sad', 'excited',
                    'tired', 'busy', 'free', 'time', 'day', 'night', 'morning',
                    'afternoon', 'evening', 'week', 'month', 'year', 'life',
                    'work', 'job', 'study', 'learn', 'read', 'watch', 'listen',
                    'music', 'movie', 'book', 'food', 'coffee', 'tea', 'drink',
                    'eat', 'sleep', 'rest', 'relax', 'travel', 'vacation'
                ],
                'patterns': [
                    r'\b(hello|hi|hey|good\s+(?:morning|evening|day))\b',
                    r'\b(how\s+are\s+you|how\s+is\s+it\s+going|what\'?s\s+up)\b',
                    r'\b(thanks?|thank\s+you|please|sorry|excuse\s+me)\b',
                    r'\b(nice|good|great|awesome|cool|interesting)\b',
                    r'\b(weather|today|yesterday|tomorrow|weekend)\b',
                    r'\b(like|love|enjoy|favorite|think|opinion)\b',
                    r'\b(happy|sad|excited|tired|busy|free)\b',
                    r'\b(music|movie|book|food|coffee|tea|travel)\b'
                ]
            },
            
            ChatMode.SYSTEM_HELP: {
                'keywords': [
                    'help', 'explain', 'tutorial', 'guide', 'documentation', 
                    'capabilities', 'modes', 'mode', 'atlas', 'system',
                    'tell me about', 'what are', 'show me', 'describe',
                    'atlas capabilities', 'atlas features', 'atlas modes',
                    'about atlas', 'atlas system', 'development mode',
                    'your memory', 'organized memory', 'about yourself',
                    'your capabilities', 'your features', 'provider',
                    'memory system', 'long-term memory', 'short-term memory',
                    'how do you remember', 'do you forget', 'memory management',
                    'пам\'ять', 'память', 'запоминаєш', 'запам\'ятовуєш',
                    # Code analysis keywords - most specific ones only
                    'rebuild index', 'update index', 'show file', 'analyze file',
                    'code analysis', 'structure analysis'
                ],
                'patterns': [
                    r'\b(explain\s+(?:atlas|system)|help\s+(?:with|me)\s+(?:atlas|system))\b',
                    r'\b(atlas\s+(?:capabilities|features|modes|system))\b',
                    r'\b(tell\s+me\s+about\s+(?:atlas|system|yourself))\b',
                    r'\b(what\s+(?:are|is)\s+(?:atlas|your)\s+(?:capabilities|features|modes))\b',
                    r'\b(development\s+mode|your\s+memory|organized\s+memory)\b',
                    r'\b(rebuild\s+index|analyze\s+file|code\s+analysis)\b',
                    r'\b(about\s+(?:atlas|system|yourself))\b',
                    r'\b(memory\s+system|long-term\s+memory|how\s+(?:do\s+)?you\s+remember)\b',
                    r'\b(how\s+(?:is|does)\s+(?:your|atlas)\s+memory\s+(?:work|organized))\b'
                ]
            },
            
            ChatMode.GOAL_SETTING: {
                'keywords': [
                    'take screenshot', 'click on', 'open', 'run', 'execute',
                    'find', 'search', 'copy', 'paste', 'type', 'press',
                    'create', 'delete', 'move', 'automation', 'automate',
                    'do', 'make', 'perform', 'complete', 'finish', 'start',
                    'stop', 'close', 'launch', 'capture', 'screenshot'
                ],
                'patterns': [
                    r'\b(take\s+a?\s*screenshot|click\s+(?:on|at)|open\s+\w+|run\s+\w+)\b',
                    r'\b(do\s+(?:this|that)|make\s+(?:this|that)|perform\s+(?:this|that))\b',
                    r'\b(automate\s+\w+|execute\s+\w+|launch\s+\w+)\b'
                ]
            },
            
            ChatMode.TOOL_INQUIRY: {
                'keywords': [
                    'tools', 'available', 'list', 'what tools', 'functions',
                    'instruments', 'commands', 'capabilities', 'features',
                    'what can', 'show tools', 'list tools', 'available functions',
                    'show me', 'what functions', 'tool list'
                ],
                'patterns': [
                    r'\b(what\s+tools|available\s+tools|list\s+(?:of\s+)?tools)\b',
                    r'\b(show\s+(?:me\s+)?(?:tools|functions|capabilities))\b',
                    r'\b(what\s+(?:can\s+)?(?:functions|tools|commands))\b'
                ]
            },
            
            ChatMode.STATUS_CHECK: {
                'keywords': [
                    'status', 'running', 'working', 'progress', 'state',
                    'health', 'performance', 'current state', 'how is',
                    'what is happening', 'what is going on', 'system status',
                    'is everything', 'all good', 'working properly',
                    'functioning', 'operational', 'active', 'idle'
                ],
                'patterns': [
                    r'\b(what(?:\'s|\s+is)\s+(?:the\s+)?status|how\s+(?:is|are)\s+things)\b',
                    r'\b(is\s+(?:everything|atlas|system)\s+(?:working|running|ok))\b',
                    r'\b(current\s+(?:status|state)|system\s+health)\b'
                ]
            },
            
            ChatMode.CONFIGURATION: {
                'keywords': [
                    'settings', 'configure', 'setup', 'options', 'preferences',
                    'config', 'api key', 'provider', 'change settings',
                    'modify', 'adjust', 'customize', 'configuration',
                    'parameters', 'set up', 'installation', 'initialization'
                ],
                'patterns': [
                    r'\b(change\s+settings|configure\s+\w+|setup\s+\w+)\b',
                    r'\b(modify\s+(?:settings|config)|adjust\s+\w+)\b',
                    r'\b(api\s+key|provider\s+setup|installation)\b'
                ]
            }
        }
    
    def _initialize_templates(self):
        """Initialize response templates."""
        # Response templates
        self.response_templates = {
            ChatMode.SYSTEM_HELP: self._generate_help_response,
            ChatMode.GOAL_SETTING: self._generate_goal_response,
            ChatMode.TOOL_INQUIRY: self._generate_tool_response,
            ChatMode.STATUS_CHECK: self._generate_status_response,
            ChatMode.CONFIGURATION: self._generate_config_response,
            ChatMode.CASUAL_CHAT: self._generate_casual_response,
            ChatMode.DEVELOPMENT: self._generate_development_response
        }
    
    def analyze_message(self, message: str, user_context: Dict = None) -> ChatContext:
        """Analyze a message and determine its context."""
        # If in manual mode, use the override mode
        if not self.auto_mode_enabled and self.manual_override_mode:
            return ChatContext(
                mode=self.manual_override_mode,
                confidence=1.0,  # Manual mode has 100% confidence
                suggested_response_type=self._get_response_type(self.manual_override_mode),
                context_keywords=[],
                requires_system_integration=self.manual_override_mode in [
                    ChatMode.GOAL_SETTING, 
                    ChatMode.STATUS_CHECK, 
                    ChatMode.TOOL_INQUIRY,
                    ChatMode.DEVELOPMENT
                ],
                control_type=ModeControl.MANUAL
            )
        
        # Auto mode - analyze the message
        message_lower = message.lower()
        scores = {}
        
        # Calculate scores for each mode (except DEVELOPMENT which is manual-only)
        analyzable_modes = [mode for mode in self.mode_patterns.keys() 
                           if mode != ChatMode.DEVELOPMENT]
        
        for mode in analyzable_modes:
            patterns = self.mode_patterns[mode]
            score = 0.0
            
            # Check keywords with higher weight for exact matches
            keyword_matches = 0
            for keyword in patterns['keywords']:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    # Bonus for exact word boundaries
                    if f" {keyword.lower()} " in f" {message_lower} ":
                        score += 0.1
            
            if keyword_matches > 0:
                # Equal weight for all modes - no special preference for SYSTEM_HELP
                score += (keyword_matches / len(patterns['keywords'])) * 0.6
            
            # Check regex patterns with equal weight
            pattern_matches = sum(1 for pattern in patterns['patterns']
                                if re.search(pattern, message_lower, re.IGNORECASE))
            if pattern_matches > 0:
                score += (pattern_matches / len(patterns['patterns'])) * 0.4
            
            scores[mode] = score
        
        # Find the best match
        best_mode = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_mode]
        
        # Special handling for casual greetings and short messages
        if len(message.strip()) <= 20 and any(greeting in message_lower for greeting in [
            'привіт', 'привет', 'hi', 'hello', 'hey', 'добрий', 'доброе', 'good'
        ]):
            best_mode = ChatMode.CASUAL_CHAT
            confidence = 0.8
        
        # Default to casual chat if confidence is too low or message is very short
        if confidence < 0.1 or (len(message.strip()) <= 10 and confidence < 0.3):
            best_mode = ChatMode.CASUAL_CHAT
            confidence = 0.5
        
        # Store last auto-detected mode
        self.last_auto_detected_mode = best_mode
        
        # Determine context keywords
        context_keywords = []
        for mode, patterns in self.mode_patterns.items():
            if mode == best_mode:
                context_keywords = [kw for kw in patterns['keywords'] 
                                  if kw.lower() in message_lower]
                break
        
        # Determine if system integration is required
        requires_integration = best_mode in [
            ChatMode.GOAL_SETTING, 
            ChatMode.STATUS_CHECK, 
            ChatMode.TOOL_INQUIRY
        ]
        
        return ChatContext(
            mode=best_mode,
            confidence=confidence,
            suggested_response_type=self._get_response_type(best_mode),
            context_keywords=context_keywords,
            requires_system_integration=requires_integration,
            control_type=ModeControl.AUTO
        )
    
    def get_current_mode_info(self) -> Dict:
        """Get current mode control information."""
        return {
            'auto_enabled': self.auto_mode_enabled,
            'manual_override': self.manual_override_mode.value if self.manual_override_mode else None,
            'last_auto_mode': self.last_auto_detected_mode.value if self.last_auto_detected_mode else None,
            'development_features': self.development_mode_features if self.manual_override_mode == ChatMode.DEVELOPMENT else None
        }
    
    def analyze_message_with_mode_control(self, message: str, system_info: Dict = None) -> ChatContext:
        """Analyze message respecting mode control settings."""
        if not self.auto_mode_enabled and self.manual_override_mode:
            # Manual mode is active
            if self.manual_override_mode == ChatMode.DEVELOPMENT:
                return self._create_development_context(message)
            else:
                return self._create_manual_context(message, self.manual_override_mode)
        else:
            # Auto mode - use normal analysis
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
            control_type=ModeControl.MANUAL
        )
    
    def _create_manual_context(self, message: str, mode: ChatMode) -> ChatContext:
        """Create context for manual mode override."""
        return ChatContext(
            mode=mode,
            confidence=1.0,
            suggested_response_type=self._get_response_type(mode),
            context_keywords=[],
            requires_system_integration=mode in [ChatMode.GOAL_SETTING, ChatMode.STATUS_CHECK, ChatMode.TOOL_INQUIRY],
            control_type=ModeControl.MANUAL
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
            ChatMode.DEVELOPMENT: "development_focused"
        }
        return response_types.get(mode, "conversational")
    
    def generate_response_prompt(self, context: ChatContext, message: str, 
                               system_info: Dict = None) -> str:
        """Generate an appropriate system prompt based on context."""
        return self.response_templates[context.mode](context, message, system_info)
    
    def _generate_help_response(self, context: ChatContext, message: str, 
                              system_info: Dict = None) -> str:
        """Generate help-focused response prompt."""
        available_tools = system_info.get('tools', []) if system_info else []
        available_agents = system_info.get('agents', []) if system_info else []
        
        # Determine specific topics based on the message
        message_lower = message.lower()
        specific_topics = []
        
        if any(word in message_lower for word in ['development', 'dev']):
            specific_topics.append('development_mode')
        if any(word in message_lower for word in ['mode', 'modes']):
            specific_topics.append('modes')
        if any(word in message_lower for word in ['tool', 'tools']):
            specific_topics.append('tools')
        if any(word in message_lower for word in ['capabilities', 'features']):
            specific_topics.append('capabilities')
        if any(word in message_lower for word in ['atlas', 'system']):
            specific_topics.append('system_overview')
        
        # Add specific topic detection for memory-related queries
        if any(word in message_lower for word in ['memory', 'пам\'ять', 'память', 'remember', 'memorize', 'store', 'recall']):
            specific_topics.append('memory_system')
            
        # Generate the base system prompt
        base_prompt = f"""You are Atlas, an autonomous computer assistant. The user is asking for help about your capabilities and features.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}
Detected specific topics: {', '.join(specific_topics) if specific_topics else 'general_help'}
Available tools count: {len(available_tools)}
Available agents: {', '.join(available_agents)}"""

        # Add specialized information for memory-related queries
        if 'memory_system' in specific_topics:
            return f"""{base_prompt}

The user is asking about the Atlas memory system. Provide detailed information about how your memory works.

**Memory System Information:**

1. **Enhanced Memory Architecture:**
   - Atlas uses a hierarchical vector database (ChromaDB) for long-term memory storage
   - Memory is organized by agent type and memory purpose
   - Different types of memories have configurable retention periods (TTL)
   - Memory is stored locally on the user's machine for privacy

2. **Memory Categories:**
   - **Chat Memory**: Stores different conversation types (casual, help, goals)
   - **Agent Memory**: Each agent (Master, Screen, Browser, etc.) has isolated memory
   - **System Knowledge**: Stores successful patterns and error solutions
   - **User Preferences**: Retains user settings and preferences long-term

3. **Memory Features:**
   - **Semantic Search**: Finds related memories based on meaning, not just keywords
   - **Time-based Expiry**: Old memories automatically expire based on importance
   - **Context Isolation**: Different chat modes have separate memory storage
   - **Metadata Tagging**: Enhanced context with timestamps and categorization

4. **Memory Types by Duration:**
   - **Short-term**: Current session context (1-2 hours)
   - **Medium-term**: Recent tasks and conversations (1-30 days)
   - **Long-term**: Important knowledge and preferences (90-365 days)

Based on the user's specific question about memory, focus on explaining the relevant aspects in detail, using clear examples of how the memory system improves their experience with Atlas.

Keep your response focused specifically on the memory system that was asked about, be direct and informative rather than promotional. Structure your answer clearly with bullet points and sections."""
        
        # Default help response for non-memory topics
        return f"""{base_prompt}

Provide a comprehensive, well-structured response following this format:

**🤖 ATLAS CAPABILITIES OVERVIEW**

**Core Functions:**
• **Automation & Control** - Mouse/keyboard automation, screen interaction
• **Visual Analysis** - Screenshot capture, OCR, image recognition  
• **File Management** - File operations, clipboard management
• **System Integration** - Terminal commands, process management
• **Communication** - Email, Telegram, SMS notifications
• **Web Interaction** - Browser automation, data extraction
• **Custom Development** - Tool creation, script generation

**Operating Modes:**
• 🤖 **Auto Mode** - Intelligent context detection
• 💬 **Chat Mode** - General conversation
• ❓ **Help Mode** - System information and guidance
• 🎯 **Goal Mode** - Task execution and automation
• 🔧 **Development Mode** - Advanced system access with safety features

**Key Features:**
1. **Multi-language Support** - Ukrainian, Russian, English with automatic translation
2. **Intelligent Context** - Understands conversation intent automatically
3. **Safety First** - Built-in backup and recovery systems
4. **Extensible** - Custom tool creation and plugin support
5. **Real-time Monitoring** - Background system health checks

**Available Tools:** {len(available_tools)} tools including:
{', '.join(available_tools[:12])}{'...' if len(available_tools) > 12 else ''}

**Specialized Agents:**
{', '.join(available_agents)}

Based on your specific question, provide additional detailed information about the requested topic. 

Be specific, practical, and include examples. Structure your response with clear sections and use emojis for better readability. If the user asked about development mode specifically, emphasize its safety features and enhanced capabilities."""
