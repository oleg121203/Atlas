#!/usr/bin/env python3
"""
Швидкий запуск Atlas без індексації коду для тестування
"""

import os
import sys

# Відключаємо індексацію коду
os.environ['ATLAS_DISABLE_CODE_INDEXING'] = 'true'

# Додаємо Atlas до шляху
atlas_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, atlas_dir)

# Запускаємо Atlas
if __name__ == "__main__":
    print("🚀 Запуск Atlas без індексації коду...")
    print("📋 Індексація коду відключена для швидкого запуску")
    
    try:
        from main import AtlasApp
        app = AtlasApp()
        app.mainloop()  # Використовуємо mainloop() замість run()
    except KeyboardInterrupt:
        print("\n👋 Atlas зупинено користувачем")
    except Exception as e:
        print(f"❌ Помилка при запуску Atlas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
