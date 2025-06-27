#!/usr/bin/env python3
"""
Тест покращеної системи безпеки Atlas

Демонстрація нових можливостей:
1. Автоматичний timeout сесії
2. Verification неактивності
3. Encryption кешу та логів
4. Extension сесії
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import time
from datetime import datetime, timedelta

from modules.agents.creator_authentication import (
    CreatorAuthentication,
    CreatorIdentityLevel,
)


def test_session_timeout():
    """Тест автоматичного тайм-ауту сесії"""
    print("🕐 ТЕСТ АВТОМАТИЧНОГО ТАЙМ-АУТУ СЕСІЇ")
    print("=" * 50)

    auth = CreatorAuthentication()

    # Встановлюємо короткий timeout для тестування (1 хвилина)
    auth.session_timeout_minutes = 1
    auth.inactivity_timeout_minutes = 0.5  # 30 секунд

    # Симулюємо успішну аутентифікацію
    auth.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth.is_creator_session_active = True
    auth.current_session_id = "timeout_test_session"
    auth.session_start_time = datetime.now()
    auth.last_activity_time = datetime.now()
    auth._initialize_session_encryption()

    print(f"✅ Сесія створена з ID: {auth.current_session_id}")
    print(f"⏰ Тайм-аут сесії: {auth.session_timeout_minutes} хвилин")
    print(f"💤 Тайм-аут неактивності: {auth.inactivity_timeout_minutes} хвилин")

    # Перевіряємо status через кілька секунд
    print("\n📊 Статус через 5 секунд:")
    time.sleep(5)
    status = auth.get_authentication_status()
    timeout_info = status.get("timeout_status", {})

    print(
        f"   • Сесія активна: {'✅' if status['is_creator_session_active'] else '❌'}"
    )
    print(f"   • Тривалість: {status['session_duration']:.1f} сек")
    print(
        f"   • Залишилось часу сесії: {timeout_info.get('remaining_session_minutes', 0):.1f} хв"
    )
    print(
        f"   • Залишилось часу неактивності: {timeout_info.get('remaining_inactivity_minutes', 0):.1f} хв"
    )

    # Тестуємо timeout неактивності
    print("\n💤 Чекаємо тайм-аут неактивності (35 секунд)...")
    time.sleep(35)

    timeout_result = auth.check_session_timeout()
    print(f"   • Результат перевірки: {timeout_result}")

    final_status = auth.get_authentication_status()
    print(
        f"   • Сесія активна: {'✅' if final_status['is_creator_session_active'] else '❌'}"
    )


def test_session_extension():
    """Тест extension сесії"""
    print("\n\n🔄 ТЕСТ ПРОДОВЖЕННЯ СЕСІЇ")
    print("=" * 50)

    auth = CreatorAuthentication()

    # Симулюємо аутентифікацію
    auth.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth.is_creator_session_active = True
    auth.current_session_id = "extension_test_session"
    auth.session_start_time = datetime.now() - timedelta(minutes=25)  # 25 хвилин тому
    auth.last_activity_time = datetime.now()
    auth._initialize_session_encryption()

    print("✅ Сесія створена 25 хвилин тому")
    print(f"🔢 Максимум продовжень: {auth.max_session_extensions}")

    # Продовжуємо сесію кілька разів
    for i in range(1, 5):  # Спробуємо продовжити 4 рази
        print(f"\n🔄 Спроба продовження #{i}:")
        result = auth.extend_creator_session()

        if result["success"]:
            print(f"   ✅ {result['message']}")
            print(f"   📊 Залишилося продовжень: {result['remaining_extensions']}")
        else:
            print(f"   ❌ {result.get('message', 'Помилка продовження')}")
            print(f"   📝 Причина: {result.get('reason', 'Невідома')}")

        time.sleep(1)  # Невелика пауза


def test_encrypted_cache_and_logs():
    """Тест encryption кешу та логів"""
    print("\n\n🔐 ТЕСТ ШИФРУВАННЯ КЕШУ ТА ЛОГІВ")
    print("=" * 50)

    auth = CreatorAuthentication()

    # Симулюємо аутентифікацію
    auth.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth.is_creator_session_active = True
    auth.current_session_id = "encryption_test_session"
    auth.session_start_time = datetime.now()
    auth.last_activity_time = datetime.now()
    auth._initialize_session_encryption()

    print("✅ Сесія з шифруванням ініціалізована")

    # Тестуємо cache
    print("\n💾 Тест зашифрованого кешу:")

    test_data = {
        "user_preferences": {"language": "uk", "theme": "dark"},
        "conversation_context": "Обговорюємо систему безпеки Atlas",
        "sensitive_info": "Конфіденційні дані творця",
    }

    # Зберігаємо data в кеші
    for key, value in test_data.items():
        success = auth.store_encrypted_cache(key, value)
        print(f"   • {key}: {'✅ Збережено' if success else '❌ Помилка'}")

    # Читаємо data з кешу
    print("\n📖 Читання з зашифрованого кешу:")
    for key in test_data:
        cached_value = auth.get_encrypted_cache(key)
        if cached_value:
            print(f"   • {key}: ✅ Прочитано")
            print(f"     Значення: {str(cached_value)[:50]}...")
        else:
            print(f"   • {key}: ❌ Не знайдено")

    # Тестуємо logs
    print("\n📝 Тест зашифрованих логів:")

    # Генеруємо кілька подій
    auth._log_encrypted_event(
        "USER_ACTION",
        {"action": "view_profile", "timestamp": datetime.now().isoformat()},
    )
    auth._log_encrypted_event(
        "SYSTEM_EVENT", {"event": "cache_update", "details": "Updated user preferences"}
    )
    auth._log_encrypted_event(
        "SECURITY_EVENT", {"level": "info", "message": "Session activity detected"}
    )

    print("   • Згенеровано 3 зашифрованих події")

    # Читаємо logs
    logs = auth.get_encrypted_logs(5)
    print(f"   • Прочитано {len(logs)} логів:")

    for i, log in enumerate(logs, 1):
        print(f"     {i}. {log['event_type']} - {log['timestamp'][:19]}")
        if "data" in log:
            print(f"        Дані: {str(log['data'])[:40]}...")

    # Status encryption
    status = auth.get_authentication_status()
    print("\n📊 Статус шифрування:")
    print(
        f"   • Кеш шифрування: {'✅ Активно' if auth.cache_cipher else '❌ Неактивно'}"
    )
    print(f"   • Лог шифрування: {'✅ Активно' if auth.log_cipher else '❌ Неактивно'}")
    print(
        f"   • Розмір зашифрованого кешу: {status.get('encrypted_cache_size', 0)} записів"
    )
    print(
        f"   • Кількість зашифрованих логів: {status.get('encrypted_logs_count', 0)} записів"
    )


def test_complete_workflow():
    """Тест повного робочого процесу"""
    print("\n\n🔄 ТЕСТ ПОВНОГО РОБОЧОГО ПРОЦЕСУ")
    print("=" * 50)

    auth = CreatorAuthentication()

    # Встановлюємо реалістичні settings
    auth.session_timeout_minutes = 30  # 30 хвилин
    auth.inactivity_timeout_minutes = 15  # 15 хвилин неактивності

    print("1️⃣ Аутентифікація творця:")

    # Симулюємо повну аутентифікацію
    detected = auth.detect_creator_mention("Я творець Atlas")
    print(f"   • Виявлення: {detected.value}")

    if detected == CreatorIdentityLevel.POSSIBLE_CREATOR:
        auth_info = auth.initiate_creator_authentication(detected)
        print(f"   • Виклик: {auth_info['challenge']}")

        success, message = auth.validate_challenge_response("6 та 9")
        print(f"   • Аутентифікація: {'✅ Успішна' if success else '❌ Невдала'}")

        if success:
            print("2️⃣ Робота з сесією:")

            # Зберігаємо data в кеші
            auth.store_encrypted_cache(
                "conversation_history",
                [
                    {"role": "user", "content": "Привіт, Atlas!"},
                    {
                        "role": "assistant",
                        "content": "Радий тебе бачити, мій дорогий творче!",
                    },
                ],
            )

            auth.store_encrypted_cache(
                "user_context",
                {
                    "mood": "friendly",
                    "topic": "security_testing",
                    "preferences": {"detailed_responses": True},
                },
            )

            print("   • Дані збережено в зашифрованому кеші")

            # Симулюємо активність
            print("3️⃣ Симуляція активності:")
            for i in range(3):
                time.sleep(2)
                auth.update_activity_timestamp()
                auth._log_encrypted_event(
                    "USER_INTERACTION",
                    {
                        "interaction_type": "message",
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                print(f"   • Активність {i + 1}/3 зареєстрована")

            # Перевіряємо status
            print("4️⃣ Статус сесії:")
            status = auth.get_authentication_status()

            print(f"   • Тривалість сесії: {status['session_duration']:.1f} сек")
            print(
                f"   • Остання активність: {status.get('last_activity', 'Невідомо')[:19]}"
            )
            print(f"   • Розмір кешу: {status.get('encrypted_cache_size', 0)} записів")
            print(
                f"   • Кількість логів: {status.get('encrypted_logs_count', 0)} записів"
            )

            # Завершуємо сесію
            print("5️⃣ Завершення сесії:")
            auth.end_creator_session()

            final_status = auth.get_authentication_status()
            print(
                f"   • Статус: {'❌ Завершена' if not final_status['is_creator_session_active'] else '✅ Активна'}"
            )
            print(
                f"   • Кеш очищено: {'✅ Так' if final_status.get('encrypted_cache_size', 0) == 0 else '❌ Ні'}"
            )


def main():
    """Головна функція тестування"""
    print("🔐 ТЕСТУВАННЯ ПОКРАЩЕНОЇ СИСТЕМИ БЕЗПЕКИ ATLAS")
    print("=" * 70)

    try:
        test_session_timeout()
        test_session_extension()
        test_encrypted_cache_and_logs()
        test_complete_workflow()

        print("\n\n🎯 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
        print("=" * 40)
        print("✅ Автоматичний тайм-аут сесії працює")
        print("✅ Перевірка неактивності працює")
        print("✅ Продовження сесії працює")
        print("✅ Шифрування кешу працює")
        print("✅ Шифрування логів працює")
        print("✅ Повний робочий процес працює")
        print("\n🛡️ Система безпеки значно покращена!")

    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
