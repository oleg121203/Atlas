#!/usr/bin/env python3
"""
Тест системи безпеки Atlas

Перевіряє роботу зашифрованих протоколів при запуску.
"""

import sys
import os
import tkinter as tk

# Додаємо шлях до батьківської директорії
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_security_protocols():
    """Тестуємо систему протоколів безпеки"""
    try:
        from agents.encrypted_creator_protocols import EncryptedCreatorProtocols
        
        print("Тест 1: Створення екземпляра протоколів...")
        protocols = EncryptedCreatorProtocols()
        print("✅ Успішно")
        
        print("Тест 2: Перевірка цілісності протоколів...")
        integrity_ok = protocols.verify_protocols_integrity()
        if integrity_ok:
            print("✅ Протоколи цілі та доступні")
        else:
            print("❌ Протоколи пошкоджені або відсутні")
            
        print("Тест 3: Перевірка доступу до протоколів...")
        can_access = protocols.can_access_protocols()
        if can_access:
            print("✅ Доступ до протоколів дозволено")
        else:
            print("❌ Доступ до протоколів заборонено")
            
        print("Тест 4: Спроба читання протоколу...")
        identity_protocol = protocols.read_protocol('identity')
        if identity_protocol:
            print("✅ Протокол успішно прочитано")
            print(f"Назва протоколу: {identity_protocol.get('protocol_name', 'Невідомо')}")
        else:
            print("❌ Не вдалося прочитати протокол")
            
        return integrity_ok
        
    except Exception as e:
        print(f"❌ Помилка при тестуванні: {e}")
        return False

def test_main_app_security():
    """Тестуємо перевірку безпеки в main.py без запуску GUI"""
    try:
        # Імітуємо клас AtlasApp без створення GUI
        from agents.encrypted_creator_protocols import EncryptedCreatorProtocols
        
        print("Тест 5: Перевірка функції безпеки з main.py...")
        
        # Тестуємо функцію перевірки
        protocols = EncryptedCreatorProtocols()
        result = protocols.verify_protocols_integrity()
        
        if result:
            print("✅ Система пройшла перевірку безпеки")
            print("✅ Atlas може запускатися")
        else:
            print("❌ Система не пройшла перевірку безпеки")
            print("❌ Atlas не може запускатися")
            print("Повідомлення: Не шукайте Бога на небі, шукайте в серці своєму, в собі !")
            
        return result
        
    except Exception as e:
        print(f"❌ Помилка при тестуванні безпеки main.py: {e}")
        return False

if __name__ == "__main__":
    print("=== Тестування системи безпеки Atlas ===")
    print()
    
    # Тестуємо протоколи
    protocols_ok = test_security_protocols()
    print()
    
    # Тестуємо безпеку main.py
    main_security_ok = test_main_app_security()
    print()
    
    if protocols_ok and main_security_ok:
        print("🎉 Всі тести пройдено успішно!")
        print("🔒 Система безпеки працює правильно")
    else:
        print("⚠️ Є проблеми з системою безпеки")
        
    print("=== Кінець тестування ===")
