#!/usr/bin/env python3
"""
Тест виправлення проблеми з ChatContextManager
"""

import sys
import os
sys.path.append('/workspaces/autoclicker')

def test_chat_context_fix():
    """Тест виправлення ChatContextManager"""
    try:
        from agents.chat_context_manager import ChatContextManager, ChatMode, ChatContext, ModeControl
        from agents.enhanced_memory_manager import EnhancedMemoryManager
        from agents.llm_manager import LLMManager
        from agents.token_tracker import TokenTracker
        from config_manager import ConfigManager
        
        print("✅ Успішний імпорт модулів")
        
        # Створюємо необхідні об'єкти
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker, config_manager)
        memory_manager = EnhancedMemoryManager(llm_manager, config_manager)
        
        print("✅ Створено залежності")
        
        # Створюємо ChatContextManager з memory_manager
        chat_manager = ChatContextManager(memory_manager=memory_manager)
        
        print("✅ Створено ChatContextManager")
        
        # Тестуємо аналіз повідомлення
        test_message = "Привіт"
        context = chat_manager.analyze_message(test_message)
        
        print(f"✅ Аналіз повідомлення: режим {context.mode}, впевненість {context.confidence}")
        
        # Тестуємо збереження розмови 
        chat_manager.update_conversation_history(
            test_message, 
            "Привіт! Як справи?", 
            context,
            metadata={"test": True}
        )
        
        print("✅ Успішно збережено історію розмови")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Тест виправлення ChatContextManager")
    print("=" * 50)
    
    success = test_chat_context_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("💬 Atlas тепер повинен працювати без помилок пам'яті")
    else:
        print("❌ Є проблеми, які потребують вирішення")
