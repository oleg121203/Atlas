#!/usr/bin/env python3
"""
Діагностика модуля думання та аналізу Atlas
Виявляє проблеми в advanced_thinking.py та пов'язаних компонентах
"""

import importlib.util
import sys
import traceback
from pathlib import Path


def diagnose_thinking_module():
    """Основна функція діагностики модуля думання"""
    print("🧠 ДІАГНОСТИКА МОДУЛЯ ДУМАННЯ ATLAS")
    print("=" * 50)

    issues_found = []

    # 1. Verification існування файлів
    print("\n1. Перевірка структури файлів...")

    base_dir = Path("/Users/developer/Documents/Atlas")
    thinking_file = base_dir / "plugins" / "helper_sync_tell" / "advanced_thinking.py"
    hybrid_file = base_dir / "plugins" / "helper_sync_tell" / "hybrid_integration.py"

    if not thinking_file.exists():
        issues_found.append("❌ Файл advanced_thinking.py не знайдено")
    else:
        print("✅ advanced_thinking.py знайдено")

    if not hybrid_file.exists():
        issues_found.append("❌ Файл hybrid_integration.py не знайдено")
    else:
        print("✅ hybrid_integration.py знайдено")

    # 2. Verification імпортів
    print("\n2. Перевірка залежностей та імпортів...")

    # Додаємо шляхи для імпорту
    sys.path.insert(0, str(base_dir))
    sys.path.insert(0, str(base_dir / "plugins" / "helper_sync_tell"))

    try:
        # Verification platform_utils
        from utils.platform_utils import IS_HEADLESS, IS_LINUX, IS_MACOS

        print("✅ platform_utils доступні")
    except ImportError as e:
        issues_found.append(f"⚠️  platform_utils недоступні: {e}")

    try:
        # Verification memory_manager
        from modules.agents.enhanced_memory_manager import MemoryScope, MemoryType

        print("✅ enhanced_memory_manager доступний")
    except ImportError as e:
        issues_found.append(f"⚠️  enhanced_memory_manager недоступний: {e}")

    # 3. Verification основного модуля
    print("\n3. Перевірка advanced_thinking модуля...")

    try:
        spec = importlib.util.spec_from_file_location(
            "advanced_thinking", thinking_file
        )
        advanced_thinking = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(advanced_thinking)
        print("✅ advanced_thinking модуль успішно завантажено")

        # Verification класів
        if hasattr(advanced_thinking, "AdvancedAIThinkingTool"):
            print("✅ AdvancedAIThinkingTool клас знайдено")
        else:
            issues_found.append("❌ AdvancedAIThinkingTool клас не знайдено")

        if hasattr(advanced_thinking, "ThinkingStrategy"):
            print("✅ ThinkingStrategy enum знайдено")
        else:
            issues_found.append("❌ ThinkingStrategy enum не знайдено")

        if hasattr(advanced_thinking, "register"):
            print("✅ register функція знайдена")
        else:
            issues_found.append("❌ register функція не знайдена")

    except Exception as e:
        issues_found.append(f"❌ Помилка завантаження advanced_thinking: {e}")
        traceback.print_exc()

    # 4. Verification функціональності
    print("\n4. Перевірка функціональності...")

    try:
        tool = advanced_thinking.AdvancedAIThinkingTool()
        print("✅ AdvancedAIThinkingTool може бути створений")

        # Verification методів
        required_methods = [
            "analyze_query_context",
            "select_thinking_strategy",
            "generate_strategic_questions",
            "analyze_with_meta_cognition",
            "synthesize_with_refinement",
            "process_with_advanced_thinking",
        ]

        for method in required_methods:
            if hasattr(tool, method):
                print(f"✅ Метод {method} існує")
            else:
                issues_found.append(f"❌ Метод {method} відсутній")

        # Тест простого запиту
        try:
            tool.process_with_advanced_thinking("Тест запиту")
            print("✅ Простий запит оброблено успішно")
        except Exception as e:
            issues_found.append(f"⚠️  Помилка обробки запиту: {e}")

    except Exception as e:
        issues_found.append(f"❌ Помилка створення інструменту: {e}")

    # 5. Verification інтеграції
    print("\n5. Перевірка інтеграції...")

    try:
        register_result = advanced_thinking.register()
        if register_result and "tools" in register_result:
            print("✅ Функція register працює")
        else:
            issues_found.append("⚠️  register повертає неочікуваний результат")
    except Exception as e:
        issues_found.append(f"❌ Помилка реєстрації: {e}")

    # 6. Аналіз конфігурації
    print("\n6. Аналіз конфігурації...")

    try:
        tool = advanced_thinking.AdvancedAIThinkingTool()
        config = tool.config
        print(f"✅ Конфігурація завантажена: {len(config)} параметрів")

        # Verification ключових параметрів
        key_params = ["max_sub_questions", "confidence_threshold", "thinking_timeout"]
        for param in key_params:
            if param in config:
                print(f"✅ Параметр {param}: {config[param]}")
            else:
                issues_found.append(f"⚠️  Відсутній параметр: {param}")

    except Exception as e:
        issues_found.append(f"❌ Помилка аналізу конфігурації: {e}")

    # Підсумок
    print("\n" + "=" * 50)
    print("📊 ПІДСУМОК ДІАГНОСТИКИ")
    print("=" * 50)

    if not issues_found:
        print("🎉 УСПІХ! Модуль думання працює правильно!")
        return True
    print(f"⚠️  ЗНАЙДЕНО {len(issues_found)} ПРОБЛЕМ:")
    for i, issue in enumerate(issues_found, 1):
        print(f"{i:2d}. {issue}")

    # Рекомендації
    print("\n🔧 РЕКОМЕНДАЦІЇ:")
    if any("platform_utils" in issue for issue in issues_found):
        print("• Перевірте наявність utils/platform_utils.py")
    if any("memory_manager" in issue for issue in issues_found):
        print("• Перевірте наявність agents/enhanced_memory_manager.py")
    if any("завантаження" in issue for issue in issues_found):
        print("• Перевірте синтаксис та імпорти в advanced_thinking.py")
    if any("метод" in issue for issue in issues_found):
        print("• Доповніть відсутні методи в AdvancedAIThinkingTool")

    return False


def analyze_algorithm_structure():
    """Аналіз структури алгоритму"""
    print("\n🔍 АНАЛІЗ СТРУКТУРИ АЛГОРИТМУ")
    print("=" * 50)

    try:
        thinking_file = Path(
            "/Users/developer/Documents/Atlas/plugins/helper_sync_tell/advanced_thinking.py"
        )
        content = thinking_file.read_text()

        # Аналіз структури
        print("\n📋 Структурний аналіз:")

        classes = content.count("class ")
        functions = content.count("def ")
        strategies = content.count("ThinkingStrategy.")
        phases = content.count("Phase")

        print(f"• Класів: {classes}")
        print(f"• Функцій/методів: {functions}")
        print(f"• Стратегій мислення: {strategies}")
        print(f"• Фаз обробки: {phases}")

        # Аналіз фаз алгоритму
        print("\n🔄 Фази алгоритму:")
        if "Phase 1" in content:
            print("✅ Фаза 1: Контекстний аналіз")
        if "Phase 2" in content:
            print("✅ Фаза 2: Генерація стратегічних питань")
        if "Phase 3" in content:
            print("✅ Фаза 3: Мета-когнітивний аналіз")
        if "Phase 4" in content:
            print("✅ Фаза 4: Синтез з удосконаленням")
        if "Phase 5" in content:
            print("✅ Фаза 5: Мета-статистика")

        # Аналіз стратегій
        print("\n🎯 Стратегії мислення:")
        strategies_found = []
        if "ANALYTICAL" in content:
            strategies_found.append("Аналітична")
        if "EXPLORATORY" in content:
            strategies_found.append("Дослідницька")
        if "ARCHITECTURAL" in content:
            strategies_found.append("Архітектурна")
        if "TROUBLESHOOTING" in content:
            strategies_found.append("Усунення проблем")
        if "CREATIVE" in content:
            strategies_found.append("Творча")
        if "CONTEXTUAL" in content:
            strategies_found.append("Контекстна")

        for strategy in strategies_found:
            print(f"✅ {strategy}")

        return True

    except Exception as e:
        print(f"❌ Помилка аналізу структури: {e}")
        return False


if __name__ == "__main__":
    success = diagnose_thinking_module()
    analyze_algorithm_structure()

    if success:
        print("\n🎯 Модуль думання готовий до використання!")
        exit(0)
    else:
        print("\n⚠️  Потребує виправлення перед використанням.")
        exit(1)
