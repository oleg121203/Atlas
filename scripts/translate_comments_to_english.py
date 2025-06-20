#!/usr/bin/env python3
"""
Translate Ukrainian comments and docstrings to English in Python files
Following Atlas development standards for cross-platform compatibility
"""

import os
import re
from pathlib import Path
from typing import Dict, List

#Translation dictionary for common Ukrainian programming terms
TRANSLATIONS = {
    #System terms
    "Система": "System",
    "система": "system", 
    "Ініціалізація": "Initialization",
    "ініціалізація": "initialization",
    "Конфігурація": "Configuration", 
    "конфігурація": "configuration",
    "Налаштування": "Settings",
    "налаштування": "settings",
    "Управління": "Management",
    "управління": "management",
    "Обробка": "Processing",
    "обробка": "processing",
    
    #Authentication terms
    "Аутентифікація": "Authentication",
    "аутентифікація": "authentication",
    "Ідентифікація": "Identification", 
    "ідентифікація": "identification",
    "Авторизація": "Authorization",
    "авторизація": "authorization",
    "Перевірка": "Verification",
    "перевірка": "verification",
    "Виклик": "Challenge",
    "виклик": "challenge",
    "Відповідь": "Response", 
    "відповідь": "response",
    "Сесія": "Session",
    "сесія": "session",
    
    #Security terms
    "Безпека": "Security",
    "безпека": "security",
    "Шифрування": "Encryption",
    "шифрування": "encryption",
    "Розшифрування": "Decryption",
    "розшифрування": "decryption",
    "Захист": "Protection",
    "захист": "protection",
    "Доступ": "Access",
    "доступ": "access",
    "Привілеї": "Privileges",
    "привілеї": "privileges",
    
    #Data terms
    "Дані": "Data",
    "дані": "data",
    "Кеш": "Cache",
    "кеш": "cache",
    "Логи": "Logs",
    "логи": "logs",
    "Збереження": "Storage",
    "збереження": "storage",
    "Завантаження": "Loading",
    "завантаження": "loading",
    
    #Action terms
    "Створення": "Creation",
    "створення": "creation",
    "Видалення": "Deletion",
    "видалення": "deletion",
    "Оновлення": "Update",
    "оновлення": "update",
    "Отримання": "Getting",
    "отримання": "getting",
    "Генерація": "Generation",
    "генерація": "generation",
    
    #Time terms
    "Тайм-аут": "Timeout",
    "тайм-аут": "timeout",
    "Час": "Time",
    "час": "time",
    "Неактивність": "Inactivity",
    "неактивність": "inactivity",
    "Продовження": "Extension",
    "продовження": "extension",
    
    #Status terms
    "Статус": "Status", 
    "статус": "status",
    "Стан": "State",
    "стан": "state",
    "Активний": "Active",
    "активний": "active",
    "Неактивний": "Inactive",
    "неактивний": "inactive",
    
    #Common phrases
    "для творця": "for creator",
    "творця": "creator",
    "Творець": "Creator",
    "творець": "creator",
    "Атлас": "Atlas",
    "поточний": "current",
    "Поточний": "Current",
    "новий": "new",
    "Новий": "New",
    "застарілий": "old",
    "Застарілий": "Old",
}

def translate_text(text: str) -> str:
    """Translate Ukrainian text to English using the translation dictionary"""
    result = text
    for uk, en in TRANSLATIONS.items():
        #Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(uk) + r'\b'
        result = re.sub(pattern, en, result)
    return result

def translate_comments_in_file(file_path: Path) -> bool:
    """Translate Ukrainian comments and docstrings in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        #Translate single-line comments
        def translate_comment(match):
            comment = match.group(1)
            translated = translate_text(comment)
            return f"#{translated}"
        
        content = re.sub(r'#\s*(.+)', translate_comment, content)
        
        #Translate docstrings
        def translate_docstring(match):
            quotes = match.group(1)  #""" or '''
            docstring = match.group(2)
            translated = translate_text(docstring)
            return f'{quotes}{translated}{quotes}'
        
        content = re.sub(r'(""")(.*?)(""")', translate_docstring, content, flags=re.DOTALL)
        content = re.sub(r"(''')(.*?)(''')", translate_docstring, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Translated comments in: {file_path}")
            return True
        else:
            print(f"📋 No translation needed: {file_path}")
            return False
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Translate Ukrainian comments in Atlas Python files"""
    print("🌍 ATLAS CODE TRANSLATION TO ENGLISH")
    print("=" * 50)
    print("Following Atlas development standards for cross-platform compatibility")
    print()
    
    root_dir = Path(".")
    
    #Directories to process
    dirs_to_process = [
        "agents",
        "tools", 
        "ui",
        "monitoring",
        "plugins",
        "scripts",
        "tests",
        "dev-tools",
        "utils"
    ]
    
    translated_files = 0
    total_files = 0
    
    #Process root level files
    for py_file in root_dir.glob("*.py"):
        if py_file.name not in ["translate_comments_to_english.py"]:
            total_files += 1
            if translate_comments_in_file(py_file):
                translated_files += 1
    
    #Process directories
    for dir_name in dirs_to_process:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                total_files += 1
                if translate_comments_in_file(py_file):
                    translated_files += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files translated: {translated_files}")
    print(f"   Files unchanged: {total_files - translated_files}")
    print("\n✅ Translation completed!")
    print("🎯 Atlas code now follows English-only development standards")

if __name__ == "__main__":
    main()
