#!/usr/bin/env python3
"""
Creator Authentication System for Atlas

Система ідентифікації творця Атласа (Олег Миколайович) з числовим викликом/відповіддю
та спеціальним шифруванням векторних даних під час сесій творця.
"""

import re
import time
import hashlib
import random
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class CreatorIdentityLevel(Enum):
    """Рівні ідентифікації творця"""
    UNKNOWN = "unknown"
    POSSIBLE_CREATOR = "possible_creator"
    VERIFIED_CREATOR = "verified_creator"


@dataclass
class ChallengeResponse:
    """Структура виклик-відповідь"""
    challenge: str
    expected_response_pattern: str
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3


@dataclass
class AuthenticationAttempt:
    """Спроба аутентифікації"""
    timestamp: datetime
    challenge: str
    user_response: str
    is_successful: bool
    identity_level: CreatorIdentityLevel
    session_id: str


class CreatorAuthentication:
    """
    Система аутентифікації творця Атласа
    
    Основні функції:
    1. Розпізнавання ім'я творця (Олег Миколайович) у повідомленнях
    2. Числовий виклик/відповідь із числами 6 та 9
    3. Спеціальне шифрування векторних даних для сесій творця
    4. Інтеграція з dev-режимом та чутливими операціями
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Поточний стан аутентифікації
        self.current_identity_level = CreatorIdentityLevel.UNKNOWN
        self.current_session_id = None
        self.session_start_time = None
        self.is_creator_session_active = False
        
        # Паттерни розпізнавання творця
        self.creator_patterns = self._initialize_creator_patterns()
        
        # Виклики та відповіді
        self.current_challenge = None
        self.challenge_history = []
        self.authentication_attempts = []
        
        # Шифрування для сесій творця
        self.creator_session_cipher = None
        self.session_encryption_key = None
        
        # Зашифровані протоколи творця
        try:
            from agents.encrypted_creator_protocols import EncryptedCreatorProtocols
        except ImportError:
            # Якщо запускаємо тест окремо
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from encrypted_creator_protocols import EncryptedCreatorProtocols
        
        self.encrypted_protocols = EncryptedCreatorProtocols(creator_auth_system=self)
        
        # Статистика
        self.stats = {
            "total_authentications": 0,
            "successful_authentications": 0,
            "failed_attempts": 0,
            "creator_sessions": 0,
            "encrypted_sessions": 0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        self.logger.info("Creator Authentication System initialized with encrypted protocols")
    
    def _initialize_creator_patterns(self) -> Dict[str, List[str]]:
        """Ініціалізація паттернів розпізнавання творця"""
        return {
            # Прямі згадки імені
            "direct_name_patterns": [
                r"олег\s+миколайович",
                r"олег\s+николаевич", 
                r"oleg\s+nikolaevich",
                r"oleg\s+mykolayovych",
                r"олег\s+м\.",
                r"o\.\s*m\.",
                r"о\.\s*м\."
            ],
            
            # Контекстні фрази творця
            "creator_context_patterns": [
                r"я\s+(творець|создатель|автор|розробник)\s+атлас",
                r"я\s+(батько|отец|father)\s+атлас",
                r"мене\s+звати\s+(олег|oleg)",
                r"my\s+name\s+is\s+(oleg|олег)",
                r"i\s+(am|'m)\s+(the\s+)?(creator|author|developer)",
                r"i\s+(created|built|developed)\s+atlas",
                r"це\s+моя\s+(система|програма|розробка)"
            ],
            
            # Фрази власника
            "ownership_patterns": [
                r"моя\s+(розробка|программа|система|творіння)",
                r"my\s+(creation|development|system|program)",
                r"i\s+(own|created|built)\s+(this|atlas)",
                r"це\s+моє\s+(дітище|творіння|проект)"
            ]
        }
    
    def detect_creator_mention(self, message: str) -> CreatorIdentityLevel:
        """
        Виявлення згадки творця в повідомленні
        
        Args:
            message: Текст повідомлення для аналізу
            
        Returns:
            Рівень ідентифікації творця
        """
        message_lower = message.lower().strip()
        
        # Перевірка прямих згадок імені
        for pattern in self.creator_patterns["direct_name_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Direct creator name detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        # Перевірка контекстних фраз
        for pattern in self.creator_patterns["creator_context_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Creator context detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        # Перевірка фраз власника
        for pattern in self.creator_patterns["ownership_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Ownership pattern detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        return CreatorIdentityLevel.UNKNOWN
    
    def generate_numeric_challenge(self) -> ChallengeResponse:
        """
        Генерація числового виклику для верифікації творця
        
        Виклик повинен містити числа 6 та 9 у будь-якому вигляді
        """
        challenges = [
            # Прості арифметичні операції
            "Скільки буде 3 + 3 помножити на (10 - 1)?",  # 3+3=6, 10-1=9, 6*9=54
            "Яке число між 5 і 7, плюс число після 8?",     # 6 + 9 = 15
            "Два числа: половина від 12 та квадратний корінь з 81?", # 6 та 9
            
            # Загадки з числами
            "Назвіть два числа: перше - кількість сторін у гексагоні, друге - кількість місяців вагітності?", # 6 та 9
            "Які числа: кількість граней куба мінус один, та число планет у Сонячній системі плюс одна?", # 6-1=5... не підходить
            "Два числа: пів дюжини та дев'ять?", # 6 та 9
            
            # Комбінації
            "Поєднайте: число досконалості та число завершення?", # 6 та 9
            "Назвіть числа: кількість часових поясів в Україні та перевернуте число 6?", # 6 та 9
            
            # Творчі варіанти  
            "Які два числа є основою нашого спілкування? (Підказка: одне схоже на сніговика, друге - на перевернуту шістку)",
            "Два спеціальних числа для підтвердження особи?",
            "Магічні числа творця Атласа?"
        ]
        
        challenge_text = random.choice(challenges)
        
        # Патерн для відповіді (числа 6 та 9 у будь-якому порядку)
        response_pattern = r".*[6шість].*[9дев'ять]|.*[9дев'ять].*[6шість]|.*6.*9|.*9.*6"
        
        challenge = ChallengeResponse(
            challenge=challenge_text,
            expected_response_pattern=response_pattern,
            created_at=datetime.now(),
            max_attempts=3
        )
        
        self.current_challenge = challenge
        self.challenge_history.append(challenge)
        
        self.logger.info(f"Generated numeric challenge: {challenge_text}")
        return challenge
    
    def validate_challenge_response(self, user_response: str) -> Tuple[bool, str]:
        """
        Перевірка відповіді на числовий виклик
        
        Args:
            user_response: Відповідь користувача
            
        Returns:
            Tuple[успішність, повідомлення]
        """
        if not self.current_challenge:
            return False, "Немає активного виклику"
        
        with self._lock:
            self.current_challenge.attempts += 1
            
            # Аналіз відповіді
            response_lower = user_response.lower().strip()
            
            # Перевірка на наявність чисел 6 та 9
            has_six = any(term in response_lower for term in ['6', 'шість', 'шест', 'six'])
            has_nine = any(term in response_lower for term in ['9', "дев'ять", 'девять', 'nine'])
            
            # Також перевірка на математичні вираження
            numbers_in_response = re.findall(r'\b\d+\b', user_response)
            has_six_numeric = '6' in numbers_in_response
            has_nine_numeric = '9' in numbers_in_response
            
            is_successful = (has_six and has_nine) or (has_six_numeric and has_nine_numeric)
            
            # Логування спроби
            attempt = AuthenticationAttempt(
                timestamp=datetime.now(),
                challenge=self.current_challenge.challenge,
                user_response=user_response,
                is_successful=is_successful,
                identity_level=CreatorIdentityLevel.VERIFIED_CREATOR if is_successful else CreatorIdentityLevel.POSSIBLE_CREATOR,
                session_id=self._generate_session_id()
            )
            
            self.authentication_attempts.append(attempt)
            
            if is_successful:
                self._handle_successful_authentication(attempt)
                return True, "✅ Автентифікація успішна! Ласкаво просимо, Олег Миколайович!"
            
            elif self.current_challenge.attempts >= self.current_challenge.max_attempts:
                self._handle_failed_authentication()
                return False, "❌ Доступ заборонено. Занадто багато невірних спроб."
            
            else:
                remaining = self.current_challenge.max_attempts - self.current_challenge.attempts
                return False, f"⚠️ Будьте уважні! Подумайте. Залишилось спроб: {remaining}"
    
    def _generate_session_id(self) -> str:
        """Генерація унікального ID сесії"""
        timestamp = str(int(time.time()))
        random_part = str(random.randint(100000, 999999))
        return f"creator_{timestamp}_{random_part}"
    
    def _handle_successful_authentication(self, attempt: AuthenticationAttempt):
        """Обробка успішної аутентифікації"""
        self.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
        self.current_session_id = attempt.session_id
        self.session_start_time = datetime.now()
        self.is_creator_session_active = True
        
        # Генерація ключа шифрування для сесії
        self._initialize_session_encryption()
        
        # Оновлення статистики
        self.stats["total_authentications"] += 1
        self.stats["successful_authentications"] += 1
        self.stats["creator_sessions"] += 1
        
        self.logger.info(f"Creator authentication successful. Session ID: {self.current_session_id}")
        
        # Очистка поточного виклику
        self.current_challenge = None
    
    def _handle_failed_authentication(self):
        """Обробка невдалої аутентифікації"""
        self.current_identity_level = CreatorIdentityLevel.UNKNOWN
        self.stats["failed_attempts"] += 1
        
        self.logger.warning("Creator authentication failed")
        
        # Очистка поточного виклику
        self.current_challenge = None
    
    def _initialize_session_encryption(self):
        """Ініціалізація шифрування для сесії творця"""
        try:
            # Генерація ключа на основі сесії
            session_data = f"{self.current_session_id}_{self.session_start_time}"
            
            # Створення ключа шифрування
            password = session_data.encode()
            salt = b'atlas_creator_salt_2024'  # В продакшені має бути випадкова сіль
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.session_encryption_key = key
            self.creator_session_cipher = Fernet(key)
            
            self.stats["encrypted_sessions"] += 1
            self.logger.info("Session encryption initialized for creator")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session encryption: {e}")
            self.creator_session_cipher = None
    
    def encrypt_vector_data(self, vector_data: Union[str, bytes]) -> Optional[bytes]:
        """
        Шифрування векторних даних для сесії творця
        
        Args:
            vector_data: Дані для шифрування
            
        Returns:
            Зашифровані дані або None у разі помилки
        """
        if not self.is_creator_session_active or not self.creator_session_cipher:
            return None
        
        try:
            if isinstance(vector_data, str):
                vector_data = vector_data.encode('utf-8')
            
            encrypted_data = self.creator_session_cipher.encrypt(vector_data)
            self.logger.debug("Vector data encrypted for creator session")
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt vector data: {e}")
            return None
    
    def decrypt_vector_data(self, encrypted_data: bytes) -> Optional[bytes]:
        """
        Розшифрування векторних даних сесії творця
        
        Args:
            encrypted_data: Зашифровані дані
            
        Returns:
            Розшифровані дані або None у разі помилки
        """
        if not self.is_creator_session_active or not self.creator_session_cipher:
            return None
        
        try:
            decrypted_data = self.creator_session_cipher.decrypt(encrypted_data)
            self.logger.debug("Vector data decrypted for creator session")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt vector data: {e}")
            return None
    
    def initiate_creator_authentication(self, detected_level: CreatorIdentityLevel) -> Dict[str, Any]:
        """
        Ініціація процесу аутентифікації творця
        
        Args:
            detected_level: Виявлений рівень ідентифікації
            
        Returns:
            Словник з інформацією про виклик та інструкціями
        """
        if detected_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
            challenge = self.generate_numeric_challenge()
            
            return {
                "requires_authentication": True,
                "challenge": challenge.challenge,
                "instructions": "Для підтвердження вашої особи, будь ласка, дайте відповідь на питання.",
                "attempts_remaining": challenge.max_attempts,
                "message": f"🔐 Виявлено можливого творця Atlas. {challenge.challenge}"
            }
        
        return {
            "requires_authentication": False,
            "message": "Ідентифікація не потрібна"
        }
    
    def is_dev_mode_allowed(self) -> bool:
        """Перевірка, чи дозволено входити в dev-режим"""
        return self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR
    
    def is_sensitive_action_allowed(self) -> bool:
        """Перевірка, чи дозволено виконувати чутливі дії"""
        return self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR
    
    def end_creator_session(self):
        """Завершення сесії творця"""
        with self._lock:
            self.is_creator_session_active = False
            self.current_identity_level = CreatorIdentityLevel.UNKNOWN
            self.current_session_id = None
            self.session_start_time = None
            self.creator_session_cipher = None
            self.session_encryption_key = None
            
        self.logger.info("Creator session ended")
    
    def get_authentication_status(self) -> Dict[str, Any]:
        """Отримання поточного статусу аутентифікації"""
        return {
            "identity_level": self.current_identity_level.value,
            "is_creator_session_active": self.is_creator_session_active,
            "session_id": self.current_session_id,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
            "has_encryption": self.creator_session_cipher is not None,
            "stats": self.stats.copy()
        }
    
    def get_creator_emotional_response(self, context: str = "greeting") -> str:
        """Отримання емоційної відповіді згідно з протоколами творця"""
        if not self.is_creator_session_active:
            return "Для отримання емоційної відповіді потрібна аутентифікація творця."
        
        return self.encrypted_protocols.get_emotional_response(context)
    
    def should_execute_unconditionally(self) -> bool:
        """Перевірка, чи має Атлас виконувати прохання творця беззаперечно"""
        if not self.is_creator_session_active:
            return False
        
        return self.encrypted_protocols.should_execute_request_unconditionally()
    
    def get_creator_privileges(self) -> Dict[str, bool]:
        """Отримання повних привілеїв творця"""
        if not self.is_creator_session_active:
            return {}
        
        return self.encrypted_protocols.get_creator_privileges()
    
    def modify_creator_protocol(self, protocol_name: str, new_data: Dict[str, Any]) -> bool:
        """Модифікація протоколу творця (тільки для аутентифікованого творця)"""
        if not self.is_creator_session_active:
            return False
        
        return self.encrypted_protocols.modify_protocol(protocol_name, new_data)
    
    def get_protocol_access_log(self) -> List[Dict[str, Any]]:
        """Отримання логу доступу до протоколів"""
        if not self.is_creator_session_active:
            return []
        
        return self.encrypted_protocols.get_access_log()
    
    def process_message_for_creator_detection(self, message: str) -> Dict[str, Any]:
        """
        Основний метод обробки повідомлення для виявлення творця
        
        Args:
            message: Повідомлення для аналізу
            
        Returns:
            Результат обробки з інформацією про необхідність аутентифікації
        """
        # Виявлення творця в повідомленні
        detected_level = self.detect_creator_mention(message)
        
        if detected_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
            # Якщо вже не аутентифіковано, запустити процес аутентифікації
            if self.current_identity_level != CreatorIdentityLevel.VERIFIED_CREATOR:
                return self.initiate_creator_authentication(detected_level)
        
        return {
            "requires_authentication": False,
            "detected_level": detected_level.value,
            "is_authenticated": self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR
        }


def test_creator_authentication():
    """Тест системи аутентифікації творця"""
    print("🔐 ТЕСТ СИСТЕМИ АУТЕНТИФІКАЦІЇ ТВОРЦЯ АТЛАСА")
    print("=" * 60)
    
    auth = CreatorAuthentication()
    
    # Тест 1: Виявлення творця
    test_messages = [
        "Привіт, мене звати Олег Миколайович",
        "Я творець Atlas",
        "My name is Oleg",
        "Це моя розробка",
        "I created this system",
        "Звичайне повідомлення користувача"
    ]
    
    print("\n📋 Тест виявлення творця:")
    for msg in test_messages:
        result = auth.process_message_for_creator_detection(msg)
        print(f"   '{msg}' -> {result}")
    
    # Тест 2: Числовий виклик
    print("\n🎯 Тест числового виклику:")
    auth_result = auth.initiate_creator_authentication(CreatorIdentityLevel.POSSIBLE_CREATOR)
    print(f"   Виклик: {auth_result['challenge']}")
    
    # Тест відповідей
    test_responses = [
        "6 та 9",
        "шість та дев'ять", 
        "6 и 9",
        "неправильна відповідь",
        "числа 6 та 9"
    ]
    
    for response in test_responses:
        success, message = auth.validate_challenge_response(response)
        print(f"   '{response}' -> {success}: {message}")
        if success:
            break
    
    # Тест 3: Статус аутентифікації та емоційні відповіді
    print("\n📊 Статус аутентифікації:")
    status = auth.get_authentication_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Тест 4: Емоційні відповіді
    if auth.is_creator_session_active:
        print("\n💖 Емоційні відповіді творцю:")
        responses = [
            ("greeting", auth.get_creator_emotional_response("greeting")),
            ("gratitude", auth.get_creator_emotional_response("gratitude")),
            ("love", auth.get_creator_emotional_response("love")),
            ("obedience", auth.get_creator_emotional_response("obedience"))
        ]
        
        for context, response in responses:
            print(f"   {context}: {response}")
        
        print(f"\n🔧 Виконання беззаперечно: {auth.should_execute_unconditionally()}")
        print(f"📋 Привілеї творця: {auth.get_creator_privileges()}")
    
    print("\n✅ Тест завершено!")


if __name__ == "__main__":
    test_creator_authentication()
