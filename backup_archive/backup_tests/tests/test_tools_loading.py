#!/usr/bin/env python3
"""
Тест loading інструментів при старті Atlas
"""

import os
import sys

# Додаємо шлях до проекту
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_tools_loading():
    """Тестуємо loading інструментів при старті."""
    print("🔧 ТЕСТ ЗАВАНТАЖЕННЯ ІНСТРУМЕНТІВ")
    print("=" * 50)

    try:
        from config_manager import ConfigManager
        from modules.agents.agent_manager import AgentManager
        from modules.agents.memory_manager import EnhancedMemoryManager
        from modules.agents.token_tracker import TokenTracker

        from utils.llm_manager import LLMManager

        print("📦 Ініціалізація компонентів...")

        # Ініціалізуємо компоненти
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(
            token_tracker=token_tracker, config_manager=config_manager
        )
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager, config_manager=config_manager
        )

        print("🤖 Створення AgentManager...")
        agent_manager = AgentManager(
            llm_manager=llm_manager, memory_manager=memory_manager
        )

        print("\n🔍 Перевірка завантажених інструментів...")
        tools = agent_manager.get_tool_descriptions()

        # Очікувані базові інструменти
        expected_tools = [
            "capture_screen",
            "get_clipboard_text",
            "set_clipboard_text",
            "click_at",
            "move_mouse",
            "type_text",
            "press_key",
            "ocr_image",
            "ocr_file",
            "find_template_in_image",
            "execute_command",
            "create_tool",
        ]

        print(f"📋 Загалом завантажено інструментів: {len(tools)}")
        print(f"🎯 Очікуваних базових інструментів: {len(expected_tools)}")

        missing_tools = []
        found_tools = []

        for tool_name in expected_tools:
            if tool_name in tools:
                found_tools.append(tool_name)
                print(f"  ✅ {tool_name}: завантажено")
            else:
                missing_tools.append(tool_name)
                print(f"  ❌ {tool_name}: відсутній")

        print("\n📊 Статистика:")
        print(f"  ✅ Знайдено: {len(found_tools)}")
        print(f"  ❌ Відсутніх: {len(missing_tools)}")

        # Показуємо всі доступні інструменти
        print(f"\n📄 Всі доступні інструменти ({len(tools)}):")
        for tool_name, description in tools.items():
            print(f"  • {tool_name}: {description[:60]}...")

        # Перевіряємо generated інструменти
        print("\n🔧 Перевірка згенерованих інструментів...")
        generated_dir = os.path.join(project_root, "tools", "generated")
        if os.path.exists(generated_dir):
            generated_files = [
                f
                for f in os.listdir(generated_dir)
                if f.endswith(".py") and not f.startswith("__")
            ]
            print(f"  📁 Знайдено файлів у tools/generated: {len(generated_files)}")
            for file in generated_files:
                print(f"    • {file}")
        else:
            print("  📁 Папка tools/generated не існує")

        # Фінальна оцінка
        success_rate = len(found_tools) / len(expected_tools) * 100
        print("\n🎯 Результат тесту:")
        print(f"  📈 Успішність завантаження: {success_rate:.1f}%")

        if success_rate >= 80:
            print("  🟢 ВІДМІННО: Більшість інструментів завантажена")
        elif success_rate >= 60:
            print("  🟡 ДОБРЕ: Деякі інструменти відсутні")
        else:
            print("  🔴 ПОГАНО: Багато інструментів не завантажено")

        return success_rate >= 80

    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_tools_loading()
    sys.exit(0 if success else 1)
