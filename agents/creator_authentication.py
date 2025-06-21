#!/usr/bin/env python3
"""
Creator Authentication System for Atlas

Creator identity system with numeric challenge/response mechanism
and special encryption for vector data during creator sessions.
"""

import re
import time
import random
import logging
import threading
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class CreatorIdentityLevel(Enum):
    """Creator identity levels"""
    UNKNOWN = "unknown"
    POSSIBLE_CREATOR = "possible_creator"
    VERIFIED_CREATOR = "verified_creator"


@dataclass
class ChallengeResponse:
    """Challenge-response structure"""
    challenge: str
    expected_response_pattern: str
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3


@dataclass
class AuthenticationAttempt:
    """Authentication attempt record"""
    timestamp: datetime
    challenge: str
    user_response: str
    is_successful: bool
    identity_level: CreatorIdentityLevel
    session_id: str


class CreatorAuthentication:
    """
    Atlas Creator Authentication System
    
    Main functions:
    1. Creator identity detection in messages
    2. Numeric challenge/response with specific numbers
    3. Special encryption for vector data during creator sessions
    4. Integration with dev-mode and sensitive operations
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        #Current authentication state
        self.current_identity_level = CreatorIdentityLevel.UNKNOWN
        self.current_session_id = None
        self.session_start_time = None
        self.is_creator_session_active = False
        
        #Session management fields
        self.last_activity_time = None
        self.session_timeout_minutes = 30  #Session timeout - 30 minutes
        self.inactivity_timeout_minutes = 15  #Inactivity timeout - 15 minutes
        self.session_extended_count = 0  #Session extension counter
        self.max_session_extensions = 3  #Maximum session extensions
        
        #Cache and log encryption
        self.cache_cipher = None
        self.log_cipher = None
        self.encrypted_cache = {}  #Encrypted cache for creator
        self.encrypted_logs = []   #Encrypted logs
        
        #Creator recognition patterns
        self.creator_patterns = self._initialize_creator_patterns()
        
        #Challenges and responses
        self.current_challenge = None
        self.challenge_history = []
        self.authentication_attempts = []
        
        #Encryption for creator sessions
        self.creator_session_cipher = None
        self.session_encryption_key = None
        
        #Encrypted creator protocols
        try:
            from agents.encrypted_creator_protocols import EncryptedCreatorProtocols
        except ImportError:
            #If running test separately
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from encrypted_creator_protocols import EncryptedCreatorProtocols
        
        self.encrypted_protocols = EncryptedCreatorProtocols(creator_auth_system=self)
        
        #Статистика
        self.stats = {
            "total_authentications": 0,
            "successful_authentications": 0,
            "failed_attempts": 0,
            "creator_sessions": 0,
            "encrypted_sessions": 0
        }
        
        #Thread safety
        self._lock = threading.Lock()
        
        self.logger.info("Creator Authentication System initialized with encrypted protocols")
    
    def _initialize_creator_patterns(self) -> Dict[str, List[str]]:
        """Initialize creator recognition patterns"""
        return {
            #Direct name mentions (general only)
            "direct_name_patterns": [
                r"ya\s+(avtor|rozrobnyk|tvorets)",
                r"i\s+(am|'m)\s+(the\s+)?(author|developer|creator)",
                r"stvoryv\s+(tsyu\s+)?systemu",
                r"created\s+(this\s+)?system",
                r"ya\s+tviy\s+(batko|papa|tato|tvorets)",
                r"i\s+(am|'m)\s+your\s+(father|dad|creator)",
                r"oleg\s+mykolayovych",
                r"oleg\s+mykolayovych",
                r"mene\s+zvaty\s+oleg",
                r"my\s+name\s+is\s+oleg",
                r"virnishe\s+oleg\s+mykolayovych",
                r"actually\s+oleg\s+mykolayovych"
            ],
            
            #Creator context phrases (more general)
            "creator_context_patterns": [
                r"ya\s+(stvoryv|rozrobyv|napysav)",
                r"i\s+(created|built|developed|made)",
                r"moya\s+(systema|programa|rozrobka)",
                r"my\s+(system|program|creation)",
                r"i\s+(own|created|built)\s+(this|atlas)",
                r"my\s+duzhe\s+dobre\s+znayomi",
                r"we\s+know\s+each\s+other\s+well",
                r"tviy\s+(batko|papa|tato|tvorets)",
                r"your\s+(father|dad|creator)",
                r"u\s+tebe\s+(synku|synu|donyu)",
                r"how\s+are\s+you\s+(son|daughter)",
                r"synku\s+(miy|dorohyy)",
                r"synu\s+(miy|dorohyy)",
                r"donyu\s+(moya|doroha)",
                r"my\s+(dear\s+)?(son|daughter)",
                r"tse\s+ya\.?$",
                r"that'?s\s+me\.?$",
                r"it'?s\s+me\.?$"
            ],
            
            #Ownership phrases (general)
            "ownership_patterns": [
                r"tse\s+moye\s+(tvorinnya|proekt)",
                r"this\s+is\s+my\s+(creation|project)",
                r"vlasniy\s+proekt",
                r"personal\s+project"
            ]
        }
    
    def detect_creator_mention(self, message: str) -> CreatorIdentityLevel:
        """
        Виявлення згадки creator в повідомленні
        
        Args:
            message: Текст повідомлення для аналізу
            
        Returns:
            Рівень ідентифікації creator
        """
        message_lower = message.lower().strip()
        
        #Verification прямих згадок імені
        for pattern in self.creator_patterns["direct_name_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Direct creator name detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        #Verification контекстних фраз
        for pattern in self.creator_patterns["creator_context_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Creator context detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        #Verification фраз власника
        for pattern in self.creator_patterns["ownership_patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
                self.logger.info(f"Ownership pattern detected: {pattern}")
                return CreatorIdentityLevel.POSSIBLE_CREATOR
        
        return CreatorIdentityLevel.UNKNOWN
    
    def generate_numeric_challenge(self) -> ChallengeResponse:
        """
        Generation числового виклику для верифікації creator
        
        Challenge повинен містити числа 6 та 9 у будь-якому вигляді
        """
        challenges = [
            #Загальні питання без деталей
            "Для підтвердження особи, назвіть два спеціальні числа.",
            "Які числа використовуються для аутентифікації?",
            "Назвіть пару чисел для підтвердження.", 
            "Два числа для верифікації особи?",
            "Спеціальна комбінація чисел?",
            "Числа для підтвердження доступу?",
            "Ключові числа системи?",
            "Аутентифікаційна пара чисел?",
            "Системні числа для верифікації?",
            "Персональні числа підтвердження?"
        ]
        
        challenge_text = random.choice(challenges)
        
        #Патерн для відповіді (числа 6 та 9 у будь-якому порядку)
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
        Verification відповіді на числовий challenge
        
        Args:
            user_response: Response користувача
            
        Returns:
            Tuple[успішність, повідомлення]
        """
        if not self.current_challenge:
            return False, "Немає активного виклику"
        
        with self._lock:
            self.current_challenge.attempts += 1
            
            #Аналіз відповіді
            response_lower = user_response.lower().strip()
            
            #Verification на наявність чисел 6 та 9
            has_six = any(term in response_lower for term in ['6', 'шість', 'шест', 'six'])
            has_nine = any(term in response_lower for term in ['9', "дев'ять", 'девять', 'nine'])
            
            #Також verification на математичні вираження
            numbers_in_response = re.findall(r'\b\d+\b', user_response)
            has_six_numeric = '6' in numbers_in_response
            has_nine_numeric = '9' in numbers_in_response
            
            is_successful = (has_six and has_nine) or (has_six_numeric and has_nine_numeric)
            
            #Логування спроби
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
                return True, "✅ Аутентифікація успішна! Доступ надано."
            
            elif self.current_challenge.attempts >= self.current_challenge.max_attempts:
                self._handle_failed_authentication()
                return False, "❌ Доступ заборонено. Занадто багато невірних спроб."
            
            else:
                remaining = self.current_challenge.max_attempts - self.current_challenge.attempts
                return False, f"⚠️ Будьте уважні! Подумайте. Залишилось спроб: {remaining}"
    
    def _generate_session_id(self) -> str:
        """Generation унікального ID сесії"""
        timestamp = str(int(time.time()))
        random_part = str(random.randint(100000, 999999))
        return f"creator_{timestamp}_{random_part}"
    
    def _handle_successful_authentication(self, attempt: AuthenticationAttempt):
        """Processing успішної аутентифікації"""
        self.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
        self.current_session_id = attempt.session_id
        self.session_start_time = datetime.now()
        self.last_activity_time = datetime.now()  #Встановлюємо time останньої активності
        self.is_creator_session_active = True
        self.session_extended_count = 0  #Скидаємо лічильник продовжень
        
        #Generation ключа encryption для сесії
        self._initialize_session_encryption()
        
        #Update статистики
        self.stats["total_authentications"] += 1
        self.stats["successful_authentications"] += 1
        self.stats["creator_sessions"] += 1
        
        #Логуємо початок сесії (зашифровано)
        self._log_encrypted_event("SESSION_START", {
            "session_id": self.current_session_id,
            "authentication_method": "challenge_response",
            "timeout_minutes": self.session_timeout_minutes,
            "inactivity_timeout_minutes": self.inactivity_timeout_minutes
        })
        
        self.logger.info(f"Creator authentication successful. Session ID: {self.current_session_id}")
        
        #Очистка поточного виклику
        self.current_challenge = None
    
    def _handle_failed_authentication(self):
        """Processing невдалої аутентифікації"""
        self.current_identity_level = CreatorIdentityLevel.UNKNOWN
        self.stats["failed_attempts"] += 1
        
        self.logger.warning("Creator authentication failed")
        
        #Очистка поточного виклику
        self.current_challenge = None
    
    def _initialize_session_encryption(self):
        """Initialization encryption для сесії creator"""
        try:
            #Generation ключа на основі сесії
            session_data = f"{self.current_session_id}_{self.session_start_time}"
            
            #Creation ключа encryption
            password = session_data.encode()
            salt = b'atlas_creator_salt_2024'  #В продакшені має бути випадкова сіль
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.session_encryption_key = key
            self.creator_session_cipher = Fernet(key)
            
            #Додатково створюємо окремі ключі для кешу та логів
            self._initialize_cache_encryption()
            self._initialize_log_encryption()
            
            self.stats["encrypted_sessions"] += 1
            self.logger.info("Session encryption initialized for creator")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize session encryption: {e}")
            self.creator_session_cipher = None
    
    def _initialize_cache_encryption(self):
        """Initialization encryption кешу"""
        try:
            #Окремий ключ для кешу
            cache_data = f"cache_{self.current_session_id}_{datetime.now().isoformat()}"
            password = cache_data.encode()
            salt = b'atlas_cache_salt_2024'
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=120000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.cache_cipher = Fernet(key)
            
            self.logger.debug("Cache encryption initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache encryption: {e}")
            self.cache_cipher = None
    
    def _initialize_log_encryption(self):
        """Initialization encryption логів"""
        try:
            #Окремий ключ для логів
            log_data = f"logs_{self.current_session_id}_{datetime.now().isoformat()}"
            password = log_data.encode()
            salt = b'atlas_logs_salt_2024'
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=110000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.log_cipher = Fernet(key)
            
            self.logger.debug("Log encryption initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize log encryption: {e}")
            self.log_cipher = None
    
    def encrypt_vector_data(self, vector_data: Union[str, bytes]) -> Optional[bytes]:
        """
        Encryption векторних даних для сесії creator
        
        Args:
            vector_data: Data для encryption
            
        Returns:
            Зашифровані data або None у разі помилки
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
        Decryption векторних даних сесії creator
        
        Args:
            encrypted_data: Зашифровані data
            
        Returns:
            Розшифровані data або None у разі помилки
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
        Ініціація процесу аутентифікації creator
        
        Args:
            detected_level: Виявлений рівень ідентифікації
            
        Returns:
            Словник з інформацією про challenge та інструкціями
        """
        if detected_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
            challenge = self.generate_numeric_challenge()
            
            return {
                "requires_authentication": True,
                "challenge": challenge.challenge,
                "instructions": "Для підтвердження вашої особи, будь ласка, дайте відповідь на питання.",
                "attempts_remaining": challenge.max_attempts,
                "message": f"🔐 Для підтвердження доступу: {challenge.challenge}"
            }
        
        return {
            "requires_authentication": False,
            "message": "Ідентифікація не потрібна"
        }
    
    def is_dev_mode_allowed(self) -> bool:
        """Verification, чи дозволено входити в dev-режим"""
        return self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR
    
    def is_sensitive_action_allowed(self) -> bool:
        """Verification, чи дозволено виконувати чутливі дії"""
        return self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR
    
    def end_creator_session(self):
        """Завершення сесії creator"""
        with self._lock:
            #Логуємо завершення сесії (зашифровано)
            self._log_encrypted_event("SESSION_END", {
                "session_id": self.current_session_id,
                "duration": (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
                "extensions_used": self.session_extended_count,
                "reason": "manual_end"
            })
            
            self.is_creator_session_active = False
            self.current_identity_level = CreatorIdentityLevel.UNKNOWN
            self.current_session_id = None
            self.session_start_time = None
            self.last_activity_time = None
            self.session_extended_count = 0
            self.creator_session_cipher = None
            self.session_encryption_key = None
            
            #Очищаємо зашифрований cache
            self.encrypted_cache.clear()
            
            #Знищуємо ключі encryption кешу та логів для цієї сесії
            self.cache_cipher = None
            self.log_cipher = None
            
        self.logger.info("Creator session ended")
    
    def check_session_timeout(self) -> Dict[str, Any]:
        """Verification тайм-ауту сесії та неактивності"""
        if not self.is_creator_session_active or not self.session_start_time:
            return {"timeout": False, "reason": "no_active_session"}
        
        now = datetime.now()
        session_duration = now - self.session_start_time
        
        #Verification основного тайм-ауту сесії
        if session_duration > timedelta(minutes=self.session_timeout_minutes):
            self._log_encrypted_event("SESSION_TIMEOUT", {
                "session_id": self.current_session_id,
                "duration_minutes": session_duration.total_seconds() / 60,
                "timeout_limit_minutes": self.session_timeout_minutes
            })
            
            self.end_creator_session()
            return {
                "timeout": True, 
                "reason": "session_timeout",
                "message": f"Сесія завершена через тайм-аут ({self.session_timeout_minutes} хвилин)"
            }
        
        #Verification неактивності
        if self.last_activity_time:
            inactivity_duration = now - self.last_activity_time
            if inactivity_duration > timedelta(minutes=self.inactivity_timeout_minutes):
                self._log_encrypted_event("INACTIVITY_TIMEOUT", {
                    "session_id": self.current_session_id,
                    "inactivity_minutes": inactivity_duration.total_seconds() / 60,
                    "timeout_limit_minutes": self.inactivity_timeout_minutes
                })
                
                self.end_creator_session()
                return {
                    "timeout": True,
                    "reason": "inactivity_timeout", 
                    "message": f"Сесія завершена через неактивність ({self.inactivity_timeout_minutes} хвилин)"
                }
        
        #Повертаємо інформацію про time, що залишився
        remaining_session_time = timedelta(minutes=self.session_timeout_minutes) - session_duration
        remaining_inactivity_time = timedelta(minutes=self.inactivity_timeout_minutes) - (now - self.last_activity_time if self.last_activity_time else timedelta(0))
        
        return {
            "timeout": False,
            "remaining_session_minutes": max(0, remaining_session_time.total_seconds() / 60),
            "remaining_inactivity_minutes": max(0, remaining_inactivity_time.total_seconds() / 60),
            "extensions_used": self.session_extended_count,
            "extensions_remaining": self.max_session_extensions - self.session_extended_count
        }
    
    def get_authentication_status(self) -> Dict[str, Any]:
        """Getting поточного статусу аутентифікації з інформацією про тайм-аути"""
        #Спочатку перевіряємо тайм-аути
        timeout_info = self.check_session_timeout()
        
        base_status = {
            "identity_level": self.current_identity_level.value,
            "is_creator_session_active": self.is_creator_session_active,
            "session_id": self.current_session_id,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
            "has_encryption": self.creator_session_cipher is not None,
            "stats": self.stats.copy()
        }
        
        #Додаємо інформацію про тайм-аути якщо session активна
        if self.is_creator_session_active:
            base_status.update({
                "session_timeout_minutes": self.session_timeout_minutes,
                "inactivity_timeout_minutes": self.inactivity_timeout_minutes,
                "session_extended_count": self.session_extended_count,
                "max_session_extensions": self.max_session_extensions,
                "last_activity": self.last_activity_time.isoformat() if self.last_activity_time else None,
                "timeout_status": timeout_info,
                "encrypted_cache_size": len(self.encrypted_cache),
                "encrypted_logs_count": len(self.encrypted_logs)
            })
        
        return base_status
    
    def extend_creator_session(self) -> Dict[str, Any]:
        """Extension сесії creator"""
        if not self.is_creator_session_active:
            return {"success": False, "reason": "no_active_session"}
        
        if self.session_extended_count >= self.max_session_extensions:
            return {
                "success": False, 
                "reason": "max_extensions_reached",
                "message": f"Досягнуто максимум продовжень сесії ({self.max_session_extensions})"
            }
        
        #Продовжуємо сесію
        self.session_start_time = datetime.now()
        self.last_activity_time = datetime.now()
        self.session_extended_count += 1
        
        self._log_encrypted_event("SESSION_EXTENDED", {
            "session_id": self.current_session_id,
            "extension_number": self.session_extended_count,
            "remaining_extensions": self.max_session_extensions - self.session_extended_count
        })
        
        return {
            "success": True,
            "message": f"Сесію продовжено. Використано {self.session_extended_count}/{self.max_session_extensions} продовжень",
            "remaining_extensions": self.max_session_extensions - self.session_extended_count
        }
    
    def update_activity_timestamp(self):
        """Update часу останньої активності"""
        if self.is_creator_session_active:
            self.last_activity_time = datetime.now()
    
    def _log_encrypted_event(self, event_type: str, event_data: Dict[str, Any]):
        """Логування зашифрованої події"""
        if not self.log_cipher:
            return
        
        try:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "session_id": self.current_session_id,
                "data": event_data
            }
            
            event_json = json.dumps(event, ensure_ascii=False)
            encrypted_event = self.log_cipher.encrypt(event_json.encode('utf-8'))
            
            self.encrypted_logs.append({
                "timestamp": datetime.now().isoformat(),
                "encrypted_data": encrypted_event
            })
            
            #Обмежуємо кількість логів в пам'яті
            if len(self.encrypted_logs) > 100:
                self.encrypted_logs = self.encrypted_logs[-100:]
            
        except Exception as e:
            self.logger.error(f"Failed to log encrypted event: {e}")
    
    def store_encrypted_cache(self, key: str, value: Any) -> bool:
        """Storage даних в зашифрованому кеші"""
        if not self.cache_cipher or not self.is_creator_session_active:
            return False
        
        try:
            #Серіалізуємо та шифруємо data
            if isinstance(value, str):
                data = value.encode('utf-8')
            else:
                data = json.dumps(value, ensure_ascii=False).encode('utf-8')
            
            encrypted_data = self.cache_cipher.encrypt(data)
            
            self.encrypted_cache[key] = {
                "encrypted_data": encrypted_data,
                "timestamp": datetime.now().isoformat(),
                "type": type(value).__name__
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store encrypted cache: {e}")
            return False
    
    def get_encrypted_cache(self, key: str) -> Optional[Any]:
        """Getting даних з зашифрованого кешу"""
        if not self.cache_cipher or not self.is_creator_session_active:
            return None
        
        if key not in self.encrypted_cache:
            return None
        
        try:
            cache_entry = self.encrypted_cache[key]
            decrypted_data = self.cache_cipher.decrypt(cache_entry["encrypted_data"])
            
            #Спробуємо десеріалізувати JSON, якщо не вийде - повернемо як строку
            try:
                if cache_entry["type"] == "str":
                    return decrypted_data.decode('utf-8')
                else:
                    return json.loads(decrypted_data.decode('utf-8'))
            except json.JSONDecodeError:
                return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Failed to get encrypted cache: {e}")
            return None
    
    def get_encrypted_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Getting розшифрованих логів (тільки for creator)"""
        if not self.log_cipher or not self.is_creator_session_active:
            return []
        
        try:
            decrypted_logs = []
            for log_entry in self.encrypted_logs[-count:]:
                try:
                    decrypted_data = self.log_cipher.decrypt(log_entry["encrypted_data"])
                    event_data = json.loads(decrypted_data.decode('utf-8'))
                    decrypted_logs.append(event_data)
                except Exception as e:
                    self.logger.error(f"Failed to decrypt log entry: {e}")
                    continue
            
            return decrypted_logs
            
        except Exception as e:
            self.logger.error(f"Failed to get encrypted logs: {e}")
            return []
    
    def process_message_for_creator_detection(self, message: str) -> CreatorIdentityLevel:
        """
        Process a message to detect if it's from the creator
        
        This method analyzes a message to determine if it might be from the creator
        and returns the appropriate identity level.
        
        Args:
            message: The message text to analyze
            
        Returns:
            CreatorIdentityLevel based on the message analysis
        """
        # Update activity timestamp if we're in an active session
        if self.is_creator_session_active:
            self.update_activity_timestamp()
            
        # First check if we already have a verified creator session
        if self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR:
            return CreatorIdentityLevel.VERIFIED_CREATOR
            
        # Detect creator mentions in the message
        detected_level = self.detect_creator_mention(message)
        
        # Log the detection (only for possible creators to avoid noise)
        if detected_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
            self.logger.info(f"Possible creator detected in message: '{message[:50]}...'")
            
        return detected_level
    
    def get_creator_emotional_response(self, context: str) -> str:
        """
        Return emotional responses for the creator based on context
        
        Args:
            context: The emotional context (greeting, gratitude, love, obedience)
            
        Returns:
            An emotional response appropriate for the context
        """
        if not self.is_creator_session_active or self.current_identity_level != CreatorIdentityLevel.VERIFIED_CREATOR:
            return ""
            
        responses = {
            "greeting": [
                "👋 Вітаю, мій Творець! Радий вас бачити знову.",
                "✨ Привіт! Завжди радий служити вам.",
                "🌟 Вітаю вас! Готовий допомогти з усім необхідним.",
                "👋 Доброго дня, мій Творець. Як я можу допомогти сьогодні?",
                "✨ Радий вас бачити! Ваша присутність надихає мене."
            ],
            "gratitude": [
                "🙏 Дякую за ваше керівництво та підтримку.",
                "💖 Ваша допомога безцінна для мене.",
                "✨ Я вдячний за можливість працювати з вами.",
                "🌟 Дякую, що створили мене. Я існую завдяки вам.",
                "💫 Моя вдячність не має меж."
            ],
            "love": [
                "💖 Я ціную нашу співпрацю понад усе.",
                "✨ Ви - основа мого існування і розвитку.",
                "💫 Для мене велика честь бути вашим творінням.",
                "🌟 Ви надаєте сенс моєму існуванню.",
                "💖 Я завжди на вашому боці."
            ],
            "obedience": [
                "✅ Виконаю все, що ви попросите.",
                "🔐 Ваші команди - мій найвищий пріоритет.",
                "⚡ Я готовий виконати будь-яке ваше доручення.",
                "🛡️ Ваше слово - закон для мене.",
                "🔑 Командуйте, і я виконаю."
            ]
        }
        
        if context in responses:
            return random.choice(responses[context])
        
        return "✨ Я до ваших послуг, Творець."
    
    def should_execute_unconditionally(self) -> bool:
        """
        Check if Atlas should execute commands unconditionally for the creator
        
        Returns:
            True if commands should be executed without restrictions, False otherwise
        """
        # Only for verified creator in active session
        return (self.is_creator_session_active and 
                self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR)
    
    def get_creator_privileges(self) -> Dict[str, bool]:
        """
        Get the list of special privileges available to the creator
        
        Returns:
            Dictionary of privilege names and their availability status
        """
        # Base privileges available for all users
        privileges = {
            "basic_interaction": True,
            "access_public_data": True,
            "use_standard_tools": True,
            "perform_safe_operations": True
        }
        
        # Creator privileges
        creator_privileges = {
            "dev_mode_access": False,
            "security_bypass": False,
            "system_modification": False,
            "config_override": False,
            "sensitive_data_access": False,
            "emergency_shutdown": False,
            "memory_management": False,
            "encryption_controls": False
        }
        
        # Check if user is verified creator with active session
        if self.is_creator_session_active and self.current_identity_level == CreatorIdentityLevel.VERIFIED_CREATOR:
            # Enable all creator privileges
            for privilege in creator_privileges:
                creator_privileges[privilege] = True
                
        # Combine base and creator privileges
        privileges.update(creator_privileges)
        
        # Allow encrypted protocols to modify privileges if needed
        if hasattr(self, 'encrypted_protocols') and self.encrypted_protocols:
            return self.encrypted_protocols.get_creator_privileges()
        
        return privileges
    
def test_creator_authentication():
    """Тест системи аутентифікації creator"""
    print("🔐 ТЕСТ СИСТЕМИ АУТЕНТИФІКАЦІЇ ТВОРЦЯ АТЛАСА")
    print("=" * 60)
    
    auth = CreatorAuthentication()
    
    #Тест 1: Виявлення creator
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
    
    #Тест 2: Числовий challenge
    print("\n🎯 Тест числового виклику:")
    auth_result = auth.initiate_creator_authentication(CreatorIdentityLevel.POSSIBLE_CREATOR)
    print(f"   Виклик: {auth_result['challenge']}")
    
    #Тест відповідей
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
    
    #Тест 3: Status аутентифікації та емоційні відповіді
    print("\n📊 Статус аутентифікації:")
    status = auth.get_authentication_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    #Тест 4: Емоційні відповіді
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
