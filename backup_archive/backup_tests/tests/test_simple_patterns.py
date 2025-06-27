#!/usr/bin/env python3
"""
Simple test for chat context patterns without dependencies
"""

from enum import Enum


class ChatMode(Enum):
    """Different modes of conversation with Atlas."""

    CASUAL_CHAT = "casual_chat"
    SYSTEM_HELP = "system_help"
    GOAL_SETTING = "goal_setting"
    TOOL_INQUIRY = "tool_inquiry"
    STATUS_CHECK = "status_check"
    CONFIGURATION = "configuration"
    DEVELOPMENT = "development"


def test_pattern_detection():
    """Test our improved pattern detection logic."""
    print("🧪 Testing pattern detection logic...\n")

    # Define the same patterns as in our improved code
    mode_patterns = {
        ChatMode.CASUAL_CHAT: {
            "keywords": [
                "hello",
                "hi",
                "hey",
                "привіт",
                "привет",
                "як справи",
                "як тебе звати",
            ],
        },
        ChatMode.SYSTEM_HELP: {
            "keywords": [
                "пам'ять",
                "память",
                "memory",
                "забезпечена",
                "довгострокова",
                "розмежуванням",
                "напрямку",
                "чату",
                "цікавить",
                "мене цікавить",
            ],
        },
    }

    test_cases = [
        ("Привіт друже, як тебе звати?", ChatMode.CASUAL_CHAT),
        (
            "Мене цікавить чи забезпечена в тебе пам'ять довгострокова і з розмежуванням по напрямку чату?",
            ChatMode.SYSTEM_HELP,
        ),
        ("Hi there!", ChatMode.CASUAL_CHAT),
    ]

    for message, expected_mode in test_cases:
        message_lower = message.lower()
        scores = {}

        # Analyze each mode
        for mode, patterns in mode_patterns.items():
            score = 0.0
            keyword_matches = 0

            for keyword in patterns["keywords"]:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    if f" {keyword.lower()} " in f" {message_lower} ":
                        score += 0.1

            if keyword_matches > 0:
                score += (keyword_matches / len(patterns["keywords"])) * 0.6

            scores[mode] = score

        best_mode = (
            max(scores.keys(), key=lambda k: scores[k])
            if scores
            else ChatMode.CASUAL_CHAT
        )
        confidence = scores.get(best_mode, 0.0)

        # Apply memory boost
        memory_indicators = [
            "пам'ять",
            "память",
            "memory",
            "забезпечена",
            "довгострокова",
            "розмежуванням",
            "цікавить",
        ]
        if (
            any(indicator in message_lower for indicator in memory_indicators)
            and best_mode == ChatMode.SYSTEM_HELP
        ):
            confidence = min(0.9, confidence + 0.3)

        status = "✅" if best_mode == expected_mode else "❌"
        print(f"{status} '{message}'")
        print(f"   Expected: {expected_mode.value}")
        print(f"   Got: {best_mode.value} (confidence: {confidence:.2f})")
        print(
            f"   Scores: {[(mode.value, f'{score:.2f}') for mode, score in scores.items()]}"
        )
        print()


def test_memory_response_logic():
    """Test memory response detection logic."""
    print("🧪 Testing memory response logic...\n")

    message = "Мене цікавить чи забезпечена в тебе пам'ять довгострокова?"
    message_lower = message.lower()

    memory_keywords = [
        "пам'ять",
        "память",
        "memory",
        "remember",
        "memorize",
        "store",
        "recall",
        "забезпечена",
        "довгострокова",
        "розмежуванням",
        "напрямку",
        "чату",
    ]

    detected = any(word in message_lower for word in memory_keywords)
    print(f"Memory keywords detected: {detected}")
    print(
        f"Detected keywords: {[word for word in memory_keywords if word in message_lower]}"
    )

    if detected:
        print("✅ Would generate direct memory response")
    else:
        print("❌ Would not generate memory response")


if __name__ == "__main__":
    test_pattern_detection()
    test_memory_response_logic()
    print("✨ Testing completed!")
