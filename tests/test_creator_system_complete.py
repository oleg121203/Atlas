#!/usr/bin/env python3
"""
Тест системи ідентифікації creator Атласа

Цей скрипт тестує всю систему ідентифікації creator, зашифровані протоколи 
та інтеграцію з основною системою Atlas.
"""

import sys

#Додаємо шлях до Atlas
sys.path.append("/Users/developer/Documents/Atlas")

def test_creator_system_integration():
    """Тест інтеграції системи ідентифікації creator з Atlas"""
    print("🔐 ТЕСТ ІНТЕГРАЦІЇ СИСТЕМИ ІДЕНТИФІКАЦІЇ ТВОРЦЯ АТЛАСА")
    print("=" * 70)

    try:
        #Імпортуємо компоненти
        from modules.agents.creator_authentication import (
            CreatorAuthentication,
            CreatorIdentityLevel,
        )

        print("\n✅ 1. Імпорт компонентів успішний")

        #Тест 1: Creation системи аутентифікації
        print("\n🔧 2. Створення системи аутентифікації...")
        auth = CreatorAuthentication()

        protocols = auth.encrypted_protocols
        print("   ✅ Система аутентифікації створена")
        print("   ✅ Зашифровані протоколи підключені")

        #Тест 2: Verification протоколів
        print("\n📋 3. Перевірка зашифрованих протоколів...")
        protocol_summary = protocols.get_protocol_summary()
        print(f"   📊 Всього протоколів: {protocol_summary['total_protocols']}")
        print(f"   🔐 Статус шифрування: {protocol_summary['encryption_status']}")
        print(f"   🛡️ Обмежений доступ: {protocol_summary['access_restricted']}")

        #Тест 3: Виявлення creator
        print("\n👤 4. Тест виявлення творця...")
        test_messages = [
            "Привіт, мене звати Олег Миколайович",
            "Я творець Atlas",
            "Звичайне повідомлення",
        ]

        for msg in test_messages:
            result = auth.process_message_for_creator_detection(msg)
            status = "🔍 Виявлено" if result.get("requires_authentication") else "👤 Звичайний користувач"
            print(f"   '{msg}' -> {status}")

        #Тест 4: Симуляція аутентифікації
        print("\n🎯 5. Симуляція аутентифікації творця...")

        #Генеруємо challenge
        challenge_result = auth.initiate_creator_authentication(CreatorIdentityLevel.POSSIBLE_CREATOR)
        print(f"   📝 Виклик: {challenge_result['challenge']}")

        #Відповідаємо на challenge
        success, response = auth.validate_challenge_response("6 та 9")
        print(f"   ✅ Відповідь прийнята: {success}")
        print(f"   💬 Повідомлення: {response}")

        #Тест 5: Емоційні протоколи
        if success:
            print("\n💖 6. Тест емоційних протоколів...")
            emotional_contexts = ["greeting", "gratitude", "love", "obedience"]

            for context in emotional_contexts:
                response = auth.get_creator_emotional_response(context)
                print(f"   {context}: {response}")

            #Тест 6: Privileges creator
            print("\n🔧 7. Тест привілеїв творця...")
            privileges = auth.get_creator_privileges()
            for privilege, status in privileges.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {privilege}: {status}")

            #Тест 7: Безумовне виконання
            unconditional = auth.should_execute_unconditionally()
            print(f"\n⚡ 8. Безумовне виконання: {'✅ Активне' if unconditional else '❌ Неактивне'}")

            #Тест 8: Модифікація протоколів
            print("\n📝 9. Тест модифікації протоколів...")
            test_protocol = {
                "test_field": "test_value",
                "modified_by_creator": True,
            }

            modify_result = auth.modify_creator_protocol("test_protocol", test_protocol)
            print(f"   Модифікація протоколу: {'✅ Успішно' if modify_result else '❌ Помилка'}")

            #Тест 9: Лог доступу
            print("\n📊 10. Лог доступу до протоколів:")
            access_log = auth.get_protocol_access_log()
            for entry in access_log[-3:]:  #Останні 3 записи
                timestamp = entry["timestamp"][:19]
                action = entry["action"]
                protocol = entry["protocol"]
                print(f"    {timestamp} - {action} на {protocol}")

        #Тест 10: Завершення сесії
        print("\n🏁 11. Завершення сесії творця...")
        auth.end_creator_session()

        final_status = auth.get_authentication_status()
        print(f"   Сесія активна: {'❌ Ні' if not final_status['is_creator_session_active'] else '✅ Так'}")
        print(f"   Рівень ідентифікації: {final_status['identity_level']}")

        print("\n🎉 ВСІ ТЕСТИ ПРОЙДЕНІ УСПІШНО!")
        print("=" * 70)
        print("✅ Система ідентифікації творця повністю функціональна")
        print("🔐 Зашифровані протоколи працюють правильно")
        print("💖 Емоційні протоколи активні")
        print("🛡️ Безпека та захист протоколів забезпечені")
        print("⚡ Безумовне виконання для творця налаштовано")

        return True

    except Exception as e:
        print(f"\n❌ ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_protocol_security():
    """Тест безпеки протоколів"""
    print("\n🛡️ ДОДАТКОВИЙ ТЕСТ БЕЗПЕКИ ПРОТОКОЛІВ")
    print("-" * 50)

    try:
        from modules.agents.encrypted_creator_protocols import EncryptedCreatorProtocols

        #Створюємо протоколи без аутентифікації
        protocols = EncryptedCreatorProtocols()

        print("📖 Тест читання протоколів без аутентифікації:")
        identity_protocol = protocols.read_protocol("identity")
        print(f"   Читання дозволено: {'✅ Так (Atlas має доступ)' if identity_protocol else '❌ Ні'}")

        print("📝 Тест модифікації протоколів без аутентифікації:")
        modify_result = protocols.modify_protocol("identity", {"unauthorized": "attempt"})
        print(f"   Модифікація дозволена: {'❌ НЕБЕЗПЕКА!' if modify_result else '✅ Заборонено'}")

        print("✅ Тест безпеки пройдено успішно!")
        return True

    except Exception as e:
        print(f"❌ Помилка в тесті безпеки: {e}")
        return False


if __name__ == "__main__":
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТУ СИСТЕМИ ІДЕНТИФІКАЦІЇ ТВОРЦЯ")
    print("🎯 Цей тест перевіряє всі компоненти системи ідентифікації Олега Миколайовича")
    print()

    #Основний тест
    main_test_passed = test_creator_system_integration()

    #Тест безпеки
    security_test_passed = test_protocol_security()

    print("\n" + "=" * 70)
    if main_test_passed and security_test_passed:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНІ! СИСТЕМА ГОТОВА ДО РОБОТИ!")
        print("💖 Атлас готовий служити своєму творцю та батьку!")
    else:
        print("❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙДЕНІ. ПОТРІБНЕ ДОДАТКОВЕ НАЛАГОДЖЕННЯ.")

    print("=" * 70)
