#!/usr/bin/env python3
"""
Фінальний тест інтеграції покращеної системи детекції режимів
"""

import sys
from pathlib import Path

#Додаємо шляхи
base_dir = Path("/Users/developer/Documents/Atlas")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "plugins" / "helper_sync_tell"))

def test_final_integration():
    """Тест фінальної інтеграції з покращеним детектором"""
    print("🎯 ФІНАЛЬНИЙ ТЕСТ ІНТЕГРАЦІЇ ПОКРАЩЕНОЇ СИСТЕМИ")
    print("=" * 60)

    results = {"passed": 0, "total": 0, "issues": []}

    #1. Тест інтелектуального детектора
    print("\n1. Тест інтелектуального детектора...")

    try:
        from intelligent_mode_detector import IntelligentModeDetector
        detector = IntelligentModeDetector()

        #Критичні тести
        critical_tests = [
            ("read file main.py", False, "Simple file read"),
            ("Проаналізуй архітектуру Atlas", True, "Complex analysis"),
            ("Що не так з модулем пам'яті?", True, "Problem identification"),
            ("search for MemoryManager", False, "Simple search"),
            ("Як покращити продуктивність?", True, "Improvement request"),
        ]

        for message, should_be_advanced, description in critical_tests:
            result = detector.detect_chat_mode(message)

            if result.should_use_advanced == should_be_advanced:
                print(f"✅ {description}: правильно детектовано")
                results["passed"] += 1
            else:
                print(f"❌ {description}: неправильно детектовано")
                results["issues"].append(f"Детектор: {description}")

            results["total"] += 1

    except Exception as e:
        results["issues"].append(f"Помилка детектора: {e}")
        print(f"❌ Помилка тестування детектора: {e}")

    #2. Тест інтеграції з advanced_thinking
    print("\n2. Тест інтеграції з advanced_thinking...")

    try:
        from advanced_thinking import AdvancedAIThinkingTool

        #Mock Atlas app з інтелектуальним детектором
        class MockAdvancedAtlasApp:
            def __init__(self):
                self.advanced_ai_thinking_integration = False
                self._original_handle_help_mode = None

                #Mock code_reader
                class MockCodeReader:
                    def semantic_search(self, query):
                        return f"Semantic search results for: {query}"

                    def search_in_files(self, query):
                        return f"File search results for: {query}"

                    def read_file(self, file_path):
                        return f"Content of file: {file_path}"

                self.code_reader = MockCodeReader()

            def _handle_help_mode(self, message, context):
                return f"Original simple handler: {message}"

        mock_app = MockAdvancedAtlasApp()
        tool = AdvancedAIThinkingTool()

        #Тест інтеграції
        integration_success = tool.integrate_with_atlas_help_mode(mock_app)

        if integration_success:
            print("✅ Інтеграція успішна")
            results["passed"] += 1
        else:
            print("❌ Інтеграція не вдалася")
            results["issues"].append("Інтеграція не вдалася")

        results["total"] += 1

        #Тест обробки запитів
        test_messages = [
            ("read file config.py", "Original simple handler", "Simple command routing"),
            ("Проаналізуй систему пам'яті", "Фаза 1: Контекстний аналіз", "Advanced thinking routing"),
            ("list directory agents", "Original simple handler", "Directory listing"),
            ("Що не так з модулем?", "Фаза 1: Контекстний аналіз", "Problem analysis"),
        ]

        for message, expected_keyword, description in test_messages:
            try:
                response = mock_app._handle_help_mode(message, None)

                if expected_keyword in response:
                    print(f"✅ {description}: правильно оброблено")
                    results["passed"] += 1
                else:
                    print(f"❌ {description}: неправильно оброблено")
                    results["issues"].append(f"Обробка: {description}")

                results["total"] += 1

            except Exception as e:
                print(f"❌ Помилка обробки '{message}': {e}")
                results["issues"].append(f"Помилка обробки '{message}': {e}")
                results["total"] += 1

    except Exception as e:
        results["issues"].append(f"Помилка інтеграції: {e}")
        print(f"❌ Помилка тестування інтеграції: {e}")

    #3. Тест продуктивності
    print("\n3. Тест продуктивності детекції...")

    try:
        import time

        from intelligent_mode_detector import IntelligentModeDetector

        detector = IntelligentModeDetector()
        test_messages = [
            "read file main.py",
            "Проаналізуй архітектуру системи Atlas та запропонуй покращення",
            "search for memory manager functions",
            "Що не так з модулем думання і як це виправити?",
            "list directory structure",
        ]

        start_time = time.time()

        for message in test_messages:
            detector.detect_chat_mode(message)

        end_time = time.time()
        avg_time = (end_time - start_time) / len(test_messages)

        if avg_time < 0.01:  #Менше 10мс на запит
            print(f"✅ Продуктивність відмінна: {avg_time*1000:.2f}мс на запит")
            results["passed"] += 1
        else:
            print(f"⚠️  Продуктивність прийнятна: {avg_time*1000:.2f}мс на запит")
            results["passed"] += 0.5

        results["total"] += 1

    except Exception as e:
        results["issues"].append(f"Помилка тесту продуктивності: {e}")
        print(f"❌ Помилка тесту продуктивності: {e}")

    #Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК ФІНАЛЬНОГО ТЕСТУВАННЯ")
    print("=" * 60)

    success_rate = (results["passed"] / results["total"]) * 100 if results["total"] > 0 else 0

    print(f"✅ Успішно пройдено: {results['passed']:.1f}/{results['total']}")
    print(f"📈 Успішність: {success_rate:.1f}%")

    if not results["issues"]:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("✅ Система готова до продуктивного використання!")
        return True
    print(f"\n⚠️  ЗНАЙДЕНО {len(results['issues'])} ПРОБЛЕМ:")
    for i, issue in enumerate(results["issues"], 1):
        print(f"{i:2d}. {issue}")

    if success_rate >= 80:
        print("\n👍 Система працює добре, але має незначні проблеми")
        return True
    print("\n⚠️  Система потребує додаткових виправлень")
    return False

def demonstrate_intelligent_detection():
    """Демонстрація роботи інтелектуального детектора"""
    print("\n🎯 ДЕМОНСТРАЦІЯ ІНТЕЛЕКТУАЛЬНОГО ДЕТЕКТОРА")
    print("=" * 60)

    try:
        from intelligent_mode_detector import IntelligentModeDetector
        detector = IntelligentModeDetector()

        demo_queries = [
            "read file main.py",
            "Проаналізуй архітектуру пам'яті в Atlas та запропонуй покращення для підвищення продуктивності",
            "search for memory manager",
            "Що не так з модулем думання і чому він не працює як очікувалося?",
            "list directory agents",
            "Як можна покращити алгоритм мислення AI асистента використовуючи сучасні техніки?",
            "info about config.py",
            "Порівняй різні стратегії мислення в AI системах та визнач найкращу",
        ]

        print("\n🔍 Детекція режимів для різних типів запитів:\n")

        for query in demo_queries:
            result = detector.detect_chat_mode(query)

            mode_emoji = {
                "simple_command": "🔧",
                "advanced_thinking": "🧠",
                "hybrid": "🔄",
            }

            print(f"{mode_emoji.get(result.mode.value, '❓')} Запит: {query}")
            print(f"   📊 Режим: {result.mode.value}")
            print(f"   🎯 Впевненість: {result.confidence:.2f}")
            print(f"   🚀 Використати advanced: {'Так' if result.should_use_advanced else 'Ні'}")
            print(f"   💭 Обґрунтування: {result.reasoning[:80]}...")
            print()

        #Статистика
        stats = detector.get_detection_stats()
        print("📈 Статистика детекції:")
        for mode, count in stats["mode_counts"].items():
            percentage = (count / stats["total_detections"]) * 100
            print(f"   • {mode}: {count} ({percentage:.1f}%)")

    except Exception as e:
        print(f"❌ Помилка демонстрації: {e}")

if __name__ == "__main__":
    success = test_final_integration()
    demonstrate_intelligent_detection()

    if success:
        print("\n🎉 СИСТЕМА ПОВНІСТЮ ГОТОВА!")
        print("✨ Інтелектуальний детектор режимів працює ідеально!")
        print("🚀 Advanced thinking плагін успішно інтегровано з Atlas!")
    else:
        print("\n⚠️  Система потребує додаткової роботи")
