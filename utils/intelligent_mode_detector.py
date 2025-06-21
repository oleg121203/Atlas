"""
Інтелектуальний детектор режимів чату Atlas
Розумна system визначення, коли використовувати advanced thinking vs звичайний help mode
"""

import re
import logging
from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class ChatMode(Enum):
    """Режими чату"""
    SIMPLE_COMMAND = "simple_command"      #Прості команди (read file, list dir)
    ADVANCED_THINKING = "advanced_thinking" #Складний аналіз і мислення
    HYBRID = "hybrid"                       #Потребує обох підходів

@dataclass
class DetectionResult:
    """Результат детекції режиму"""
    mode: ChatMode
    confidence: float  #0.0 - 1.0
    reasoning: str
    should_use_advanced: bool
    fallback_to_simple: bool = False

class IntelligentModeDetector:
    """
    Інтелектуальний детектор режимів з контекстним аналізом
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        #Вдосконалені паттерни детекції
        self.patterns = self._initialize_detection_patterns()
        
        #Статистика для навчання
        self.detection_stats = {
            "total_detections": 0,
            "mode_counts": {},
            "accuracy_feedback": []
        }
    
    def _initialize_detection_patterns(self) -> Dict:
        """Initialization паттернів детекції"""
        return {
            #Прості команди - високий пріоритет, точні збіги
            "simple_commands": {
                "patterns": [
                    #Файлові операції
                    r"^(read|show|display)\s+(file|код)\s+[^\s]+",
                    r"^list\s+(directory|folder|dir|папк)",
                    r"^(show|display)\s+(tree|structure|структур)",
                    
                    #Пошук з конкретними параметрами
                    r"^search\s+(for|in)\s+[\"']?[^\"']+[\"']?$",
                    r"^find\s+(functions?|classes?|methods?)\s+[\"']?[^\"']+[\"']?$",
                    r"^(info|details)\s+(about|про)\s+[^\s]+",
                    
                    #Метрики та статистика
                    r"^(metrics|statistics|stats|статистик)",
                    r"^(usage|використання)\s+of\s+[^\s]+$",
                    r"^where\s+is\s+[^\s]+$",
                ],
                "weight": 0.9,
                "keywords": [
                    "read file", "show file", "list directory", "show tree",
                    "search for", "find functions", "info about", "metrics",
                    "читати файл", "показати файл", "список директорій"
                ]
            },
            
            #Складні аналітичні запити
            "advanced_thinking": {
                "patterns": [
                    #Аналітичні запити
                    r"(проаналізуй|analyze|розгляну|examine|досліди|investigate)",
                    r"(як\s+(працює|work|функціону)|how\s+does\s+.+work)",
                    r"(чому|why|навіщо|what\s+is\s+the\s+purpose)",
                    
                    #Проблемні запити
                    r"(що\s+не\s+так|what.+wrong|проблем|problem|issue|помилк|error)",
                    r"(не\s+працює|doesn.t\s+work|broken|зламан)",
                    
                    #Покращення та оптимізація
                    r"(як\s+(можна\s+)?покращи|how\s+(can\s+)?improve|удосконал|enhance|оптиміз|optimize)",
                    r"(пропону|suggest|рекоменду|recommend|ідеї|ideas)",
                    
                    #Порівняння та вибір
                    r"(порівня|compare|різниц|difference|альтернатив|alternative)",
                    r"(який\s+(кращ|варіант)|which\s+(is\s+)?better|що\s+вибрати|what\s+to\s+choose)",
                    
                    #Архітектурні питання
                    r"(архітектур|architecture|структур|structure|дизайн|design)",
                    r"(систем|system|компонент|component|модул|module|інтеграц|integrat)",
                    
                    #Концептуальні питання
                    r"(принцип|principle|підхід|approach|методолог|methodolog|стратег|strateg)",
                    r"(філософ|philosoph|концепц|concept|ідеолог|ideolog)"
                ],
                "weight": 0.8,
                "keywords": [
                    "проаналізуй", "як працює", "що не так", "покращити", "порівняти",
                    "архітектура", "система", "принципи", "оптимізація", "проблема"
                ]
            },
            
            #Контекстні модифікатори
            "context_modifiers": {
                #Слова, що підвищують складність
                "complexity_indicators": [
                    "детально", "глибоко", "комплексно", "всебічно",
                    "detailed", "comprehensive", "thorough", "in-depth",
                    "складн", "complex", "розширен", "advanced"
                ],
                
                #Слова, що знижують складність
                "simplicity_indicators": [
                    "швидко", "коротко", "просто", "базово",
                    "quick", "brief", "simple", "basic", "just"
                ],
                
                #Технічні терміни
                "technical_terms": [
                    "алгоритм", "algorithm", "реалізац", "implementation",
                    "код", "code", "функц", "function", "клас", "class",
                    "метод", "method", "змінна", "variable", "параметр", "parameter"
                ]
            }
        }
    
    def detect_chat_mode(self, message: str, context: Optional[Dict] = None) -> DetectionResult:
        """
        Основний метод детекції режиму чату
        """
        message = message.strip()
        message_lower = message.lower()
        
        if not message:
            return DetectionResult(
                mode=ChatMode.SIMPLE_COMMAND,
                confidence=0.5,
                reasoning="Порожнє повідомлення",
                should_use_advanced=False
            )
        
        #Фаза 1: Verification простих команд (високий пріоритет)
        simple_score, simple_reasoning = self._check_simple_commands(message, message_lower)
        
        #Фаза 2: Verification складних запитів
        advanced_score, advanced_reasoning = self._check_advanced_thinking(message, message_lower)
        
        #Фаза 3: Контекстні модифікатори
        context_modifier = self._analyze_context_modifiers(message, message_lower)
        
        #Фаза 4: Вирішення конфліктів та фінальне рішення
        final_result = self._resolve_mode_conflict(
            simple_score, advanced_score, context_modifier,
            simple_reasoning, advanced_reasoning, message
        )
        
        #Логування для навчання
        self._log_detection(message, final_result)
        
        return final_result
    
    def _check_simple_commands(self, message: str, message_lower: str) -> Tuple[float, str]:
        """Verification простих команд"""
        score = 0.0
        matched_patterns = []
        
        #Verification регулярних виразів
        for pattern in self.patterns["simple_commands"]["patterns"]:
            if re.search(pattern, message_lower):
                score += 0.3
                matched_patterns.append(f"pattern: {pattern[:30]}...")
        
        #Verification ключових слів
        for keyword in self.patterns["simple_commands"]["keywords"]:
            if keyword in message_lower:
                score += 0.2
                matched_patterns.append(f"keyword: {keyword}")
        
        #Додаткові правила для простих команд
        if len(message.split()) <= 4 and any(cmd in message_lower for cmd in ["read", "show", "list", "tree"]):
            score += 0.3
            matched_patterns.append("short_command")
        
        #Точні збіги мають найвищий пріоритет
        exact_matches = [
            "read file", "show file", "list directory", "show tree",
            "search for", "info about", "metrics", "stats"
        ]
        
        for exact in exact_matches:
            if message_lower.startswith(exact):
                score = 0.95  #Майже гарантована проста команда
                matched_patterns = [f"exact_match: {exact}"]
                break
        
        reasoning = f"Simple command indicators: {', '.join(matched_patterns)}" if matched_patterns else "No simple patterns"
        return min(score, 1.0), reasoning
    
    def _check_advanced_thinking(self, message: str, message_lower: str) -> Tuple[float, str]:
        """Verification потреби в складному мисленні"""
        score = 0.0
        matched_patterns = []
        
        #Конкретні українські та англійські ключові слова з високою вагою
        high_priority_keywords = {
            #Аналітичні слова
            "проаналізуй": 0.4, "analyze": 0.4, "аналіз": 0.3, "analysis": 0.3,
            "розгляну": 0.3, "examine": 0.3, "досліди": 0.3, "investigate": 0.3,
            
            #Проблемні слова  
            "що не так": 0.5, "what's wrong": 0.5, "what is wrong": 0.5,
            "проблем": 0.4, "problem": 0.4, "issue": 0.4, "помилк": 0.4, "error": 0.4,
            "не працює": 0.4, "doesn't work": 0.4, "not working": 0.4,
            
            #Покращення
            "покращи": 0.4, "improve": 0.4, "покращення": 0.3, "improvement": 0.3,
            "як можна": 0.4, "how can": 0.4, "удосконал": 0.3, "enhance": 0.3,
            "оптиміз": 0.3, "optimize": 0.3,
            
            #Порівняння
            "порівня": 0.4, "compare": 0.4, "різниц": 0.3, "difference": 0.3,
            "який кращ": 0.4, "which is better": 0.4, "що вибрати": 0.4,
            
            #Архітектурні
            "архітектур": 0.4, "architecture": 0.4, "структур": 0.3, "structure": 0.3,
            "систем": 0.3, "system": 0.3, "дизайн": 0.3, "design": 0.3,
            
            #Концептуальні
            "як працює": 0.5, "how does": 0.4, "how it works": 0.5,
            "чому": 0.3, "why": 0.3, "навіщо": 0.3, "what is the purpose": 0.4,
            "принцип": 0.3, "principle": 0.3, "підхід": 0.3, "approach": 0.3
        }
        
        #Verification ключових слів з вагами
        for keyword, weight in high_priority_keywords.items():
            if keyword in message_lower:
                score += weight
                matched_patterns.append(f"keyword: {keyword} (+{weight})")
        
        #Регулярні вирази для складних паттернів
        complex_patterns = [
            (r"як\s+(можна\s+)?(покращи|удосконал)", 0.4, "improvement_question"),
            (r"що\s+не\s+так\s+з", 0.5, "problem_question"),
            (r"чому\s+.+\s+(не\s+)?працює", 0.4, "why_not_working"),
            (r"як\s+.+\s+працює", 0.4, "how_it_works"),
            (r"порівня.+\s+(з|та|and|with)", 0.4, "comparison"),
            (r"проаналізуй\s+.+", 0.5, "analysis_request"),
            (r"(how|як)\s+(can|to|могти)\s+.+", 0.3, "how_to_question"),
            (r"(what|що)\s+(should|треба|потрібно)", 0.3, "what_should"),
        ]
        
        for pattern, weight, name in complex_patterns:
            if re.search(pattern, message_lower):
                score += weight
                matched_patterns.append(f"pattern: {name} (+{weight})")
        
        #Додаткові правила
        
        #Питальні слова з складністю
        complex_question_starters = ["як можна", "чому саме", "що робити", "як краще", 
                                   "how can", "why does", "what should", "how to"]
        for starter in complex_question_starters:
            if message_lower.startswith(starter):
                score += 0.3
                matched_patterns.append(f"complex_start: {starter}")
        
        #Довгі речення часто потребують аналізу (але не дуже довгі файлові шляхи)
        word_count = len(message.split())
        if word_count > 6 and not any(sep in message for sep in ['/', '\\', '.']):
            bonus = min(0.2, (word_count - 6) * 0.03)
            score += bonus
            matched_patterns.append(f"long_sentence: {word_count} words (+{bonus:.2f})")
        
        #Кілька питань в одному повідомленні
        question_count = message.count('?')
        if question_count > 1:
            score += question_count * 0.1
            matched_patterns.append(f"multiple_questions: {question_count}")
        
        #Наявність технічних термінів Atlas
        atlas_terms = ["atlas", "пам'ять", "memory", "агент", "agent", "модуль", "module", 
                       "менеджер", "manager", "думання", "thinking", "аналіз", "analysis"]
        atlas_count = sum(1 for term in atlas_terms if term in message_lower)
        if atlas_count > 1:
            score += atlas_count * 0.05
            matched_patterns.append(f"atlas_terms: {atlas_count}")
        
        reasoning = f"Advanced thinking indicators: {', '.join(matched_patterns)}" if matched_patterns else "No advanced patterns"
        return min(score, 1.0), reasoning
    
    def _analyze_context_modifiers(self, message: str, message_lower: str) -> float:
        """Аналіз контекстних модифікаторів"""
        modifier = 0.0
        
        #Індикатори складності
        complexity_indicators = self.patterns["context_modifiers"]["complexity_indicators"]
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in message_lower)
        modifier += complexity_count * 0.1
        
        #Індикатори простоти
        simplicity_indicators = self.patterns["context_modifiers"]["simplicity_indicators"]
        simplicity_count = sum(1 for indicator in simplicity_indicators if indicator in message_lower)
        modifier -= simplicity_count * 0.1
        
        #Технічні терміни
        technical_terms = self.patterns["context_modifiers"]["technical_terms"]
        technical_count = sum(1 for term in technical_terms if term in message_lower)
        if technical_count > 2:
            modifier += 0.15  #Багато технічних термінів = складність
        
        return max(-0.3, min(0.3, modifier))  #Обмежуємо модифікатор
    
    def _resolve_mode_conflict(self, simple_score: float, advanced_score: float, 
                              context_modifier: float, simple_reasoning: str, 
                              advanced_reasoning: str, original_message: str) -> DetectionResult:
        """Вирішення конфліктів та фінальне рішення"""
        
        #Застосовуємо контекстний модифікатор
        adjusted_advanced_score = max(0.0, advanced_score + context_modifier)
        
        #Різниця між оцінками
        score_diff = abs(simple_score - adjusted_advanced_score)
        
        #Логіка прийняття рішення з покращеними порогами
        if simple_score >= 0.8 and adjusted_advanced_score < 0.4:
            #Чітка проста команда
            mode = ChatMode.SIMPLE_COMMAND
            confidence = simple_score
            should_use_advanced = False
            reasoning = f"Clear simple command: {simple_reasoning}"
            
        elif adjusted_advanced_score >= 0.4 and (adjusted_advanced_score > simple_score or simple_score < 0.3):
            #Потреба в складному мисленні
            mode = ChatMode.ADVANCED_THINKING
            confidence = adjusted_advanced_score
            should_use_advanced = True
            reasoning = f"Advanced thinking needed: {advanced_reasoning}"
            
        elif score_diff < 0.15 and max(simple_score, adjusted_advanced_score) > 0.3:
            #Неоднозначна ситуація - гібридний підхід
            mode = ChatMode.HYBRID
            confidence = max(simple_score, adjusted_advanced_score)
            should_use_advanced = adjusted_advanced_score >= simple_score
            reasoning = f"Ambiguous case (diff: {score_diff:.2f}): prefer {'advanced' if should_use_advanced else 'simple'}"
            
        elif simple_score > 0.8:
            #Високий пріоритет простих команд
            mode = ChatMode.SIMPLE_COMMAND
            confidence = simple_score
            should_use_advanced = False
            reasoning = f"High priority simple command: {simple_reasoning}"
            
        else:
            #Вибір за найвищою оцінкою або за замовчуванням advanced для складних термінів
            has_complex_terms = any(term in original_message.lower() for term in 
                                  ["проаналізуй", "архітектур", "що не так", "покращ", "порівня"])
            
            if adjusted_advanced_score > simple_score or has_complex_terms:
                mode = ChatMode.ADVANCED_THINKING
                confidence = max(adjusted_advanced_score, 0.6)
                should_use_advanced = True
                reasoning = f"Fallback to advanced: scores(simple={simple_score:.2f}, advanced={adjusted_advanced_score:.2f})"
            else:
                mode = ChatMode.SIMPLE_COMMAND
                confidence = max(simple_score, 0.5)
                should_use_advanced = False
                reasoning = f"Fallback to simple: scores(simple={simple_score:.2f}, advanced={adjusted_advanced_score:.2f})"
        
        return DetectionResult(
            mode=mode,
            confidence=confidence,
            reasoning=reasoning,
            should_use_advanced=should_use_advanced,
            fallback_to_simple=(mode == ChatMode.HYBRID and not should_use_advanced)
        )
    
    def _log_detection(self, message: str, result: DetectionResult):
        """Логування для аналізу та покращення"""
        self.detection_stats["total_detections"] += 1
        
        mode_key = result.mode.value
        if mode_key not in self.detection_stats["mode_counts"]:
            self.detection_stats["mode_counts"][mode_key] = 0
        self.detection_stats["mode_counts"][mode_key] += 1
        
        self.logger.debug(f"Mode detection: '{message[:50]}...' -> {result.mode.value} (confidence: {result.confidence:.2f})")
    
    def get_detection_stats(self) -> Dict:
        """Getting статистики детекції"""
        return self.detection_stats.copy()
    
    def add_feedback(self, message: str, detected_mode: ChatMode, actual_mode: ChatMode, user_satisfaction: float):
        """Додавання зворотного зв'язку для покращення точності"""
        feedback = {
            "message": message,
            "detected": detected_mode.value,
            "actual": actual_mode.value,
            "satisfaction": user_satisfaction,
            "correct": detected_mode == actual_mode
        }
        self.detection_stats["accuracy_feedback"].append(feedback)


def test_mode_detector():
    """Тест інтелектуального детектора режимів"""
    print("🧠 ТЕСТ ІНТЕЛЕКТУАЛЬНОГО ДЕТЕКТОРА РЕЖИМІВ")
    print("=" * 60)
    
    detector = IntelligentModeDetector()
    
    #Тестові запити
    test_cases = [
        #Прості команди
        ("read file main.py", ChatMode.SIMPLE_COMMAND),
        ("list directory agents", ChatMode.SIMPLE_COMMAND),
        ("show tree", ChatMode.SIMPLE_COMMAND),
        ("search for MemoryManager", ChatMode.SIMPLE_COMMAND),
        ("info about config.py", ChatMode.SIMPLE_COMMAND),
        
        #Складні аналітичні запити
        ("Проаналізуй архітектуру пам'яті в Atlas", ChatMode.ADVANCED_THINKING),
        ("Що не так з модулем думання?", ChatMode.ADVANCED_THINKING),
        ("Як можна покращити продуктивність Atlas?", ChatMode.ADVANCED_THINKING),
        ("Порівняй різні стратегії мислення", ChatMode.ADVANCED_THINKING),
        ("Чому система працює повільно?", ChatMode.ADVANCED_THINKING),
        
        #Потенційно конфліктні
        ("search for architecture patterns", ChatMode.HYBRID),
        ("analyze file structure main.py", ChatMode.HYBRID),
        ("how does memory manager work?", ChatMode.ADVANCED_THINKING),
        ("show me how the system works", ChatMode.ADVANCED_THINKING),
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\n📋 Результати тестування:")
    print("-" * 60)
    
    for message, expected_mode in test_cases:
        result = detector.detect_chat_mode(message)
        is_correct = result.mode == expected_mode or (
            result.mode == ChatMode.HYBRID and result.should_use_advanced == (expected_mode == ChatMode.ADVANCED_THINKING)
        )
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} '{message}'")
        print(f"    Очікувано: {expected_mode.value}")
        print(f"    Детектовано: {result.mode.value} (впевненість: {result.confidence:.2f})")
        print(f"    Використати advanced: {result.should_use_advanced}")
        print(f"    Обґрунтування: {result.reasoning}")
        print()
    
    accuracy = correct / total * 100
    print(f"📊 Точність детекції: {accuracy:.1f}% ({correct}/{total})")
    
    #Статистика
    stats = detector.get_detection_stats()
    print("\n📈 Статистика детекції:")
    for mode, count in stats["mode_counts"].items():
        print(f"   • {mode}: {count}")
    
    return accuracy >= 80


if __name__ == "__main__":
    success = test_mode_detector()
    print(f"\n{'✅ Детектор працює відмінно!' if success else '⚠️ Детектор потребує покращення'}")
