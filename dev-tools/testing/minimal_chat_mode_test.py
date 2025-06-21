#!/usr/bin/env python3
"""
Мінімальний тест режимів
"""

print("🧪 Тестування виправлених режимів")

#Імпорт основних класів
try:
    import sys
    sys.path.append('.')
    
    print("📥 Імпорт модулів...")
    from agents.chat_context_manager import ChatMode
    print("✅ Основні класи імпортовано")
    
    #Verification enum
    modes = list(ChatMode)
    print(f"✅ Режими: {[m.value for m in modes]}")
    
    #Тестування без memory_manager
    print("📝 Створення ChatContextManager...")
    from agents.chat_context_manager import ChatContextManager
    
    #Creation без залежностей
    manager = ChatContextManager(memory_manager=None)
    print("✅ ChatContextManager створено")
    
    #Простий тест
    print("🧪 Тестування простих повідомлень...")
    
    test_messages = [
        "Привіт",
        "Hi", 
        "яка погода?",
        "What's the weather?",
        "Tell me about Atlas",
        "Take a screenshot"
    ]
    
    for msg in test_messages:
        try:
            context = manager.analyze_message(msg)
            print(f"'{msg}' → {context.mode.value} (confidence: {context.confidence:.2f})")
        except Exception as e:
            print(f"'{msg}' → ERROR: {e}")
    
    print("✅ Базове тестування завершено")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
