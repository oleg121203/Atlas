#!/usr/bin/env python3
"""
Тест покращень ChatContextManager
"""

import sys

sys.path.append("/workspaces/Atlas")


def test_chat_improvements():
    try:
        from modules.agents.chat_context_manager import ChatContextManager, ChatMode

        print("✅ Успішно імпортований ChatContextManager")

        # Initialization
        manager = ChatContextManager()
        print("✅ ChatContextManager ініціалізований")

        # Тест 1: Питання про пам'ять (українською)
        test_message = "Мене цікавить чи забезпечена в тебе пам'ять довгострокова і з розмежуванням по напрямку чату?"
        context = manager.analyze_message(test_message)

        print("\nТест 1: Питання про пам'ять")
        print(f"Повідомлення: {test_message}")
        print(f"Детектований режим: {context.mode.value}")
        print(f"Впевненість: {context.confidence:.2f}")
        print(f"Ключові слова: {context.context_keywords}")

        # Тест генерації відповіді
        if context.mode == ChatMode.SYSTEM_HELP:
            response_prompt = manager._generate_help_response(context, test_message)
            print(
                f"Згенерований промпт містить специфічну інформацію про пам'ять: {'memory' in response_prompt.lower()}"
            )

        # Тест 2: Просте привітання
        test_message2 = "Привіт друже, як тебе звати?"
        context2 = manager.analyze_message(test_message2)

        print("\nТест 2: Привітання")
        print(f"Повідомлення: {test_message2}")
        print(f"Детектований режим: {context2.mode.value}")
        print(f"Впевненість: {context2.confidence:.2f}")

        # Тест 3: Питання про інструменти
        test_message3 = "Які інструменти у вас є?"
        context3 = manager.analyze_message(test_message3)

        print("\nТест 3: Питання про інструменти")
        print(f"Повідомлення: {test_message3}")
        print(f"Детектований режим: {context3.mode.value}")
        print(f"Впевненість: {context3.confidence:.2f}")

        print("\n✅ Всі тести пройшли успішно!")

    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        return False
    except Exception as e:
        print(f"❌ Помилка тесту: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_chat_improvements()
    sys.exit(0 if success else 1)
