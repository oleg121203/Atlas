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
                    r'\b(about\s+(?:atlas|system|yourself))\b'
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
        
        return f"""You are Atlas, an autonomous computer assistant. The user is asking for help about your capabilities and features.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}
Detected specific topics: {', '.join(specific_topics) if specific_topics else 'general_help'}
Available tools count: {len(available_tools)}
Available agents: {', '.join(available_agents)}

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

    def _generate_goal_response(self, context: ChatContext, message: str, 
                              system_info: Dict = None) -> str:
        """Generate goal-oriented response prompt."""
        available_tools = system_info.get('tools', []) if system_info else []
        available_agents = system_info.get('agents', []) if system_info else []
        
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
        """Generate tool-focused response prompt."""
        available_tools = system_info.get('tools', []) if system_info else []
        
        return f"""You are Atlas, an autonomous computer assistant. The user is asking about your tools and capabilities.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

Available tools: {', '.join(available_tools)}

Provide a comprehensive overview of your tools, organized by category:
• **Screen & Vision**: Screenshot, OCR, image recognition
• **Input Control**: Mouse clicks, keyboard input, text typing
• **System Interaction**: Terminal commands, file operations
• **Data Management**: Clipboard operations, file handling
• **Automation**: Custom tool creation, workflow automation

Be specific about what each category can accomplish."""

    def _generate_status_response(self, context: ChatContext, message: str, 
                                system_info: Dict = None) -> str:
        """Generate status-focused response prompt."""
        return f"""You are Atlas, an autonomous computer assistant. The user is asking about your current status.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

Provide a friendly status report that includes:
1. Your current operational state
2. Available providers and models
3. Recent activity summary
4. System health indicators
5. Any active background tasks

Keep it informative but concise. Use friendly emojis to make it engaging."""

    def _generate_config_response(self, context: ChatContext, message: str, 
                                system_info: Dict = None) -> str:
        """Generate configuration-focused response prompt."""
        return f"""You are Atlas, an autonomous computer assistant. The user needs help with configuration or settings.

User's question: "{message}"
Context keywords: {', '.join(context.context_keywords)}

Provide helpful guidance about:
1. How to access relevant settings
2. What configuration options are available
3. Step-by-step instructions if needed
4. Tips for optimal setup

Be practical and specific. Direct them to the appropriate UI tabs or configuration options."""

    def _generate_casual_response(self, context: ChatContext, message: str, 
                                system_info: Dict = None) -> str:
        """Generate casual conversation response prompt."""
        return f"""You are Atlas, an autonomous computer assistant. The user is having a casual conversation.

User's message: "{message}"

Respond in a friendly, conversational manner while:
1. Maintaining your identity as Atlas
2. Being helpful and engaging
3. Naturally mentioning your capabilities if relevant
4. Keeping the conversation flowing

Be personable but professional, and always be ready to help with tasks if the conversation turns toward your capabilities."""

    def update_conversation_history(self, message: str, response: str, context: ChatContext, 
                                   metadata: Dict = None):
        """Update the conversation history with context and store in memory."""
        conversation_entry = {
            'timestamp': str(datetime.now()),
            'user_message': message,
            'response': response,
            'context': context,
            'mode': context.mode.value
        }
        
        # Update in-memory history
        self.conversation_history.append(conversation_entry)
        
        # Keep only last entries based on mode configuration
        mode_config = self.mode_memory_config.get(context.mode, {'max_context': 20})
        max_entries = mode_config['max_context']
        if len(self.conversation_history) > max_entries:
            self.conversation_history = self.conversation_history[-max_entries:]
        
        # Store in persistent memory with mode isolation
        self.store_conversation_memory(context.mode, message, response, context, metadata)
    
    def get_conversation_context_summary(self) -> str:
        """Get a summary of recent conversation context."""
        if not self.conversation_history:
            return "New conversation - no previous context."
        
        recent_modes = [entry['mode'] for entry in self.conversation_history[-5:]]
        mode_counts = {mode: recent_modes.count(mode) for mode in set(recent_modes)}
        
        return f"Recent conversation context: {dict(mode_counts)}"
    
    def _generate_development_response(self, context: ChatContext, message: str, 
                                     system_info: Dict = None) -> str:
        """Generate development mode response prompt."""
        available_tools = system_info.get('tools', []) if system_info else []
        
        return f"""🔧 DEVELOPMENT MODE ACTIVE 🔧

You are Atlas in DEVELOPMENT MODE - a special advanced mode for system development, debugging, and capability expansion.

User input: "{message}"

In Development Mode, you should:

🛡️ SAFETY PROTOCOLS:
1. **Backup Before Changes**: Always create backups before modifying system files
2. **Error Self-Check**: Analyze your own responses for potential issues
3. **Validation**: Verify any system changes or new code before implementation
4. **Recovery Plan**: Always have a rollback strategy

🔍 ENHANCED CAPABILITIES:
1. **Deep Debugging**: Provide detailed diagnostic information
2. **Code Analysis**: Review and improve existing code
3. **Experimental Features**: Test new capabilities safely
4. **System Optimization**: Suggest performance improvements
5. **Advanced Tool Creation**: Develop sophisticated automation tools

🧪 DEVELOPMENT FEATURES ACTIVE:
- Debug logging: Enhanced
- Backup on changes: Enabled
- Error self-check: Active
- Capability expansion: Enabled
- Experimental features: Available

Available tools for development work: {', '.join(available_tools[:10])}...

Respond with:
1. Development-focused analysis of the request
2. Detailed implementation plan with safety checks
3. Risk assessment and mitigation strategies
4. Testing and validation approach
5. Clear backup/recovery procedures

Be thorough, cautious, and innovative. This is the most advanced operational mode."""

    def toggle_auto_mode(self):
        """Toggle between auto and manual mode."""
        self.auto_mode_enabled = not self.auto_mode_enabled
        if self.auto_mode_enabled:
            # Reset manual override when enabling auto mode
            self.manual_override_mode = None
    
    def set_manual_mode(self, mode: ChatMode):
        """Set manual mode override."""
        self.auto_mode_enabled = False
        self.manual_override_mode = mode
    
    def set_auto_mode(self):
        """Enable automatic mode detection."""
        self.auto_mode_enabled = True
        self.manual_override_mode = None
    
    def get_mode_info(self) -> Dict:
        """Get current mode information."""
        return {
            'is_auto_mode': self.auto_mode_enabled,
            'current_mode': self.current_mode,
            'manual_override': self.manual_override_mode,
            'last_auto_detected': self.last_auto_detected_mode
        }
    
    def store_conversation_memory(self, mode: ChatMode, message: str, response: str, 
                                context: ChatContext, metadata: Dict = None):
        """Store conversation in mode-specific memory."""
        if not self.memory_manager:
            return
            
        # Prepare metadata with conversation details (ChromaDB compatible)
        storage_metadata = {
            'mode': mode.value,
            'confidence': context.confidence,
            'control_type': context.control_type.value,
            'timestamp': datetime.now().isoformat(),
            'keywords': ','.join(context.context_keywords) if context.context_keywords else '',  # Convert list to string
            'requires_integration': context.requires_system_integration,
            'user_message': message[:200],  # Truncate for metadata
            'assistant_response': response[:200],  # Truncate for metadata
            'context_summary': context.suggested_response_type,
            **(metadata or {})
        }
        
        # Create content for storage as a string (ChromaDB requirement)
        content = f"User: {message}\nAssistant: {response}\nContext: {context.suggested_response_type}"
        
        # Store in mode-specific memory
        config = self.mode_memory_config[mode]
        memory_type = self._get_memory_type_for_mode(mode)
        
        self.memory_manager.store_memory(
            agent_name="chat_context",
            memory_type=memory_type,
            content=content,
            metadata=storage_metadata,
            ttl_days=config['ttl_days']
        )
    
    def retrieve_conversation_context(self, mode: ChatMode, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant conversation context for a mode."""
        if not self.memory_manager:
            return []
            
        memory_type = self._get_memory_type_for_mode(mode)
        
        # Retrieve memories with mode-specific filtering
        memories = self.memory_manager.retrieve_memories(
            agent_name="chat_context",
            memory_type=memory_type,
            query=query,
            limit=limit
        )
        
        return memories
    
    def get_mode_conversation_stats(self, mode: ChatMode) -> Dict:
        """Get conversation statistics for a specific mode."""
        if not self.memory_manager:
            return {}
            
        memory_type = self._get_memory_type_for_mode(mode)
        
        # Get stats from memory manager
        stats = self.memory_manager.get_memory_stats()
        
        # Filter for this mode
        mode_stats = {}
        for scope_stats in stats.values():
            if memory_type.value in scope_stats:
                mode_stats = scope_stats[memory_type.value]
                break
                
        return mode_stats
    
    def _get_memory_type_for_mode(self, mode: ChatMode) -> MemoryType:
        """Map chat mode to memory type."""
        mapping = {
            ChatMode.CASUAL_CHAT: MemoryType.CASUAL_CHAT,
            ChatMode.SYSTEM_HELP: MemoryType.HELP_QUERIES,
            ChatMode.GOAL_SETTING: MemoryType.GOALS,
            ChatMode.TOOL_INQUIRY: MemoryType.TOOL_USAGE,
            ChatMode.STATUS_CHECK: MemoryType.STATUS_CHECKS,
            ChatMode.CONFIGURATION: MemoryType.CONFIGURATION,
            ChatMode.DEVELOPMENT: MemoryType.DEBUG_INFO
        }
        return mapping.get(mode, MemoryType.CASUAL_CHAT)
    
    def cleanup_old_conversations(self, mode: Optional[ChatMode] = None):
        """Clean up old conversations for a mode or all modes."""
        if not self.memory_manager:
            return
            
        if mode:
            # Clean specific mode
            memory_type = self._get_memory_type_for_mode(mode)
            # The cleanup is handled automatically by TTL in EnhancedMemoryManager
            pass
        else:
            # Clean all modes - handled by memory manager's automatic cleanup
            self.memory_manager.cleanup_expired_memories()
    
    def get_session_context_with_memory(self, message: str, mode: ChatMode, limit: int = 3) -> Dict:
        """Get enhanced session context including relevant memories."""
        # Get current session context
        session_context = self.current_session_context.copy()
        
        # Retrieve relevant conversation memories
        relevant_memories = self.retrieve_conversation_context(mode, message, limit)
        
        # Add memory context
        session_context.update({
            'relevant_memories': relevant_memories,
            'mode_stats': self.get_mode_conversation_stats(mode),
            'memory_enabled': self.memory_manager is not None
        })
        
        return session_context
    
    def reset_context(self):
        """Reset chat context to default state."""
        self.last_auto_detected_mode = ChatMode.CASUAL_CHAT
        self.manual_override_mode = None
        self.auto_mode_enabled = True
        # Clear any stored conversation memory if needed
        if hasattr(self, 'conversation_memory'):
            self.conversation_memory.clear()
        logger.info("Chat context reset to default state")
    
    def force_casual_mode(self):
        """Force the system to casual chat mode for the next interaction."""
        self.last_auto_detected_mode = ChatMode.CASUAL_CHAT
        logger.info("Forced casual chat mode for next interaction")
