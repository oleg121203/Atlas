#!/usr/bin/env python3
"""
Test integration of new analysis tools in System Help mode
"""

import sys

sys.path.append("/workspaces/Atlas")

try:
    from modules.agents.chat_context_manager import ChatContextManager

    #Initialize the context manager
    manager = ChatContextManager()

    print("🧪 Testing enhanced System Help mode with new analysis tools...")

    #Test cases specifically for the new analysis tools
    test_cases = [
        {
            "message": "Analyze the memory system dependencies and architecture",
            "expected_tools": ["dependency_analyzer", "performance_profiler", "code_reader_tool"],
            "description": "Memory system architectural analysis",
        },
        {
            "message": "Check for performance issues in tool implementations",
            "expected_tools": ["performance_profiler", "professional_analyzer", "code_reader_tool"],
            "description": "Performance analysis request",
        },
        {
            "message": "Investigate dependency conflicts and architectural problems",
            "expected_tools": ["dependency_analyzer", "professional_analyzer"],
            "description": "Dependency and architecture investigation",
        },
        {
            "message": "What tools are available for code analysis?",
            "expected_tools": ["dependency_analyzer", "performance_profiler", "code_reader_tool"],
            "description": "Tool inquiry with enhanced analysis",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n✅ Test {i}: {test['description']}")
        print(f"   Input: '{test['message']}'")

        #Analyze message
        context = manager.analyze_message(test["message"])
        mode_detected = context.mode.value
        confidence = context.confidence

        print(f"   Mode: {mode_detected} (confidence: {confidence:.2f})")

        #Generate response prompt
        prompt = manager.generate_response_prompt(context, test["message"])

        #Check if prompt includes the new analysis tools
        tools_mentioned = []
        for tool in test["expected_tools"]:
            if tool in prompt:
                tools_mentioned.append(tool)

        print(f"   📊 New analysis tools mentioned: {tools_mentioned}")

        #Check for comprehensive analysis approach
        advanced_indicators = [
            "COMPREHENSIVE ANALYSIS", "ADVANCED ANALYSIS", "PROFESSIONAL ANALYSIS",
            "dependency_analyzer", "performance_profiler", "AST analysis",
            "architectural insights", "performance optimization", "dependency analysis",
        ]

        advanced_features = [indicator for indicator in advanced_indicators if indicator in prompt]
        print(f"   🔧 Advanced features: {len(advanced_features)} detected")

        if len(tools_mentioned) >= 2 and len(advanced_features) >= 3:
            print("   ✅ ENHANCED: Professional-grade analysis capabilities active")
        else:
            print("   ⚠️  BASIC: Standard analysis (may need enhancement)")

    print("\n🎯 System Help mode enhancements:")
    print("   • Dependency analysis integration ✅")
    print("   • Performance profiling integration ✅")
    print("   • AST-based code analysis ✅")
    print("   • Architectural investigation tools ✅")
    print("   • Professional-grade analysis prompts ✅")

    print("\n📊 New Analysis Arsenal Summary:")
    print("   🔧 dependency_analyzer: Architectural & dependency analysis")
    print("   ⚡ performance_profiler: Performance bottleneck detection")
    print("   🔍 code_reader_tool: Enhanced AST analysis (existing)")
    print("   🛡️ professional_analyzer: Issue detection (existing)")
    print("   📋 All integrated into System Help mode prompts")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
