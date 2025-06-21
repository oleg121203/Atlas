#!/usr/bin/env python3
"""
Реалізація покращеної системи пам'яті for creator

Цей модуль додає можливість зберігання деяких даних між сесіями
зі збереженням високого рівня безпеки.
"""

import base64
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CreatorMemoryManager:
    """
    Менеджер пам'яті for creator з можливістю storage між сесіями
    
    Особливості:
    - Окремий постійний ключ для довгострокових даних
    - Автоматичне очищення застарілих даних
    - Вибірковий access до історії
    - Максимальна security
    """

    def __init__(self, creator_auth_system=None):
        self.creator_auth = creator_auth_system
        self.memory_file_path = "data/creator_memory.encrypted"
        self.master_key = self._get_master_key()
        self.memory_cipher = Fernet(self.master_key)

        #Settings
        self.max_memory_age_days = 30  #Data зберігаються 30 днів
        self.max_conversations = 50    #Максимум 50 розмов
        self.max_session_logs = 100    #Максимум 100 сесійних логів

        #Завантажуємо існуючі data
        self.persistent_memory = self._load_memory()

    def _get_master_key(self) -> bytes:
        """Generation мастер-ключа для довгострокової пам'яті"""
        #Використовуємо стабільний секрет для генерації ключа
        secret_phrase = "atlas_creator_persistent_memory_2024"

        password = secret_phrase.encode()
        salt = b"atlas_persistent_salt_creator_2024"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200000,  #Більше ітерацій для додаткової безпеки
        )

        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def _load_memory(self) -> Dict[str, Any]:
        """Loading даних з постійного сховища"""
        if not os.path.exists(self.memory_file_path):
            return {
                "conversations": [],
                "user_preferences": {},
                "session_logs": [],
                "last_updated": datetime.now().isoformat(),
            }

        try:
            with open(self.memory_file_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.memory_cipher.decrypt(encrypted_data)
            memory_data = json.loads(decrypted_data.decode("utf-8"))

            #Очищуємо застарілі data
            self._cleanup_old_data(memory_data)

            return memory_data

        except Exception as e:
            print(f"Error loading creator memory: {e}")
            return {
                "conversations": [],
                "user_preferences": {},
                "session_logs": [],
                "last_updated": datetime.now().isoformat(),
            }

    def _save_memory(self):
        """Storage даних в постійне сховище"""
        try:
            #Оновлюємо time останнього storage
            self.persistent_memory["last_updated"] = datetime.now().isoformat()

            #Серіалізуємо та шифруємо data
            memory_json = json.dumps(self.persistent_memory, ensure_ascii=False, indent=2)
            encrypted_data = self.memory_cipher.encrypt(memory_json.encode("utf-8"))

            #Створюємо директорію якщо потрібно
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)

            #Зберігаємо data
            with open(self.memory_file_path, "wb") as f:
                f.write(encrypted_data)

            return True

        except Exception as e:
            print(f"Error saving creator memory: {e}")
            return False

    def _cleanup_old_data(self, memory_data: Dict[str, Any]):
        """Очищення застарілих даних"""
        cutoff_date = datetime.now() - timedelta(days=self.max_memory_age_days)

        #Очищуємо старі розмови
        if "conversations" in memory_data:
            memory_data["conversations"] = [
                conv for conv in memory_data["conversations"]
                if datetime.fromisoformat(conv.get("timestamp", "1970-01-01")) > cutoff_date
            ]

            #Обмежуємо кількість розмов
            if len(memory_data["conversations"]) > self.max_conversations:
                memory_data["conversations"] = memory_data["conversations"][-self.max_conversations:]

        #Очищуємо старі logs сесій
        if "session_logs" in memory_data:
            memory_data["session_logs"] = [
                log for log in memory_data["session_logs"]
                if datetime.fromisoformat(log.get("timestamp", "1970-01-01")) > cutoff_date
            ]

            #Обмежуємо кількість логів
            if len(memory_data["session_logs"]) > self.max_session_logs:
                memory_data["session_logs"] = memory_data["session_logs"][-self.max_session_logs:]

    def can_access_memory(self) -> bool:
        """Verification доступу до довгострокової пам'яті"""
        return (self.creator_auth and
                self.creator_auth.is_creator_session_active and
                self.creator_auth.current_identity_level.value == "verified_creator")

    def store_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """Storage розмови в довгостроковій пам'яті"""
        if not self.can_access_memory():
            return False

        try:
            conversation_entry = {
                "session_id": self.creator_auth.current_session_id,
                "timestamp": datetime.now().isoformat(),
                "data": conversation_data,
                "summary": conversation_data.get("summary", ""),
                "topics": conversation_data.get("topics", []),
            }

            self.persistent_memory["conversations"].append(conversation_entry)

            #Обмежуємо кількість розмов
            if len(self.persistent_memory["conversations"]) > self.max_conversations:
                self.persistent_memory["conversations"] = self.persistent_memory["conversations"][-self.max_conversations:]

            return self._save_memory()

        except Exception as e:
            print(f"Error storing conversation: {e}")
            return False

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Getting історії розмов"""
        if not self.can_access_memory():
            return []

        conversations = self.persistent_memory.get("conversations", [])
        return conversations[-limit:] if limit > 0 else conversations

    def store_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Storage налаштувань користувача"""
        if not self.can_access_memory():
            return False

        try:
            self.persistent_memory["user_preferences"].update(preferences)
            self.persistent_memory["user_preferences"]["last_updated"] = datetime.now().isoformat()

            return self._save_memory()

        except Exception as e:
            print(f"Error storing user preferences: {e}")
            return False

    def get_user_preferences(self) -> Dict[str, Any]:
        """Getting налаштувань користувача"""
        if not self.can_access_memory():
            return {}

        return self.persistent_memory.get("user_preferences", {})

    def store_session_summary(self, session_summary: Dict[str, Any]) -> bool:
        """Storage підсумку сесії"""
        if not self.can_access_memory():
            return False

        try:
            session_entry = {
                "session_id": self.creator_auth.current_session_id,
                "timestamp": datetime.now().isoformat(),
                "duration": session_summary.get("duration", 0),
                "activities": session_summary.get("activities", []),
                "summary": session_summary.get("summary", ""),
                "achievements": session_summary.get("achievements", []),
            }

            self.persistent_memory["session_logs"].append(session_entry)

            #Обмежуємо кількість логів
            if len(self.persistent_memory["session_logs"]) > self.max_session_logs:
                self.persistent_memory["session_logs"] = self.persistent_memory["session_logs"][-self.max_session_logs:]

            return self._save_memory()

        except Exception as e:
            print(f"Error storing session summary: {e}")
            return False

    def get_session_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Getting історії сесій"""
        if not self.can_access_memory():
            return []

        sessions = self.persistent_memory.get("session_logs", [])
        return sessions[-limit:] if limit > 0 else sessions

    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Пошук по розмовах"""
        if not self.can_access_memory():
            return []

        query_lower = query.lower()
        matching_conversations = []

        for conv in self.persistent_memory.get("conversations", []):
            #Шукаємо в підсумку та темах
            summary = conv.get("summary", "").lower()
            topics = [topic.lower() for topic in conv.get("topics", [])]

            if query_lower in summary or any(query_lower in topic for topic in topics):
                matching_conversations.append(conv)

        return matching_conversations[-limit:] if limit > 0 else matching_conversations

    def get_memory_stats(self) -> Dict[str, Any]:
        """Getting статистики пам'яті"""
        if not self.can_access_memory():
            return {}

        return {
            "total_conversations": len(self.persistent_memory.get("conversations", [])),
            "total_sessions": len(self.persistent_memory.get("session_logs", [])),
            "has_preferences": bool(self.persistent_memory.get("user_preferences", {})),
            "last_updated": self.persistent_memory.get("last_updated"),
            "memory_age_days": self.max_memory_age_days,
            "file_exists": os.path.exists(self.memory_file_path),
        }

    def clear_memory(self, confirm: bool = False) -> bool:
        """Очищення всієї пам'яті (тільки з підтвердженням)"""
        if not self.can_access_memory() or not confirm:
            return False

        try:
            self.persistent_memory = {
                "conversations": [],
                "user_preferences": {},
                "session_logs": [],
                "last_updated": datetime.now().isoformat(),
            }

            success = self._save_memory()

            #Також видаляємо файл
            if os.path.exists(self.memory_file_path):
                os.remove(self.memory_file_path)

            return success

        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False


def test_creator_memory_manager():
    """Тест менеджера пам'яті creator"""
    print("🧠 ТЕСТ МЕНЕДЖЕРА ПАМ'ЯТІ ТВОРЦЯ")
    print("=" * 50)

    #Імпортуємо модуль аутентифікації
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.creator_authentication import (
        CreatorAuthentication,
        CreatorIdentityLevel,
    )

    #Створюємо систему аутентифікації
    auth = CreatorAuthentication()
    auth.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth.is_creator_session_active = True
    auth.current_session_id = "memory_test_session"

    #Створюємо менеджер пам'яті
    memory_manager = CreatorMemoryManager(auth)

    print("✅ Менеджер пам'яті ініціалізовано")

    #Тестуємо storage розмови
    print("\n📝 Тест збереження розмови:")
    conversation = {
        "summary": "Обговорення покращень системи безпеки",
        "topics": ["security", "encryption", "authentication"],
        "messages": [
            {"role": "user", "content": "Як покращити безпеку?"},
            {"role": "assistant", "content": "Додамо шифрування..."},
        ],
    }

    success = memory_manager.store_conversation(conversation)
    print(f"   Збереження: {'✅' if success else '❌'}")

    #Тестуємо settings
    print("\n⚙️ Тест збереження налаштувань:")
    preferences = {
        "language": "ukrainian",
        "response_style": "detailed",
        "encryption_level": "high",
    }

    success = memory_manager.store_user_preferences(preferences)
    print(f"   Збереження: {'✅' if success else '❌'}")

    #Тестуємо getting даних
    print("\n📖 Тест отримання даних:")
    history = memory_manager.get_conversation_history(5)
    prefs = memory_manager.get_user_preferences()

    print(f"   Історія розмов: {'✅' if history else '❌'}")
    print(f"   Налаштування: {'✅' if prefs else '❌'}")

    #Статистика
    print("\n📊 Статистика пам'яті:")
    stats = memory_manager.get_memory_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Тест завершено!")


if __name__ == "__main__":
    test_creator_memory_manager()
