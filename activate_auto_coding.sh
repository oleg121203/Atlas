#!/bin/bash

# === АТЛАС АВТО-КОДИНГ СИСТЕМА ===
# Активація повної автоматизації Ruff + AI для локальної розробки

echo "🚀 Активація Atlas Auto-Coding System..."

# Перевірка Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama не встановлено. Встановіть спочатку ollama."
    exit 1
fi

# Запуск Ollama
echo "🔄 Запуск Ollama..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!

# Перевірка моделей
echo "🧠 Перевірка AI моделей..."
if ! ollama list | grep -q "qwen2.5-coder:latest"; then
    echo "⬇️  Завантаження qwen2.5-coder:latest..."
    ollama pull qwen2.5-coder:latest
fi

if ! ollama list | grep -q "qwen2.5-coder:1.5b"; then
    echo "⬇️  Завантаження qwen2.5-coder:1.5b..."
    ollama pull qwen2.5-coder:1.5b
fi

# Перевірка і встановлення pre-commit хуків
echo "🔧 Налаштування pre-commit хуків..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit хуки активовано"
else
    echo "⚠️  pre-commit не встановлено. Встановіть: pip install pre-commit"
fi

# Запуск автоматичного watcher для Ruff
echo "👁️  Запуск Ruff auto-watcher..."
if command -v watchexec &> /dev/null; then
    watchexec -e py -- ruff check --fix --unsafe-fixes . &
    WATCHER_PID=$!
    echo "✅ Ruff watcher активовано (PID: $WATCHER_PID)"
else
    echo "⚠️  watchexec не встановлено. Встановіть: brew install watchexec"
fi

# Запуск VS Code
echo "💻 Запуск VS Code з налаштуваннями..."
code .

echo ""
echo "🎉 Atlas Auto-Coding System активовано!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Активні процеси:"
echo "   • Ollama Server (PID: $OLLAMA_PID)"
if [ ! -z "$WATCHER_PID" ]; then
    echo "   • Ruff Auto-Watcher (PID: $WATCHER_PID)"
fi
echo "   • VS Code з Continue AI"
echo ""
echo "🔥 Функціонал:"
echo "   ✓ Автоматичне виправлення коду при збереженні"
echo "   ✓ AI асистент для складних помилок"
echo "   ✓ Pre-commit хуки для контролю якості"
echo "   ✓ Постійний моніторинг файлів"
echo ""
echo "💡 Використання:"
echo "   • Просто редагуйте .py файли - Ruff виправить автоматично"
echo "   • Використовуйте Ctrl+I в VS Code для AI асистента"
echo "   • Складні помилки можна виправити через Continue"
echo ""
echo "🛑 Для зупинки: killall ollama watchexec"
