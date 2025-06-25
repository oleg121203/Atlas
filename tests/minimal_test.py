#!/usr/bin/env python3
"""Мінімальний тест TaskManager"""

import os
import sys

sys.path.insert(0, "/Users/developer/Documents/Atlas")
os.chdir("/Users/developer/Documents/Atlas")

#Тест імпортів
print("1. Тестую імпорти...")

try:
    from modules.agents.token_tracker import TokenTracker
    print("✅ TokenTracker")
except Exception as e:
    print(f"❌ TokenTracker: {e}")

try:
    from utils.llm_manager import LLMManager
    print("✅ LLMManager")
except Exception as e:
    print(f"❌ LLMManager: {e}")

try:
    from config_manager import ConfigManager
    print("✅ ConfigManager")
except Exception as e:
    print(f"❌ ConfigManager: {e}")

try:
    from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
    print("✅ EnhancedMemoryManager")
except Exception as e:
    print(f"❌ EnhancedMemoryManager: {e}")

try:
    from modules.agents.agent_manager import AgentManager
    print("✅ AgentManager")
except Exception as e:
    print(f"❌ AgentManager: {e}")

print("\n2. Тестую створення компонентів...")

try:
    from modules.agents.token_tracker import TokenTracker
    from utils.llm_manager import LLMManager

    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker)
    print("✅ LLMManager створено")

    from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
    from config_manager import ConfigManager

    config = ConfigManager()
    memory = EnhancedMemoryManager(llm_manager, config)
    print("✅ MemoryManager створено")

    from modules.agents.agent_manager import AgentManager
    agent_manager = AgentManager(llm_manager, memory)
    print("✅ AgentManager створено")

    print("\n🎉 Всі компоненти працюють!")

except Exception as e:
    print(f"❌ Помилка створення: {e}")
    import traceback
    traceback.print_exc()
