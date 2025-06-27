#!/usr/bin/env python3
"""
Test script for mode detection issues
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.chat_context_manager import ChatContextManager, ChatMode


def test_messages():
    """Test specific problematic messages."""
    manager = ChatContextManager()

    test_cases = [
        "в яких режимах можеш працювати?",
        "какие у тебя режимы работы?",
        "what modes do you have?",
        "як працює Atlas?",
        "як працює атлас?",
        "що ти вмієш робити?",
        "что ты умеешь делать?",
        "help me understand Atlas",
        "explain Atlas features",
        "как работает система",
        "як працює система",
        "режимы Atlas",
        "режими Атлас",
        "Atlas modes",
        "можеш працювати в різних режимах?",
        "можешь работать в разных режимах?",
        "can you work in different modes?",
        "what is Atlas",
        "що таке Atlas",
        "что такое Atlas",
    ]

    print("=== Mode Detection Test ===\n")

    for i, message in enumerate(test_cases, 1):
        context = manager.analyze_message(message)
        mode_icon = {
            ChatMode.CASUAL_CHAT: "💬",
            ChatMode.SYSTEM_HELP: "❓",
            ChatMode.GOAL_SETTING: "🎯",
            ChatMode.TOOL_INQUIRY: "🔧",
            ChatMode.STATUS_CHECK: "📊",
            ChatMode.CONFIGURATION: "⚙️",
        }

        icon = mode_icon.get(context.mode, "❓")
        expected = (
            "❓ SYSTEM_HELP"
            if any(
                word in message.lower()
                for word in [
                    "режим",
                    "modes",
                    "atlas",
                    "атлас",
                    "что ты",
                    "що ти",
                    "what is",
                    "help",
                    "explain",
                    "як працює",
                    "как работает",
                ]
            )
            else "Other"
        )

        status = "✅" if context.mode == ChatMode.SYSTEM_HELP else "❌"

        print(f'{i:2d}. {status} "{message}"')
        print(
            f"     Detected: {icon} {context.mode.value.upper()} (confidence: {context.confidence:.2f})"
        )
        if context.context_keywords:
            print(f"     Keywords found: {', '.join(context.context_keywords)}")
        print(f"     Expected: {expected}")
        print()


if __name__ == "__main__":
    test_messages()
