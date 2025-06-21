#!/usr/bin/env python3
"""
Швидка verification інтеграції з реальним Atlas
"""

import sys
from pathlib import Path

#Додаємо шляхи
base_dir = Path("/Users/developer/Documents/Atlas")
sys.path.insert(0, str(base_dir))

def check_atlas_integration():
    """Verification інтеграції з реальним Atlas"""
    print("🔍 ПЕРЕВІРКА ІНТЕГРАЦІЇ З ATLAS")
    print("=" * 40)
    
    #Verification наявності файлів
    files_to_check = [
        "intelligent_mode_detector.py",
        "plugins/helper_sync_tell/advanced_thinking.py",
        "main.py"
    ]
    
    print("\n📁 Перевірка файлів:")
    for file_path in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не знайдено")
    
    #Verification інтеграції advanced_thinking
    print("\n🔗 Перевірка інтеграції advanced_thinking:")
    try:
        sys.path.insert(0, str(base_dir / "plugins" / "helper_sync_tell"))
        from advanced_thinking import register
        
        #Тест реєстрації
        result = register()
        if result and 'tools' in result:
            tool = result['tools'][0]
            print(f"✅ Advanced thinking tool зареєстровано: {tool.__class__.__name__}")
            
            #Verification capabilities
            if hasattr(tool, 'capabilities'):
                caps = tool.capabilities
                print("📊 Можливості:")
                for cap, available in caps.items():
                    status = "✅" if available else "❌"
                    print(f"   {status} {cap}")
            
        else:
            print("❌ Помилка реєстрації advanced thinking")
            
    except Exception as e:
        print(f"❌ Помилка імпорту advanced_thinking: {e}")
    
    #Verification детектора
    print("\n🧠 Перевірка інтелектуального детектора:")
    try:
        from intelligent_mode_detector import IntelligentModeDetector
        
        detector = IntelligentModeDetector()
        
        #Швидкий тест
        test_result = detector.detect_chat_mode("Проаналізуй систему Atlas")
        print(f"✅ Детектор працює: {test_result.mode.value} (впевненість: {test_result.confidence:.2f})")
        
    except Exception as e:
        print(f"❌ Помилка детектора: {e}")
    
    #Verification main.py
    print("\n📱 Перевірка main.py:")
    try:
        with open(base_dir / "main.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '_handle_help_mode' in content:
            print("✅ Метод _handle_help_mode існує в main.py")
        else:
            print("❌ Метод _handle_help_mode не знайдено")
            
    except Exception as e:
        print(f"❌ Помилка читання main.py: {e}")
    
    print("\n🎯 Рекомендації для активації:")
    print("1. Переконайтеся, що intelligent_mode_detector.py знаходиться в корені Atlas")
    print("2. Перезапустіть Atlas для активації оновленого плагіна")
    print("3. Протестуйте команди:")
    print("   - Просту: 'read file main.py'")
    print("   - Складну: 'Проаналізуй архітектуру Atlas'")

if __name__ == "__main__":
    check_atlas_integration()
