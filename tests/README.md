# Atlas Tests

This directory contains all the test files for the Atlas project.

## Recent Fixes

### ✅ EnhancedMemoryManager Issue Fixed
- **Problem**: `EnhancedMemoryManager.__init__()` was missing required positional arguments: 'llm_manager' and 'config_manager'
- **Solution**: Updated `ChatContextManager` to properly pass the `memory_manager` parameter
- **Test**: `test_enhanced_memory_manager_fix.py` - Verifies the fix works correctly

## Test Categories

### Core Component Tests
- `test_enhanced_memory_manager_fix.py` - EnhancedMemoryManager initialization fix verification
- `test_enhanced_memory_integration.py` - Memory system integration
- `test_components_simple.py` - Basic component functionality
- `test_enhanced_components.py` - Advanced component features

### Agent Tests  
- `test_agent_manager.py` - Agent management functionality
- `test_agent_manager_reloading.py` - Agent reloading capabilities
- `test_master_agent.py` - Master agent functionality
- `test_tool_creator_agent.py` - Tool creation agent

### Feature Tests
- `test_chat_context.py` - Chat context management
- `test_chat_memory_system.py` - Memory system for conversations
- `test_mode_detection.py` - Mode detection system
- `test_mode_system.py` - Mode system functionality
- `test_translation_system.py` - Translation capabilities
- `test_translation_integration.py` - Translation integration

### Tool Tests
- `test_screenshot_tool.py` - Screenshot functionality
- `test_ocr_tool.py` - OCR capabilities  
- `test_clipboard_tool.py` - Clipboard operations
- `test_terminal_tool.py` - Terminal interactions
- `test_notification_tool.py` - Notification system
- `test_image_recognition_tool.py` - Image recognition

### Workflow Tests
- `test_full_workflow.py` - End-to-end workflow testing
- `test_multitask_integration.py` - Multi-task handling
- `test_security_workflow.py` - Security features
- `test_error_recovery.py` - Error handling and recovery
- `test_goal_clarification.py` - Goal clarification system

### System Tests
- `test_english_only_system.py` - English-only mode
- `test_cleaned_context.py` - Context cleaning functionality

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_enhanced_memory_manager_fix.py -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run tests for a specific component
python -m pytest tests/test_*agent*.py -v
```

## Test Environment

Tests are designed to work in both local and containerized environments. GUI-dependent tests use mocking to avoid X11/display requirements.

## Структура тестів:

### 🧪 Тести агентів:
- `test_agent_manager.py` - Тести менеджера агентів
- `test_agent_manager_reloading.py` - Тести перезавантаження агентів
- `test_master_agent.py` - Тести головного агента
- `test_security_workflow.py` - Тести безпеки

### 🛠️ Тести інструментів:
- `test_clipboard_tool.py` - Тести роботи з буфером обміну
- `test_image_recognition_tool.py` - Тести розпізнавання зображень
- `test_notification_tool.py` - Тести нотифікацій
- `test_ocr_tool.py` - Тести OCR
- `test_screenshot_tool.py` - Тести скріншотів
- `test_terminal_tool.py` - Тести терміналу
- `test_tool_creator_agent.py` - Тести створення інструментів

### 💬 Тести чату та контексту:
- `test_chat_context.py` - Тести контексту чату
- `test_cleaned_context.py` - Тести очищення контексту

### 🌐 Тести мовних систем:
- `test_english_only_system.py` - Тести англомовної системи
- `test_translation_integration.py` - Тести інтеграції перекладу
- `test_translation_system.py` - Тести системи перекладу

### 🎯 Тести режимів роботи:
- `test_mode_detection.py` - Тести виявлення режимів
- `test_mode_system.py` - Тести системи режимів

### 🔧 Інші тести:
- `test_components_simple.py` - Прості тести компонентів
- `test_enhanced_components.py` - Тести покращених компонентів
- `test_error_recovery.py` - Тести відновлення від помилок
- `test_full_workflow.py` - Тести повного робочого процесу
- `test_goal_clarification.py` - Тести уточнення цілей

## Запуск тестів:

```bash
# Запуск всіх тестів
python -m pytest tests/

# Запуск конкретного тесту
python -m pytest tests/test_agent_manager.py

# Запуск з детальним виводом
python -m pytest tests/ -v
```
