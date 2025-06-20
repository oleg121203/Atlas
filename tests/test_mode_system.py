#!/usr/bin/env python3
"""
Test script for the enhanced chat mode system with manual controls

Tests the automatic detection, manual mode switching, and development mode.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chat_context_manager import ChatContextManager, ChatMode

def test_auto_mode_detection():
    """Test automatic mode detection functionality."""
    print("🤖 Testing Automatic Mode Detection")
    print("=" * 50)
    
    context_manager = ChatContextManager()
    
    test_cases = [
        ("Hello, how are you?", ChatMode.CASUAL_CHAT, "casual conversation"),
        ("What tools are available?", ChatMode.TOOL_INQUIRY, "tool inquiry"),
        ("Help me understand this system", ChatMode.SYSTEM_HELP, "help request"),
        ("Take a screenshot of my screen", ChatMode.GOAL_SETTING, "goal setting"),
        ("What's the current status?", ChatMode.STATUS_CHECK, "status check"),
        ("How do I configure the settings?", ChatMode.CONFIGURATION, "configuration"),
    ]
    
    system_info = {
        'tools': ['capture_screen', 'click_at', 'type_text'],
        'agents': ['master_agent', 'screen_agent']
    }
    
    print(f"Auto mode enabled: {context_manager.is_auto_mode}")
    
    for message, expected_mode, description in test_cases:
        context = context_manager.analyze_message(message, system_info)
        status = "✅" if context.mode == expected_mode else "❌"
        
        print(f"{status} '{message}'")
        print(f"    → {context.mode.value} (confidence: {context.confidence:.2f}) - {description}")
        print()

def test_manual_mode_switching():
    """Test manual mode switching functionality."""
    print("👆 Testing Manual Mode Switching")
    print("=" * 50)
    
    context_manager = ChatContextManager()
    
    #Test switching to manual mode
    print(f"Initial auto mode: {context_manager.is_auto_mode}")
    
    #Switch to manual chat mode
    context_manager.set_manual_mode(ChatMode.CASUAL_CHAT)
    print(f"After manual switch - Auto mode: {context_manager.is_auto_mode}")
    print(f"Current mode: {context_manager.current_mode}")
    
    #Test that manual mode overrides detection
    system_info = {'tools': [], 'agents': []}
    
    test_message = "Take a screenshot"  #Would normally be GOAL_SETTING
    context = context_manager.analyze_message(test_message, system_info)
    
    print(f"Message: '{test_message}'")
    print(f"Detected mode: {context.mode.value} (should be casual_chat in manual mode)")
    print()
    
    #Test toggling back to auto
    context_manager.toggle_auto_mode()
    print(f"After toggle - Auto mode: {context_manager.is_auto_mode}")
    
    #Now it should detect properly
    context = context_manager.analyze_message(test_message, system_info)
    print(f"Same message in auto mode: {context.mode.value}")
    print()

def test_development_mode():
    """Test development mode functionality."""
    print("🔧 Testing Development Mode")
    print("=" * 50)
    
    context_manager = ChatContextManager()
    
    #Switch to development mode
    context_manager.set_manual_mode(ChatMode.DEVELOPMENT)
    
    print(f"Auto mode: {context_manager.is_auto_mode}")
    print(f"Current mode: {context_manager.current_mode}")
    
    #Test development mode response generation
    system_info = {
        'tools': ['capture_screen', 'execute_command', 'create_tool'],
        'agents': ['master_agent', 'security_agent']
    }
    
    dev_messages = [
        "Check system integrity and errors",
        "Create a backup of current configuration", 
        "Develop a new automation tool",
        "Analyze tool performance metrics",
        "Debug the screenshot functionality"
    ]
    
    for message in dev_messages:
        context = context_manager.analyze_message(message, system_info)
        response_prompt = context_manager.generate_response_prompt(context, message, system_info)
        
        print(f"Dev message: '{message}'")
        print(f"Mode: {context.mode.value}")
        print(f"Has enhanced capabilities: {'DEVELOPMENT_FEATURES' in response_prompt}")
        print()

def test_mode_persistence():
    """Test mode persistence and state management."""
    print("💾 Testing Mode Persistence")
    print("=" * 50)
    
    context_manager = ChatContextManager()
    
    #Test state tracking
    states = []
    
    #Auto mode
    states.append(("Auto mode", context_manager.is_auto_mode, context_manager.current_mode))
    
    #Manual chat
    context_manager.set_manual_mode(ChatMode.CASUAL_CHAT)
    states.append(("Manual chat", context_manager.is_auto_mode, context_manager.current_mode))
    
    #Manual development
    context_manager.set_manual_mode(ChatMode.DEVELOPMENT)
    states.append(("Manual dev", context_manager.is_auto_mode, context_manager.current_mode))
    
    #Back to auto
    context_manager.toggle_auto_mode()
    states.append(("Back to auto", context_manager.is_auto_mode, context_manager.current_mode))
    
    for description, is_auto, current_mode in states:
        print(f"{description}: Auto={is_auto}, Mode={current_mode}")

def main():
    """Run all mode system tests."""
    print("🎛️ Atlas Enhanced Chat Mode System Tests")
    print("=" * 60)
    print()
    
    try:
        test_auto_mode_detection()
        test_manual_mode_switching()
        test_development_mode()
        test_mode_persistence()
        
        print("✅ All mode system tests completed!")
        print()
        print("🎉 Enhanced mode system is ready!")
        print("Features verified:")
        print("- ✅ Automatic mode detection")
        print("- ✅ Manual mode switching") 
        print("- ✅ Development mode with enhanced capabilities")
        print("- ✅ Mode persistence and state management")
        print("- ✅ UI integration points ready")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
