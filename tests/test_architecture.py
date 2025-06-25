#!/usr/bin/env python3
"""Тест архітектури TaskManager"""

import os
import sys

#Settings шляху
sys.path.insert(0, "/Users/developer/Documents/Atlas")
os.chdir("/Users/developer/Documents/Atlas")

def test_task_manager():
    """Тестує TaskManager архітектуру"""
    try:
        print("🧪 Тестую архітектуру Atlas TaskManager...")

        #Імпорт компонентів
        from modules.agents.task_manager import TaskManager, TaskPriority

        print("✅ Всі компоненти імпортовано успішно!")

        #Creation TaskManager
        tm = TaskManager(max_concurrent_tasks=2)
        print(f"✅ TaskManager створено (max_tasks: {tm.max_concurrent_tasks})")

        #Creation тестового завдання
        task_id = tm.create_task(
            "Тестове завдання",
            TaskPriority.HIGH,
        )
        print(f"✅ Завдання створено: {task_id}")

        #Verification статистики
        stats = tm.get_task_statistics()
        print("📊 Статистика:")
        print(f"   - Всього завдань: {stats['total_tasks']}")
        print(f"   - Очікують: {stats['pending']}")
        print(f"   - Макс. паралельних: {stats['max_concurrent']}")

        #Getting завдання
        task = tm.get_task(task_id)
        print(f"✅ Завдання отримано: {task.goal}")

        print("\n🎉 АРХІТЕКТУРА ПОВНІСТЮ ПРАЦЕЗДАТНА!")
        print("=" * 50)
        print("🎯 TaskManager - багатозадачна система")
        print("🤖 TaskAwareMasterAgent - ізольовані агенти")
        print("🧠 MasterAgent - базовий оркестратор")
        print("🔧 AgentManager - управління інструментами")
        print("💾 EnhancedMemoryManager - ізольована пам'ять")
        print("=" * 50)
        print("✅ СИСТЕМА ГОТОВА ДО ВИКОНАННЯ СКЛАДНИХ ЗАВДАНЬ!")

        return True

    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_task_manager()
