"""
Chat Translation Manager

Manages automatic translation for Ukrainian/Russian users in the chat interface.
Ensures all internal processing happens in English while providing localized responses.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from tools.translation_tool import TranslationTool, TranslationResult

logger = logging.getLogger(__name__)

@dataclass
class ChatTranslationContext:
    """Context for chat translation session."""
    user_language: str = 'en'
    original_message: str = ""
    translated_message: str = ""
    requires_response_translation: bool = False

class ChatTranslationManager:
    """Manages translation for chat messages and responses."""
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.translation_tool = TranslationTool(llm_manager)
        self.active_sessions: Dict[str, ChatTranslationContext] = {}
        
    def set_llm_manager(self, llm_manager):
        """Set or update the LLM manager for translation."""
        self.llm_manager = llm_manager
        self.translation_tool.llm_manager = llm_manager
    
    def process_incoming_message(self, message: str, session_id: str = "default") -> Tuple[str, ChatTranslationContext]:
        """
        Process an incoming chat message, translating if necessary.
        
        Args:
            message: Original user message
            session_id: Session identifier for tracking context
            
        Returns:
            Tuple of (processed_message_for_system, translation_context)
        """
        context = ChatTranslationContext()
        
        #Detect user language and translate if needed
        user_language = self.translation_tool.get_user_language(message)
        context.user_language = user_language
        context.original_message = message
        
        if self.translation_tool.should_translate_message(message):
            #Translate to English for internal processing
            translation_result = self.translation_tool.translate_to_english(message)
            
            context.translated_message = translation_result.text
            context.requires_response_translation = True
            
            logger.info(f"Translated incoming message from {user_language}: '{message[:50]}...' -> '{translation_result.text[:50]}...'")
            
            #Store context for this session
            self.active_sessions[session_id] = context
            
            return translation_result.text, context
        else:
            #No translation needed
            context.translated_message = message
            context.requires_response_translation = False
            
            #Store context anyway for consistency
            self.active_sessions[session_id] = context
            
            return message, context
    
    def process_outgoing_response(self, response: str, session_id: str = "default") -> str:
        """
        Process an outgoing response, translating back to user's language if needed.
        
        Args:
            response: System response in English
            session_id: Session identifier
            
        Returns:
            Response in user's preferred language
        """
        context = self.active_sessions.get(session_id)
        
        if not context or not context.requires_response_translation:
            return response
        
        #Translate response back to user's language
        translation_result = self.translation_tool.translate_from_english(response, context.user_language)
        
        logger.info(f"Translated outgoing response to {context.user_language}: '{response[:50]}...' -> '{translation_result.text[:50]}...'")
        
        return translation_result.text
    
    def get_translation_status(self, session_id: str = "default") -> Dict[str, Any]:
        """
        Get translation status for a session.
        
        Returns:
            Dictionary with translation status information
        """
        context = self.active_sessions.get(session_id)
        
        if not context:
            return {
                'active': False,
                'user_language': 'en',
                'translation_enabled': False
            }
        
        return {
            'active': True,
            'user_language': context.user_language,
            'translation_enabled': context.requires_response_translation,
            'original_message': context.original_message,
            'translated_message': context.translated_message
        }
    
    def clear_session(self, session_id: str = "default"):
        """Clear translation context for a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.debug(f"Cleared translation session: {session_id}")
    
    def is_translation_available(self) -> bool:
        """Check if translation is available (requires LLM manager)."""
        return self.llm_manager is not None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.translation_tool.supported_languages.copy()
    
    def detect_language_info(self, text: str) -> Dict[str, Any]:
        """
        Get detailed language detection information for debugging.
        
        Returns:
            Dictionary with detection details
        """
        detected_lang, confidence = self.translation_tool.detect_language(text)
        
        return {
            'detected_language': detected_lang,
            'language_name': self.translation_tool.supported_languages.get(detected_lang, detected_lang),
            'confidence': confidence,
            'should_translate': self.translation_tool.should_translate_message(text),
            'text_sample': text[:100] + ('...' if len(text) > 100 else '')
        }
