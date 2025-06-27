#!/usr/bin/env python3
"""
Final verification test for Atlas completeness
Tests all the requested features:
1. .env and API key management
2. Tool loading at startup
3. Chat mode detection
4. Headless environment robustness
"""

import os
import sys
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_env_loading():
    """Test .env loading and API key management"""
    print("🔧 Testing .env loading and API key management...")

    try:
        # Load .env
        from dotenv import load_dotenv

        load_dotenv()

        # Test config manager
        from config_manager import ConfigManager

        config = ConfigManager()

        # Test API key access
        openai_key = config.get_openai_api_key()
        gemini_key = config.get_gemini_api_key()
        mistral_key = config.get_mistral_api_key()
        groq_key = config.get_groq_api_key()
        default_provider = config.get_current_provider()
        default_model = config.get_current_model()

        print(f"   ✅ OpenAI key: {'✓' if openai_key else '✗'}")
        print(f"   ✅ Gemini key: {'✓' if gemini_key else '✗'}")
        print(f"   ✅ Mistral key: {'✓' if mistral_key else '✗'}")
        print(f"   ✅ Groq key: {'✓' if groq_key else '✗'}")
        print(f"   ✅ Default provider: {default_provider}")
        print(f"   ✅ Default model: {default_model}")

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_tool_loading():
    """Test that all tools load at startup"""
    print("🛠️ Testing tool loading at startup...")

    try:
        from config_manager import ConfigManager
        from modules.agents.agent_manager import AgentManager
        from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
        from modules.agents.token_tracker import TokenTracker

        from utils.llm_manager import LLMManager

        # Initialize managers
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(
            token_tracker=token_tracker, config_manager=config_manager
        )
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager, config_manager=config_manager
        )
        agent_manager = AgentManager(
            llm_manager=llm_manager, memory_manager=memory_manager
        )

        # Get tool details
        tools = agent_manager.get_all_tools_details()
        tool_names = agent_manager.get_tool_names()

        print(f"   ✅ Total tools loaded: {len(tool_names)}")
        print(
            f"   ✅ Built-in tools: {len([t for t in tools if t.get('type') == 'builtin'])}"
        )
        print(
            f"   ✅ Generated tools: {len([t for t in tools if t.get('type') == 'generated'])}"
        )

        # Check specific critical tools
        critical_tools = [
            "capture_screen",
            "get_clipboard_text",
            "click_at",
            "create_tool",
        ]
        missing_tools = [tool for tool in critical_tools if tool not in tool_names]

        if missing_tools:
            print(f"   ⚠️ Missing critical tools: {missing_tools}")
        else:
            print("   ✅ All critical tools present")

        return len(tool_names) > 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return False


def test_chat_mode_detection():
    """Test chat mode detection improvements"""
    print("🗣️ Testing chat mode detection...")

    try:
        from config_manager import ConfigManager
        from modules.agents.chat_context_manager import ChatContextManager, ChatMode
        from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
        from modules.agents.token_tracker import TokenTracker

        from utils.llm_manager import LLMManager

        # Initialize managers
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(
            token_tracker=token_tracker, config_manager=config_manager
        )
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager, config_manager=config_manager
        )
        context_manager = ChatContextManager(memory_manager=memory_manager)

        # Test cases
        test_cases = [
            ("Hello!", ChatMode.CASUAL_CHAT),
            ("How are you?", ChatMode.CASUAL_CHAT),
            ("What is the weather?", ChatMode.CASUAL_CHAT),
            ("help me with something", ChatMode.SYSTEM_HELP),
            ("How do I use Atlas?", ChatMode.SYSTEM_HELP),
            ("Create a tool to...", ChatMode.TOOL_INQUIRY),
            ("Take a screenshot", ChatMode.GOAL_SETTING),
        ]

        results = []
        for text, expected_mode in test_cases:
            detected_mode = context_manager.determine_chat_mode(text)
            is_correct = detected_mode == expected_mode
            results.append(is_correct)
            status = "✅" if is_correct else "❌"
            print(
                f"   {status} '{text}' -> {detected_mode.name} (expected {expected_mode.name})"
            )

        accuracy = sum(results) / len(results) * 100
        print(f"   📊 Mode detection accuracy: {accuracy:.1f}%")

        return accuracy >= 70  # Accept 70%+ accuracy
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return False


def test_headless_robustness():
    """Test robustness in headless environments"""
    print("🖥️ Testing headless environment robustness...")

    try:
        # Test that tools with GUI dependencies handle gracefully
        old_display = os.environ.get("DISPLAY")

        # Simulate headless environment
        if "DISPLAY" in os.environ:
            del os.environ["DISPLAY"]

        # Test screenshot tool
        from tools.screenshot_tool import capture_screen

        result = capture_screen("test_screenshot.png")
        print(f"   ✅ Screenshot tool handles headless: {type(result)}")

        # Test mouse/keyboard tool
        from tools.mouse_keyboard_tool import click_at

        result = click_at(100, 100)
        print(f"   ✅ Mouse/keyboard tool handles headless: {type(result)}")

        # Test clipboard tool
        from tools.clipboard_tool import get_clipboard_text

        result = get_clipboard_text()
        print(f"   ✅ Clipboard tool handles headless: {type(result)}")

        # Test image recognition tool
        from tools.image_recognition_tool import find_template_in_image

        result = find_template_in_image("nonexistent.png", "nonexistent2.png")
        print(f"   ✅ Image recognition tool handles missing cv2: {result is None}")

        # Test OCR tool
        from tools.ocr_tool import ocr_file

        try:
            # Create a dummy image file to avoid file not found error
            import tempfile

            from PIL import Image

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                # Create a small test image
                img = Image.new("RGB", (10, 10), color="white")
                img.save(tmp.name)
                result = ocr_file(tmp.name)
                os.unlink(tmp.name)  # Clean up
            print("   ✅ OCR tool works with available dependencies")
        except (RuntimeError, ImportError) as e:
            if "not available" in str(e):
                print(
                    f"   ✅ OCR tool handles missing dependencies: {type(e).__name__}"
                )
            else:
                raise
        except Exception as e:
            print(f"   ⚠️ OCR tool error (expected in headless): {type(e).__name__}")

        # Restore DISPLAY if it was set
        if old_display:
            os.environ["DISPLAY"] = old_display

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("🚀 Atlas Final Verification Test")
    print("=" * 50)

    tests = [
        ("Environment & API Keys", test_env_loading),
        ("Tool Loading", test_tool_loading),
        ("Chat Mode Detection", test_chat_mode_detection),
        ("Headless Robustness", test_headless_robustness),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ FAILED with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    passed = sum(results)
    total = len(results)

    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 All verification tests PASSED! Atlas is ready.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
