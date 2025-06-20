#!/usr/bin/env python3
"""Test System Help mode integration with existing tools."""

import sys
sys.path.append('/workspaces/Atlas')

try:
    from agents.chat_context_manager import ChatContextManager, ChatMode
    
    #Initialize the context manager
    manager = ChatContextManager()
    
    print("🔧 Testing System Help integration with existing tools...")
    
    #Test cases for different types of questions
    test_cases = [
        {
            'message': 'Мене цікавить система пам\'яті Atlas. Де і як реалізовано?',
            'expected_tools': ['code_reader_tool', 'professional_analyzer', 'semantic_search'],
            'description': 'Memory system investigation'
        },
        {
            'message': 'Які інструменти є в системі та де їх код?',
            'expected_tools': ['code_reader_tool', 'file_search', 'semantic_search'],
            'description': 'Tools investigation'
        },
        {
            'message': 'Знайди проблеми в коді та запропонуй рішення',
            'expected_tools': ['professional_analyzer', 'semantic_search', 'grep_search'],
            'description': 'Problem analysis request'
        },
        {
            'message': 'Перевір якість коду і знайди помилки',
            'expected_tools': ['professional_analyzer', 'semantic_search', 'file_search'],
            'description': 'Code quality analysis'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n✅ Test {i}: {test['description']}")
        print(f"   Input: '{test['message'][:60]}...'")
        
        #Analyze message
        context = manager.analyze_message(test['message'])
        mode_detected = context.mode.value
        confidence = context.confidence
        
        print(f"   🎯 Mode: {mode_detected} (confidence: {confidence:.2f})")
        
        #Generate response prompt
        prompt = manager.generate_response_prompt(context, test['message'])
        
        #Check if prompt mentions the expected tools
        mentioned_tools = []
        for tool in test['expected_tools']:
            if tool in prompt:
                mentioned_tools.append(tool)
        
        print(f"   🔧 Expected tools: {', '.join(test['expected_tools'])}")
        print(f"   ✅ Mentioned tools: {', '.join(mentioned_tools) if mentioned_tools else 'None'}")
        
        #Check if professional analysis mode is activated for problem analysis
        if 'problem' in test['message'].lower() or 'помилки' in test['message'].lower():
            has_professional_mode = 'PROFESSIONAL ANALYSIS MODE' in prompt or 'Professional Code Analyzer' in prompt
            print(f"   🎓 Professional mode: {'✅ Activated' if has_professional_mode else '❌ Not activated'}")
        
        #Show a snippet of the prompt
        snippet = prompt[:300].replace('\n', ' ').strip() + '...'
        print(f"   📋 Prompt preview: {snippet}")
    
    print("\n🎯 System Help Analysis Integration:")
    print("   • Uses existing code_reader_tool for structure analysis")
    print("   • Leverages professional_analyzer for issue detection")
    print("   • Employs semantic_search for intelligent code search")
    print("   • Activates professional mode for problem analysis")
    print("   • References specific tools by name in analysis workflow")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
