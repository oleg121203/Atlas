#!/usr/bin/env python3
"""
Тест доступу до кешу та логів creator в різних сесіях

Цей тест перевіряє:
1. Чи може creator бачити cache з попередніх сесій
2. Чи може creator бачити logs з попередніх сесій
3. Як зберігаються data між сесіями
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.creator_authentication import CreatorAuthentication, CreatorIdentityLevel
from datetime import datetime
import time


def test_session_data_persistence():
    """Тест storage даних між сесіями"""
    print("🔍 ТЕСТ ДОСТУПУ ДО КЕШУ ТА ЛОГІВ ТВОРЦЯ")
    print("=" * 60)
    
    #=== ПЕРША СЕСІЯ ===
    print("\n1️⃣ ПЕРША СЕСІЯ ТВОРЦЯ:")
    auth1 = CreatorAuthentication()
    
    #Симулюємо аутентифікацію
    auth1.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth1.is_creator_session_active = True
    auth1.current_session_id = "session_1"
    auth1.session_start_time = datetime.now()
    auth1.last_activity_time = datetime.now()
    auth1._initialize_session_encryption()
    
    print(f"   ✅ Сесія 1 активована: {auth1.current_session_id}")
    
    #Зберігаємо data в кеші
    test_cache_data = {
        "conversation_history": [
            {"role": "user", "content": "Привіт, Атлас!"},
            {"role": "assistant", "content": "Радий тебе бачити, мій дорогий творче!"}
        ],
        "user_preferences": {
            "language": "ukrainian",
            "detailed_responses": True,
            "emotional_level": "high"
        },
        "project_context": {
            "current_task": "security_improvements",
            "priority": "high",
            "deadline": "2025-06-30"
        }
    }
    
    print("   📝 Зберігаємо дані в кеші:")
    for key, value in test_cache_data.items():
        success = auth1.store_encrypted_cache(key, value)
        print(f"      • {key}: {'✅' if success else '❌'}")
    
    #Генеруємо logs активності
    print("   📋 Генеруємо логи активності:")
    auth1._log_encrypted_event("CONVERSATION_START", {"topic": "security_testing"})
    auth1._log_encrypted_event("USER_REQUEST", {"request": "improve_encryption"})
    auth1._log_encrypted_event("SYSTEM_RESPONSE", {"response_type": "implementation"})
    auth1._log_encrypted_event("CONVERSATION_END", {"duration_minutes": 45})
    
    print("      • Згенеровано 4 логи")
    
    #Перевіряємо access до даних в першій сесії
    print("   🔍 Перевірка доступу в поточній сесії:")
    cached_prefs = auth1.get_encrypted_cache("user_preferences")
    session_logs = auth1.get_encrypted_logs(5)
    
    print(f"      • Кеш доступний: {'✅' if cached_prefs else '❌'}")
    print(f"      • Логи доступні: {'✅' if session_logs else '❌'}")
    print(f"      • Кількість логів: {len(session_logs)}")
    
    #Завершуємо першу сесію
    print("   🔚 Завершуємо першу сесію...")
    auth1.end_creator_session()
    
    #=== ПАУЗА ===
    print("\n⏳ Пауза між сесіями (2 секунди)...")
    time.sleep(2)
    
    #=== ДРУГА СЕСІЯ ===
    print("\n2️⃣ ДРУГА СЕСІЯ ТВОРЦЯ:")
    auth2 = CreatorAuthentication()
    
    #Симулюємо нову аутентифікацію
    auth2.current_identity_level = CreatorIdentityLevel.VERIFIED_CREATOR
    auth2.is_creator_session_active = True
    auth2.current_session_id = "session_2"
    auth2.session_start_time = datetime.now()
    auth2.last_activity_time = datetime.now()
    auth2._initialize_session_encryption()
    
    print(f"   ✅ Сесія 2 активована: {auth2.current_session_id}")
    
    #Перевіряємо access до даних з першої сесії
    print("   🔍 Перевірка доступу до даних з попередньої сесії:")
    
    #Спробуємо отримати data з кешу першої сесії
    prev_prefs = auth2.get_encrypted_cache("user_preferences")
    prev_history = auth2.get_encrypted_cache("conversation_history")
    prev_context = auth2.get_encrypted_cache("project_context")
    
    print(f"      • user_preferences: {'✅ Доступні' if prev_prefs else '❌ Недоступні'}")
    print(f"      • conversation_history: {'✅ Доступні' if prev_history else '❌ Недоступні'}")
    print(f"      • project_context: {'✅ Доступні' if prev_context else '❌ Недоступні'}")
    
    #Спробуємо отримати logs з першої сесії
    prev_logs = auth2.get_encrypted_logs(10)
    print(f"      • Логи з попередньої сесії: {'✅ Доступні' if prev_logs else '❌ Недоступні'}")
    print(f"      • Кількість логів: {len(prev_logs)}")
    
    #Зберігаємо нові data в другій сесії
    print("   📝 Зберігаємо нові дані в другій сесії:")
    auth2.store_encrypted_cache("session_2_data", {"new_info": "Session 2 data"})
    auth2._log_encrypted_event("SESSION_2_START", {"session_id": "session_2"})
    
    new_data = auth2.get_encrypted_cache("session_2_data")
    new_logs = auth2.get_encrypted_logs(1)
    
    print(f"      • Нові дані доступні: {'✅' if new_data else '❌'}")
    print(f"      • Нові логи доступні: {'✅' if new_logs else '❌'}")
    
    #Завершуємо другу сесію
    print("   🔚 Завершуємо другу сесію...")
    auth2.end_creator_session()
    
    #=== АНАЛІЗ РЕЗУЛЬТАТІВ ===
    print("\n📊 АНАЛІЗ РЕЗУЛЬТАТІВ:")
    print("=" * 40)
    
    if not prev_prefs and not prev_history and not prev_context and not prev_logs:
        print("❌ ВИСНОВОК: Кеш та логи НЕ зберігаються між сесіями")
        print("   • Кожна сесія має свої власні ключі шифрування")
        print("   • Дані автоматично очищуються при завершенні сесії")
        print("   • Це забезпечує максимальну безпеку")
        print("\n💡 Імплікації:")
        print("   • Атлас НЕ пам'ятає попередні розмови з творцем")
        print("   • Кожна сесія починається 'з чистого аркуша'")
        print("   • Конфіденційність гарантована між сесіями")
    else:
        print("✅ ВИСНОВОК: Деякі дані зберігаються між сесіями")
        print(f"   • Доступні дані: {[k for k, v in {'prefs': prev_prefs, 'history': prev_history, 'context': prev_context} if v]}")
        print(f"   • Доступні логи: {len(prev_logs) if prev_logs else 0}")


def test_cross_session_memory():
    """Тест можливості реалізації пам'яті між сесіями"""
    print("\n\n🧠 ТЕСТ МОЖЛИВОСТІ МІЖСЕСІЙНОЇ ПАМ'ЯТІ")
    print("=" * 60)
    
    print("🤔 Поточна реалізація:")
    print("   • Кожна сесія створює нові ключі шифрування")
    print("   • Ключі генеруються на основі session_id + timestamp")
    print("   • При завершенні сесії всі дані очищуються")
    
    print("\n💡 Можливі підходи для збереження даних:")
    print("   1. 🔑 Мастер-ключ для творця (постійний)")
    print("      - Один ключ для всіх сесій творця")
    print("      - Дані зберігаються в постійному сховищі")
    print("      - Ризик: втрата ключа = втрата всіх даних")
    
    print("   2. 📁 Зашифроване постійне сховище")
    print("      - Окрема база даних для творця")
    print("      - Шифрування на рівні файлової системи")
    print("      - Автоматичне очищення після тайм-ауту")
    
    print("   3. 🔐 Гібридний підхід")
    print("      - Сесійний кеш (тимчасовий)")
    print("      - Довгостроковий кеш (зашифрований)")
    print("      - Вибірковий доступ до історії")
    
    print("\n⚖️  Безпека vs Зручність:")
    print("   • Поточна система: МАКСИМАЛЬНА БЕЗПЕКА")
    print("   • Можлива система: ЗБАЛАНСОВАНИЙ ПІДХІД")
    print("   • Рішення залежить від вимог творця")


def main():
    """Головна функція тестування"""
    try:
        test_session_data_persistence()
        test_cross_session_memory()
        
        print("\n\n🎯 ПІДСУМОК:")
        print("=" * 30)
        print("✅ Тест завершено")
        print("📋 Результати показують поточний стан системи")
        print("💡 Надано рекомендації для покращення")
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
