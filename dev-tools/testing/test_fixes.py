#!/usr/bin/env python3
"""
Тест для перевірки виправлень зі збереженням налаштувань та memory manager.
"""

import sys
sys.path.append('/Users/dev/Documents/autoclicker')

from utils.config_manager import ConfigManager
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
from utils.llm_manager import LLMManager

def test_api_keys_saving():
    """Тест storage та loading API ключів."""
    print("🔧 Тестування збереження/завантаження API ключів...")
    
    config_manager = ConfigManager()
    
    #Створимо тестові settings
    test_settings = {
        "api_keys": {
            "openai": "test_openai_key",
            "gemini": "test_gemini_key", 
            "anthropic": "test_anthropic_key",
            "groq": "test_groq_key",
            "mistral": "test_mistral_key",
        },
        "current_provider": "gemini"
    }
    
    #Збережемо
    config_manager.save(test_settings)
    print("✅ Налаштування збережено")
    
    #Завантажимо знову
    loaded_settings = config_manager.load()
    
    #Перевіримо, чи всі ключі на місці
    api_keys = loaded_settings.get("api_keys", {})
    
    expected_keys = ["openai", "gemini", "anthropic", "groq", "mistral"]
    for key in expected_keys:
        if key in api_keys:
            print(f"✅ {key}: {api_keys[key]}")
        else:
            print(f"❌ {key}: НЕ ЗНАЙДЕНО")
    
    #Перевіримо провайдер
    provider = loaded_settings.get("current_provider", "")
    print(f"🎯 Провайдер: {provider}")
    
    return loaded_settings

def test_memory_manager():
    """Тест memory manager методів."""
    print("\n🧠 Тестування EnhancedMemoryManager...")
    
    config_manager = ConfigManager()
    llm_manager = LLMManager(config_manager)
    
    memory_manager = EnhancedMemoryManager(llm_manager, config_manager)
    
    #Тест add_memory_for_agent
    try:
        memory_id = memory_manager.add_memory_for_agent(
            agent_type=MemoryScope.CHAT_CONTEXT,
            memory_type=MemoryType.CASUAL_CHAT,
            content="Тестове повідомлення",
            metadata={"test": True}
        )
        print("✅ add_memory_for_agent працює")
    except Exception as e:
        print(f"❌ add_memory_for_agent НЕ працює: {e}")
    
    #Тест store_memory (старий API)
    try:
        memory_id = memory_manager.store_memory(
            agent_name="chat_context",
            memory_type=MemoryType.CASUAL_CHAT,
            content="Тестове повідомлення через store_memory",
            metadata={"test": True}
        )
        print("✅ store_memory працює")
    except Exception as e:
        print(f"❌ store_memory НЕ працює: {e}")
        
    #Тест retrieve_memories
    try:
        memories = memory_manager.retrieve_memories(
            agent_name="chat_context",
            memory_type=MemoryType.CASUAL_CHAT,
            query="тест",
            limit=5
        )
        print(f"✅ retrieve_memories працює (знайдено {len(memories)} спогадів)")
    except Exception as e:
        print(f"❌ retrieve_memories НЕ працює: {e}")

def test_llm_manager_providers():
    """Тест доступних провайдерів."""
    print("\n🤖 Тестування LLMManager провайдерів...")
    
    config_manager = ConfigManager()
    llm_manager = LLMManager(config_manager)
    
    providers = llm_manager.get_available_providers()
    print(f"🎯 Доступні провайдери: {list(providers.keys())}")
    
    for provider, models in providers.items():
        print(f"  📋 {provider}: {len(models)} моделей")

if __name__ == "__main__":
    print("🚀 Запуск тестів для перевірки виправлень Atlas...")
    print("=" * 60)
    
    #Тест 1: API ключі
    settings = test_api_keys_saving()
    
    #Тест 2: Memory Manager
    test_memory_manager()
    
    #Тест 3: LLM Manager
    test_llm_manager_providers()
    
    print("\n" + "=" * 60)
    print("🏁 Тести завершено!")
