# Atlas Development Commands Reference

## Налаштування середовищ

### Linux Development Environment (Python 3.12)
```bash
# Ініціальне налаштування
./setup_dev_linux.sh

# Активація середовища розробки
source venv-dev/bin/activate

# Перевірка налаштувань
python main.py --platform-info --config config-dev.ini
```

### macOS Production Environment (Python 3.13)
```bash
# Запуск продакшн версії
./launch_macos.sh

# Ручне налаштування
python3.13 -m venv venv-macos
source venv-macos/bin/activate
pip install -r requirements-macos.txt
```

## Команди розробки

### Тестування на Linux (Development)
```bash
# Активація dev середовища
source venv-dev/bin/activate

# Headless режим
python main.py --headless --debug --config config-dev.ini

# CLI тестування
python main.py --cli --config config-dev.ini

# Тести
python -m pytest tests/ -v
python -m pytest tests/ --headless

# Форматування коду
black .
flake8 .
mypy .
```

### Тестування на macOS (Production)
```bash
# Активація prod середовища
source venv-macos/bin/activate

# GUI режим
python main.py --config config-macos.ini

# Тестування нативних функцій
python main.py --test-native --config config-macos.ini

# Перевірка дозволів
python main.py --check-permissions

# Тестування скріншотів
python -c "from tools.screenshot_tool import capture_screen; capture_screen()"
```

## Налагодження

### Linux Development Debug
```bash
# Повне логування
python main.py --debug --log-level DEBUG --headless

# Профілювання
python -m cProfile -o profile.stats main.py --headless

# Аналіз профілю
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('time').print_stats(20)"
```

### macOS Production Debug
```bash
# macOS debug режим
python main.py --debug --config config-macos.ini

# Перевірка платформи
python main.py --platform-info

# Тестування GUI компонентів
python main.py --test-gui --config config-macos.ini
```

## Управління залежностями

### Оновлення залежностей
```bash
# Linux dev dependencies
pip freeze > requirements-linux-frozen.txt

# macOS prod dependencies  
pip freeze > requirements-macos-frozen.txt

# Перевірка сумісності
pip-compile requirements-linux.txt
pip-compile requirements-macos.txt
```

### Перевірка конфліктів
```bash
# Перевірка залежностей Linux
pipdeptree --warn conflict

# Перевірка залежностей macOS
pipdeptree --warn conflict
```

## Збірка та релізи

### Development Build (Linux)
```bash
# Збірка dev версії
python setup.py build_dev

# Тестова збірка
python -m build --dev

# Docker збірка для CI/CD
docker build -f Dockerfile.dev -t atlas:dev .
```

### Production Build (macOS)
```bash
# Збірка для macOS
python setup.py bdist_dmg

# Підписання (якщо є сертифікат)
codesign -s "Developer ID" dist/Atlas.app

# Створення DMG
hdiutil create -srcfolder dist/Atlas.app -volname "Atlas" Atlas.dmg
```

## Моніторинг та метрики

### Performance Monitoring
```bash
# Моніторинг пам'яті
python -m memory_profiler main.py --headless

# CPU профілювання
python -m cProfile main.py --headless > cpu_profile.txt

# Моніторинг мережі
python -m trace --trace main.py --headless 2>&1 | grep -E "(socket|http|request)"
```

### Log Analysis
```bash
# Аналіз логів розробки
tail -f logs/atlas-dev.log | grep ERROR

# Аналіз логів продакшн
tail -f ~/Library/Application\ Support/Atlas/logs/atlas.log

# Парсинг метрик
python dev-tools/analyze_logs.py logs/atlas-dev.log
```

## Cross-Platform Testing

### Compatibility Tests
```bash
# Тестування на обох платформах
python dev-tools/cross_platform_test.py

# Порівняння поведінки
python dev-tools/compare_platforms.py --linux --macos

# Benchmark
python dev-tools/benchmark.py --platform all
```

### Integration Tests  
```bash
# Повний інтеграційний тест
python -m pytest tests/integration/ --slow

# Тест GUI (тільки macOS)
python -m pytest tests/gui/ --macos-only

# Headless тести (Linux)
python -m pytest tests/headless/ --linux-only
```

## Утиліти

### Code Quality
```bash
# Повна перевірка якості
./dev-tools/check_quality.sh

# Безпека коду
bandit -r . -x tests/

# Документація
pydoc-markdown > docs/api.md
```

### Backup and Sync
```bash
# Backup конфігурації
cp config-dev.ini config-dev.ini.backup
cp config-macos.ini config-macos.ini.backup

# Синхронізація між середовищами
rsync -av --exclude='venv*' . user@macos-machine:~/Atlas/
```

Використовуйте ці команди для ефективної розробки Atlas на двох платформах!
