#!/usr/bin/env python3
"""
Тест якості роботи модуля advanced thinking
Перевіряє реальну ефективність алгоритму мислення
"""

import sys
from pathlib import Path

from advanced_thinking import AdvancedAIThinkingTool, ThinkingStrategy

#Додаємо шляхи
base_dir = Path("/Users/developer/Documents/Atlas")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "plugins" / "helper_sync_tell"))

def test_thinking_quality():
    """Тестування якості мислення"""
    print("🧠 ТЕСТ ЯКОСТІ АЛГОРИТМУ ДУМАННЯ")
    print("=" * 50)

    #Creation інструменту
    tool = AdvancedAIThinkingTool()

    #Тестові запити різних типів
    test_queries = [
        {
            "query": "Проаналізуй архітектуру пам'яті в Atlas та запропонуй покращення",
            "expected_strategy": ThinkingStrategy.ARCHITECTURAL,
            "category": "Архітектурний аналіз",
        },
        {
            "query": "Що не так з модулем думання чи аналізу?",
            "expected_strategy": ThinkingStrategy.TROUBLESHOOTING,
            "category": "Усунення проблем",
        },
        {
            "query": "Як можна покращити алгоритм мислення AI асистента?",
            "expected_strategy": ThinkingStrategy.CREATIVE,
            "category": "Творче покращення",
        },
        {
            "query": "Порівняй різні стратегії мислення в AI системах",
            "expected_strategy": ThinkingStrategy.COMPARATIVE,
            "category": "Порівняльний аналіз",
        },
    ]

    results = []

    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Тест: {test['category']}")
        print(f"Запит: {test['query']}")
        print("-" * 40)

        try:
            #Фаза 1: Аналіз контексту
            context = tool.analyze_query_context(test["query"])
            print(f"📊 Контекст: домен={context.domain}, складність={context.complexity_level}/5")

            #Фаза 2: Вибір стратегії
            strategy = tool.select_thinking_strategy(test["query"], context)
            strategy_correct = strategy == test["expected_strategy"]
            print(f"🎯 Стратегія: {strategy.value} {'✅' if strategy_correct else '❌'}")

            #Фаза 3: Generation питань
            questions = tool.generate_strategic_questions(test["query"], strategy, context)
            print(f"❓ Питань згенеровано: {len(questions)}")

            if questions:
                print("📋 Стратегічні питання:")
                for j, q in enumerate(questions[:3], 1):  #Показуємо перші 3
                    print(f"   {j}. {q}")
                if len(questions) > 3:
                    print(f"   ... та ще {len(questions) - 3} питань")

            #Оцінка якості
            quality_score = 0

            #Оцінка стратегії
            if strategy_correct:
                quality_score += 25

            #Оцінка кількості питань
            if 3 <= len(questions) <= 7:
                quality_score += 25

            #Оцінка контексту
            if context.complexity_level > 1:
                quality_score += 25

            #Оцінка специфічності питань
            if questions and all(len(q) > 20 for q in questions):
                quality_score += 25

            print(f"📈 Оцінка якості: {quality_score}%")

            results.append({
                "category": test["category"],
                "strategy_correct": strategy_correct,
                "questions_count": len(questions),
                "quality_score": quality_score,
                "context": context,
            })

        except Exception as e:
            print(f"❌ Помилка: {e}")
            results.append({
                "category": test["category"],
                "error": str(e),
                "quality_score": 0,
            })

    #Підсумок результатів
    print("\n" + "=" * 50)
    print("📊 ПІДСУМОК ТЕСТУВАННЯ ЯКОСТІ")
    print("=" * 50)

    total_score = 0
    successful_tests = 0

    for result in results:
        if "error" not in result:
            successful_tests += 1
            total_score += result["quality_score"]
            strategy_status = "✅" if result["strategy_correct"] else "❌"
            print(f"• {result['category']}: {result['quality_score']}% {strategy_status}")
        else:
            print(f"• {result['category']}: ПОМИЛКА - {result['error']}")

    if successful_tests > 0:
        average_score = total_score / successful_tests
        print(f"\n🎯 Середня оцінка: {average_score:.1f}%")

        if average_score >= 80:
            print("🎉 ВІДМІННО! Алгоритм працює на високому рівні")
        elif average_score >= 60:
            print("✅ ДОБРЕ! Алгоритм працює задовільно")
        else:
            print("⚠️  ПОТРЕБУЄ ПОКРАЩЕННЯ")

        return average_score >= 60
    print("❌ ВСІ ТЕСТИ ПРОВАЛИЛИСЬ")
    return False

def test_meta_cognition():
    """Тест мета-когнітивних здібностей"""
    print("\n🧠 ТЕСТ МЕТА-КОГНІТИВНИХ ЗДІБНОСТЕЙ")
    print("=" * 50)

    tool = AdvancedAIThinkingTool()

    #Тест складного запиту
    complex_query = "Як система мета-когнітивного аналізу в Atlas може самовдосконалюватися?"

    try:
        context = tool.analyze_query_context(complex_query)

        #Мета-когнітивний аналіз
        analysis, confidence, uncertainties = tool.analyze_with_meta_cognition(
            complex_query, {}, context,
        )

        print(f"📝 Аналіз виконано: {len(analysis)} символів")
        print(f"🎯 Рівень впевненості: {confidence:.2f}")
        print(f"❓ Невизначеностей знайдено: {len(uncertainties)}")

        if uncertainties:
            print("🔍 Ключові невизначеності:")
            for unc in uncertainties[:3]:
                print(f"   • {unc}")

        #Оцінка мета-когнітивності
        meta_score = 0

        if 0.1 <= confidence <= 0.9:  #Реалістична оцінка
            meta_score += 30

        if uncertainties:  #Виявлення невизначеностей
            meta_score += 40

        if len(analysis) > 100:  #Детальний аналіз
            meta_score += 30

        print(f"📊 Мета-когнітивна оцінка: {meta_score}%")

        return meta_score >= 70

    except Exception as e:
        print(f"❌ Помилка мета-когнітивного тесту: {e}")
        return False

def performance_test():
    """Тест продуктивності"""
    print("\n⚡ ТЕСТ ПРОДУКТИВНОСТІ")
    print("=" * 50)

    import time

    tool = AdvancedAIThinkingTool()
    query = "Швидкий тест продуктивності алгоритму"

    start_time = time.time()

    try:
        #Базові операції
        context = tool.analyze_query_context(query)
        strategy = tool.select_thinking_strategy(query, context)
        questions = tool.generate_strategic_questions(query, strategy, context)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"⏱️  Час обробки: {processing_time:.3f} сек")
        print(f"🔧 Стратегія: {strategy.value}")
        print(f"❓ Питань: {len(questions)}")

        #Оцінка швидкості
        if processing_time < 1.0:
            print("🚀 ШВИДКО! Обробка за < 1 сек")
            return True
        if processing_time < 3.0:
            print("✅ НОРМАЛЬНО! Обробка за < 3 сек")
            return True
        print("⚠️  ПОВІЛЬНО! Обробка > 3 сек")
        return False

    except Exception as e:
        print(f"❌ Помилка тесту продуктивності: {e}")
        return False

if __name__ == "__main__":
    #Запуск всіх тестів
    quality_ok = test_thinking_quality()
    meta_ok = test_meta_cognition()
    perf_ok = performance_test()

    print("\n" + "=" * 50)
    print("🏆 ЗАГАЛЬНИЙ РЕЗУЛЬТАТ")
    print("=" * 50)

    passed = sum([quality_ok, meta_ok, perf_ok])
    total = 3

    print(f"✅ Пройдено тестів: {passed}/{total}")

    if passed == total:
        print("🎉 МОДУЛЬ ДУМАННЯ ПРАЦЮЄ ІДЕАЛЬНО!")
    elif passed >= 2:
        print("👍 МОДУЛЬ ДУМАННЯ ПРАЦЮЄ ДОБРЕ!")
    else:
        print("⚠️  МОДУЛЬ ДУМАННЯ ПОТРЕБУЄ ПОКРАЩЕННЯ!")

    print("\n📋 Детальна оцінка:")
    print(f"   • Якість алгоритму: {'✅' if quality_ok else '❌'}")
    print(f"   • Мета-когнітивність: {'✅' if meta_ok else '❌'}")
    print(f"   • Продуктивність: {'✅' if perf_ok else '❌'}")
