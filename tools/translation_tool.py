"""
Translation Tool for Ukrainian/Russian Support

This tool handles automatic translation for Ukrainian and Russian users,
translating incoming messages to English for internal processing and 
translating responses back to the user's language.
"""

import logging
import re
from dataclasses import dataclass
from typing import Tuple

try:
    from utils.llm_manager import LLMManager
    LLM_MANAGER_AVAILABLE = True
except ImportError:
    LLM_MANAGER_AVAILABLE = False
    LLMManager = None  # type: ignore

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Result of a translation operation."""
    text: str
    source_language: str
    target_language: str
    confidence: float
    original_text: str = ""

class TranslationTool:
    """Handles translation for Ukrainian/Russian chat messages."""

    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.supported_languages = {
            "uk": "Ukrainian",
            "ru": "Russian",
            "en": "English",
        }

        #Language detection patterns
        self.language_patterns = {
            "uk": [
                #Common Ukrainian words and patterns
                r"\b(привіт|вітаю|добрий|день|ранок|вечір|ніч)\b",
                r"\b(що|як|де|коли|чому|хто)\b",
                r"\b(можеш|можете|будь|ласка|дякую|дуже)\b",
                r"\b(потрібно|треба|хочу|хочеш|маю|маєш)\b",
                r"\b(зроби|створи|покажи|відкрий|запусти)\b",
                r"\b(допоможи|допоможеш|розкажи|поясни)\b",
                r"\b(програма|комп\'ютер|файл|папка|система)\b",
                r"[іїєґ]",  #Ukrainian-specific letters
                r"'",  #Apostrophe common in Ukrainian
            ],
            "ru": [
                #Common Russian words and patterns
                r"\b(привет|здравствуй|добрый|день|утро|вечер|ночь)\b",
                r"\b(что|как|где|когда|почему|кто)\b",
                r"\b(можешь|можете|будь|пожалуйста|спасибо|очень)\b",
                r"\b(нужно|надо|хочу|хочешь|имею|имеешь)\b",
                r"\b(сделай|создай|покажи|открой|запусти)\b",
                r"\b(помоги|поможешь|расскажи|объясни)\b",
                r"\b(программа|компьютер|файл|папка|система)\b",
                r"[ыъэё]",  #Russian-specific letters
            ],
        }

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text.
        
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text.strip():
            return "en", 0.0

        text_lower = text.lower()
        scores = {"uk": 0, "ru": 0, "en": 0}

        #Check for Ukrainian patterns
        for pattern in self.language_patterns["uk"]:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            scores["uk"] += matches * 2  #Weight Ukrainian higher for better detection

        #Check for Russian patterns
        for pattern in self.language_patterns["ru"]:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            scores["ru"] += matches

        #Basic English detection (ASCII letters, common English words)
        if re.search(r"\b(the|and|or|but|in|on|at|to|for|of|with|by)\b", text_lower):
            scores["en"] += 3
        elif re.search(r'^[a-zA-Z0-9\s\.,!?\-\'"]+$', text):
            scores["en"] += 1

        #Calculate confidence
        total_score = sum(scores.values())
        if total_score == 0:
            return "en", 0.5  #Default to English with low confidence

        detected_lang = max(scores, key=lambda k: scores[k])
        confidence = scores[detected_lang] / total_score

        #Boost confidence for clear indicators
        if detected_lang in ["uk", "ru"] and confidence > 0.3:
            confidence = min(confidence * 1.5, 1.0)

        logger.debug(f"Language detection: {text[:50]}... -> {detected_lang} (confidence: {confidence:.2f})")
        return detected_lang, confidence

    def translate_with_llm(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using the LLM manager."""
        if not self.llm_manager:
            logger.warning("No LLM manager available for translation")
            return text

        source_name = self.supported_languages.get(source_lang, source_lang)
        target_name = self.supported_languages.get(target_lang, target_lang)

        translation_prompt = f"""You are a professional translator. Translate the following text from {source_name} to {target_name}. 
        
Preserve the original meaning, tone, and intent. If the text contains technical terms or commands, keep them accurate.
If the text is already in {target_name}, return it unchanged.

Text to translate: {text}

Provide only the translation, no additional explanation."""

        try:
            messages = [{"role": "user", "content": translation_prompt}]
            result = self.llm_manager.chat(messages)

            if result and result.response_text:
                return result.response_text.strip()
            logger.warning("LLM translation failed - no response")
            return text

        except Exception as e:
            logger.error(f"LLM translation error: {e}")
            return text

    def translate_to_english(self, text: str) -> TranslationResult:
        """
        Translate text to English if it's in Ukrainian or Russian.
        
        Returns:
            TranslationResult with translation details
        """
        detected_lang, confidence = self.detect_language(text)

        if detected_lang == "en" or confidence < 0.3:
            return TranslationResult(
                text=text,
                source_language=detected_lang,
                target_language="en",
                confidence=confidence,
                original_text=text,
            )

        #Translate to English
        translated_text = self.translate_with_llm(text, detected_lang, "en")

        return TranslationResult(
            text=translated_text,
            source_language=detected_lang,
            target_language="en",
            confidence=confidence,
            original_text=text,
        )

    def translate_from_english(self, text: str, target_language: str) -> TranslationResult:
        """
        Translate English text to the target language.
        
        Args:
            text: English text to translate
            target_language: Target language code ('uk' or 'ru')
            
        Returns:
            TranslationResult with translation details
        """
        if target_language == "en":
            return TranslationResult(
                text=text,
                source_language="en",
                target_language="en",
                confidence=1.0,
                original_text=text,
            )

        translated_text = self.translate_with_llm(text, "en", target_language)

        return TranslationResult(
            text=translated_text,
            source_language="en",
            target_language=target_language,
            confidence=0.9,  #High confidence for LLM translation
            original_text=text,
        )

    def should_translate_message(self, text: str) -> bool:
        """
        Determine if a message should be translated based on language detection.
        
        Returns:
            True if the message is in Ukrainian or Russian and should be translated
        """
        detected_lang, confidence = self.detect_language(text)
        return detected_lang in ["uk", "ru"] and confidence >= 0.3

    def get_user_language(self, text: str) -> str:
        """
        Get the user's preferred language based on their input.
        
        Returns:
            Language code ('uk', 'ru', or 'en')
        """
        detected_lang, confidence = self.detect_language(text)
        if detected_lang in ["uk", "ru"] and confidence >= 0.3:
            return detected_lang
        return "en"

#Tool function for registration
def create_translation_tool(llm_manager=None) -> TranslationTool:
    """Create and return a translation tool instance."""
    return TranslationTool(llm_manager)

#For backward compatibility and registration
def translation_tool(llm_manager=None):
    """Factory function for creating translation tool."""
    return create_translation_tool(llm_manager)
