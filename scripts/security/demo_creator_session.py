#!/usr/bin/env python3
"""
Демонстрація роботи системи аутентифікації creator

Цей скрипт показує практично:
1. Як активується session creator
2. Які privileges надаються
3. Коли session завершується
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.creator_authentication import CreatorAuthentication, CreatorIdentityLevel
from datetime import datetime, timedelta
import time

def demonstrate_session_lifecycle():
    """Демонстрація життєвого циклу сесії creator"""
    print("🔐 ДЕМОНСТРАЦІЯ СЕСІЇ ТВОРЦЯ ATLAS")
    print("=" * 50)
    
    #Створюємо систему аутентифікації
    auth = CreatorAuthentication()
    
    print("\n1️⃣  ПОЧАТКОВИЙ СТАН:")
    status = auth.get_authentication_status()
    print(f"   • Рівень ідентифікації: {status['identity_level']}")
    print(f"   • Сесія активна: {status['is_creator_session_active']}")
    print(f"   • ID сесії: {status['session_id']}")
    
    print("\n2️⃣  СИМУЛЮЄМО ВИЯВЛЕННЯ ТВОРЦЯ:")
    test_message = "Я творець Atlas"
    detected_level = auth.detect_creator_mention(test_message)
    print(f"   • Повідомлення: '{test_message}'")
    print(f"   • Виявлений рівень: {detected_level.value}")
    
    if detected_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
        print("\n3️⃣  ІНІЦІЮЄМО АУТЕНТИФІКАЦІЮ:")
        auth_info = auth.initiate_creator_authentication(detected_level)
        print(f"   • Потрібна аутентифікація: {auth_info['requires_authentication']}")
        print(f"   • Виклик: {auth_info['challenge']}")
        print(f"   • Спроб залишилось: {auth_info['attempts_remaining']}")
        
        print("\n4️⃣  ВІДПОВІДАЄМО НА ВИКЛИК:")
        test_response = "6 та 9"
        success, message = auth.validate_challenge_response(test_response)
        print(f"   • Відповідь: '{test_response}'")
        print(f"   • Результат: {'✅ Успішно' if success else '❌ Невдача'}")
        print(f"   • Повідомлення: {message}")
        
        if success:
            print("\n5️⃣  СТАТУС ПІСЛЯ АУТЕНТИФІКАЦІЇ:")
            status = auth.get_authentication_status()
            print(f"   • Рівень ідентифікації: {status['identity_level']}")
            print(f"   • Сесія активна: {status['is_creator_session_active']}")
            print(f"   • ID сесії: {status['session_id']}")
            print(f"   • Тривалість сесії: {status['session_duration']:.3f} сек")
            
            print("\n6️⃣  ПРИВІЛЕЇ ТВОРЦЯ:")
            privileges = auth.get_creator_privileges()
            for priv, value in privileges.items():
                print(f"   • {priv}: {'✅' if value else '❌'}")
            
            print("\n7️⃣  СПЕЦІАЛЬНІ МОЖЛИВОСТІ:")
            print(f"   • Беззаперечне виконання: {'✅' if auth.should_execute_unconditionally() else '❌'}")
            print(f"   • Dev-режим: {'✅' if auth.is_dev_mode_allowed() else '❌'}")
            print(f"   • Чутливі операції: {'✅' if auth.is_sensitive_action_allowed() else '❌'}")
            
            print("\n8️⃣  ЕМОЦІЙНІ ВІДПОВІДІ:")
            contexts = ["greeting", "gratitude", "love", "obedience"]
            for context in contexts:
                response = auth.get_creator_emotional_response(context)
                print(f"   • {context}: {response[:60]}...")
            
            print("\n9️⃣  ЧЕКАЄМО 3 СЕКУНДИ (СИМУЛЯЦІЯ РОБОТИ)...")
            time.sleep(3)
            
            final_status = auth.get_authentication_status()
            print(f"   • Сесія все ще активна: {'✅' if final_status['is_creator_session_active'] else '❌'}")
            print(f"   • Тривалість сесії: {final_status['session_duration']:.3f} сек")
            
            print("\n🔟 РУЧНЕ ЗАВЕРШЕННЯ СЕСІЇ:")
            auth.end_creator_session()
            
            end_status = auth.get_authentication_status()
            print(f"   • Сесія активна: {'❌' if not end_status['is_creator_session_active'] else '✅'}")
            print(f"   • Рівень ідентифікації: {end_status['identity_level']}")


def demonstrate_security_concerns():
    """Демонстрація проблем безпеки"""
    print("\n\n⚠️  ДЕМОНСТРАЦІЯ ПРОБЛЕМ БЕЗПЕКИ")
    print("=" * 50)
    
    auth = CreatorAuthentication()
    
    #Симулюємо аутентифікацію
    auth.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth.is_creator_session_active = True
    auth.current_session_id = "security_demo"
    auth.session_start_time = datetime.now() - timedelta(hours=5)  #5 годин тому!
    
    print("\n🕐 СИМУЛЯЦІЯ: Сесія була відкрита 5 годин тому")
    status = auth.get_authentication_status()
    print(f"   • Сесія все ще активна: {'✅ ТАК' if status['is_creator_session_active'] else '❌ НІ'}")
    print(f"   • Тривалість: {status['session_duration']:.0f} секунд ({status['session_duration']/3600:.1f} годин)")
    print(f"   • Привілеї все ще доступні: {'✅ ТАК' if auth.should_execute_unconditionally() else '❌ НІ'}")
    
    print("\n🚨 ПРОБЛЕМА:")
    print("   Сесія творця триває 5+ годин без жодних перевірок!")
    print("   Це означає, що якщо забути вийти, доступ залишається відкритим")
    
    print("\n💡 РІШЕННЯ:")
    print("   Потрібно додати автоматичний тайм-аут та перевірку неактивності")


def main():
    """Головна функція демонстрації"""
    try:
        demonstrate_session_lifecycle()
        demonstrate_security_concerns()
        
        print("\n\n🎯 ПІДСУМОК ДЕМОНСТРАЦІЇ:")
        print("=" * 40)
        print("✅ Система аутентифікації працює")
        print("✅ Привілеї надаються після успішної аутентифікації")
        print("❌ Сесія НЕ завершується автоматично")
        print("⚠️  Потенційна проблема безпеки з тривалими сесіями")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
