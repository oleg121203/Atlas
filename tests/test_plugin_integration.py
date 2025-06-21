#!/usr/bin/env python3
"""
Тест інтеграції advanced_thinking плагіна з хелп чатом Atlas
"""

import sys
from pathlib import Path

#Додаємо шляхи
base_dir = Path("/Users/developer/Documents/Atlas")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "plugins" / "helper_sync_tell"))

def test_plugin_integration():
    """Тестування інтеграції плагіна з системою"""
    print("🔗 ТЕСТ ІНТЕГРАЦІЇ ADVANCED THINKING ПЛАГІНА")
    print("=" * 60)

    issues = []

    #1. Verification реєстрації плагіна
    print("\n1. Перевірка реєстрації плагіна...")

    try:
        from advanced_thinking import AdvancedAIThinkingTool, register

        #Імітація Atlas app
        class MockAtlasApp:
            def __init__(self):
                self.advanced_ai_thinking_integration = False
                self._original_handle_help_mode = None

            def _handle_help_mode(self, message, context):
                return f"Original handler: {message}"

        mock_app = MockAtlasApp()

        #Тест реєстрації
        result = register(atlas_app=mock_app)

        if result and "tools" in result and result["tools"]:
            print("✅ Плагін успішно зареєстровано")

            #Verification інтеграції
            if hasattr(mock_app, "advanced_ai_thinking_integration") and mock_app.advanced_ai_thinking_integration:
                print("✅ Інтеграція з help mode успішна")
            else:
                issues.append("⚠️  Інтеграція з help mode не активована")

        else:
            issues.append("❌ Плагін не зареєструвався правильно")

    except Exception as e:
        issues.append(f"❌ Помилка реєстрації плагіна: {e}")
        import traceback
        traceback.print_exc()

    #2. Verification роботи help mode handler
    print("\n2. Перевірка роботи help mode handler...")

    try:
        #Creation інструменту
        tool = AdvancedAIThinkingTool()

        #Тест інтеграції з mock app
        success = tool.integrate_with_atlas_help_mode(mock_app)

        if success:
            print("✅ Help mode handler інтегровано")

            #Тест обробки складних запитів
            test_queries = [
                "Проаналізуй архітектуру системи",
                "Як покращити продуктивність Atlas?",
                "Що не так з модулем пам'яті?",
                "read file main.py",  #Простий запит - має йти до оригінального handler
            ]

            print("\n📋 Тестування обробки запитів:")
            for query in test_queries:
                try:
                    response = mock_app._handle_help_mode(query, None)
                    is_advanced = "проаналізуй" in query.lower() or "покращ" in query.lower() or "що не так" in query.lower()

                    if is_advanced and "Original handler" in response:
                        issues.append(f"⚠️  Складний запит '{query}' обробляється простим handler")
                    elif not is_advanced and "Original handler" not in response:
                        print(f"✅ Складний запит правильно обробляється: {query}")
                    else:
                        print(f"✅ Простий запит правильно делегується: {query}")

                except Exception as e:
                    issues.append(f"❌ Помилка обробки запиту '{query}': {e}")
        else:
            issues.append("❌ Help mode handler не інтегрувався")

    except Exception as e:
        issues.append(f"❌ Помилка тестування help mode: {e}")

    #3. Verification системи детекції режимів
    print("\n3. Перевірка системи детекції режимів...")

    try:
        #Тест поточної системи детекції
        current_keywords = [
            "проаналізуй", "analyze", "як ти використовуєш", "how do you use",
            "вдосконалення", "improvement", "покращення", "enhance",
            "проблематика", "problems", "міркування", "reasoning",
            "пам'ять", "memory", "як працює", "how does work",
            "архітектура", "architecture", "система", "system",
            "оптимізація", "optimization", "design", "structure",
        ]

        simple_keywords = ["read file", "list directory", "tree", "search for", "info about", "search functions"]

        print("📊 Поточна система детекції:")
        print(f"   • Складні ключові слова: {len(current_keywords)}")
        print(f"   • Прості ключові слова: {len(simple_keywords)}")

        #Тест конфліктів
        conflicting_queries = [
            "search for architecture patterns",  #може плутати
            "analyze file structure",  #може плутати
            "how does memory manager work?",  #складний аналіз
        ]

        print("\n⚠️  Потенційні конфлікти:")
        for query in conflicting_queries:
            has_simple = any(kw in query.lower() for kw in simple_keywords)
            has_complex = any(kw in query.lower() for kw in current_keywords)

            if has_simple and has_complex:
                print(f"   ⚠️  Конфлікт: '{query}'")
                issues.append(f"Конфліктний запит: '{query}'")
            else:
                print(f"   ✅ Чистий: '{query}'")

    except Exception as e:
        issues.append(f"❌ Помилка аналізу детекції: {e}")

    #Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК ТЕСТУВАННЯ ІНТЕГРАЦІЇ")
    print("=" * 60)

    if not issues:
        print("🎉 ВСЕ ПРАЦЮЄ ІДЕАЛЬНО!")
        print("✅ Плагін повністю інтегрований з Atlas")
        return True
    print(f"⚠️  ЗНАЙДЕНО {len(issues)} ПРОБЛЕМ:")
    for i, issue in enumerate(issues, 1):
        print(f"{i:2d}. {issue}")
    return False

def analyze_current_detection_system():
    """Аналіз поточної системи детекції режимів"""
    print("\n🔍 АНАЛІЗ ПОТОЧНОЇ СИСТЕМИ ДЕТЕКЦІЇ")
    print("=" * 60)

    #Читаємо поточну реалізацію
    try:

        #Тест системи детекції з файлу
        advanced_thinking_file = base_dir / "plugins" / "helper_sync_tell" / "advanced_thinking.py"
        content = advanced_thinking_file.read_text()

        #Витягуємо ключові слова з коду
        import re

        print("📋 Поточні ключові слова для advanced thinking:")

        #Знаходимо секцію з advanced_keywords
        adv_match = re.search(r"advanced_keywords\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if adv_match:
            keywords_text = adv_match.group(1)
            keywords = re.findall(r"'([^']+)'|\"([^\"]+)\"", keywords_text)
            keywords = [k[0] or k[1] for k in keywords]

            for kw in keywords:
                print(f"   • {kw}")

        print("\n📋 Прості команди (з main.py):")
        simple_commands = ["read file", "list directory", "tree", "search for", "info about", "search functions"]
        for cmd in simple_commands:
            print(f"   • {cmd}")

        #Аналіз проблем
        print("\n⚠️  ВИЯВЛЕНІ ПРОБЛЕМИ:")
        print("1. Ключові слова перетинаються:")
        print("   • 'search' є в обох системах")
        print("   • 'architecture' може конфліктувати з 'analyze'")
        print("   • 'memory' може конфліктувати з 'info about'")

        print("\n2. Недостатня точність детекції:")
        print("   • Базується тільки на ключових словах")
        print("   • Не враховує контекст та намір")
        print("   • Не має системи пріоритетів")

        return True

    except Exception as e:
        print(f"❌ Помилка аналізу: {e}")
        return False

if __name__ == "__main__":
    success = test_plugin_integration()
    analyze_current_detection_system()

    if success:
        print("\n✅ Інтеграція працює, але потребує покращення системи детекції")
    else:
        print("\n⚠️  Потребує виправлення інтеграції")
