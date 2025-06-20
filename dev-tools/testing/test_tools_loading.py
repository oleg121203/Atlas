#!/usr/bin/env python3
"""
Тест loading інструментів при ініціалізації
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from utils.config_manager import ConfigManager
from agents.token_tracker import TokenTracker
from agents.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from agents.agent_manager import AgentManager

def test_tools_loading():
    print("🔧 Тест завантаження інструментів")
    print("=" * 50)
    
    try:
        #Initialization як в main.py
        print("📋 Ініціалізація менеджерів...")
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        
        print("🤖 Створення LLMManager...")
        llm_manager = LLMManager(token_tracker=token_tracker, config_manager=config_manager)
        
        print("🧠 Створення MemoryManager...")
        memory_manager = EnhancedMemoryManager(llm_manager=llm_manager, config_manager=config_manager)
        
        print("⚙️ Створення AgentManager...")
        agent_manager = AgentManager(llm_manager=llm_manager, memory_manager=memory_manager)
        
        print("✅ Всі менеджери створено")
        
        #Перевірити інструменти
        print("\n🛠️ Перевірка завантажених інструментів:")
        tool_names = agent_manager.get_tool_names()
        print(f"📊 Всього інструментів: {len(tool_names)}")
        
        if tool_names:
            print("📋 Список інструментів:")
            for i, tool_name in enumerate(sorted(tool_names), 1):
                print(f"  {i:2d}. {tool_name}")
        else:
            print("❌ Інструменти не знайдено!")
        
        #Перевірити деталі
        print("\n📄 Деталі інструментів:")
        tools_details = agent_manager.get_all_tools_details()
        print(f"📊 Деталей інструментів: {len(tools_details)}")
        
        builtin_count = 0
        generated_count = 0
        
        for tool in tools_details:
            tool_type = tool.get('type', 'unknown')
            if tool_type == 'generated':
                generated_count += 1
            else:
                builtin_count += 1
        
        print(f"🔧 Вбудовані інструменти: {builtin_count}")
        print(f"🎯 Згенеровані інструменти: {generated_count}")
        
        if builtin_count == 0:
            print("⚠️ ПРОБЛЕМА: Вбудовані інструменти не завантажились!")
        
        return len(tool_names) > 0
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tools_loading()
    
    if success:
        print("\n🎉 Інструменти завантажуються правильно!")
    else:
        print("\n⚠️ Проблема з завантаженням інструментів!")
