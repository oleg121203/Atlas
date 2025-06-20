# Advanced Web Browsing Plugin

Потужний плагін для веб-автоматизації з множинними fallback методами для гарантованого виконання завдань.

## 🌟 Особливості

### Каскадні методи автоматизації:
1. **Selenium WebDriver** (первинний)
   - Chrome, Firefox, Safari
   - Повна автоматизація браузера
   - Підтримка JavaScript

2. **Playwright** (вторинний)
   - Chromium, Firefox, WebKit
   - Швидша робота
   - Краща стабільність

3. **System Events + PyAutoGUI** (третинний)
   - Пряме управління мишкою та клавіатурою
   - Роботає з будь-яким браузером
   - OCR для знаходження елементів

4. **HTTP Requests** (фінальний fallback)
   - Прямі HTTP запити
   - Для простого скрапінгу
   - Завжди доступний

## 🚀 Встановлення

```bash
# Перейти в директорію плагіна
cd plugins/web_browsing

# Запустити setup скрипт
python setup.py
```

## 🔧 Доступні інструменти

### 1. `navigate_to_url(url: str)`
Навігація на URL з автоматичним fallback між методами.

**Приклад:**
```python
navigate_to_url("https://auto.ria.com")
```

### 2. `search_on_site(search_term: str, search_field_selector: str = None, submit_selector: str = None)`
Пошук на поточному сайті з автоматичним знаходженням полів пошуку.

**Приклад:**
```python
search_on_site("Mustang 2024")
# Або з конкретними селекторами
search_on_site("Mustang 2024", "#search-input", ".search-button")
```

### 3. `click_element(selector: str, selector_type: str = "css", text: str = None, image_path: str = None)`
Клік по елементу з множинними способами знаходження.

**Приклади:**
```python
# CSS селектор
click_element(".search-button")

# XPath
click_element("//button[contains(text(), 'Пошук')]", "xpath")

# За текстом (system events)
click_element("", "css", text="Пошук")

# За зображенням
click_element("", "css", image_path="button_image.png")
```

### 4. `fill_form_field(selector: str, value: str, selector_type: str = "css", clear_first: bool = True)`
Заповнення форм з автоматичним очищенням.

**Приклад:**
```python
fill_form_field("#search-input", "Ford Mustang")
```

### 5. `scrape_page_content(selectors: str = None)`
Скрапінг контенту сторінки.

**Приклади:**
```python
# Весь контент
scrape_page_content()

# Конкретні елементи
scrape_page_content('[".car-item", ".price", ".title"]')
```

### 6. `wait_for_element(selector: str, timeout: int = 30)`
Очікування появи елемента.

**Приклад:**
```python
wait_for_element(".search-results", 10)
```

### 7. `take_screenshot(filename: str = None)`
Створення скріншота поточної сторінки.

**Приклад:**
```python
take_screenshot("search_results.png")
```

### 8. `execute_javascript(script: str)`
Виконання JavaScript коду.

**Приклад:**
```python
execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
```

### 9. `handle_popup(action: str = "accept")`
Обробка спливаючих вікон.

**Приклад:**
```python
handle_popup("accept")  # або "dismiss"
```

### 10. `scroll_page(direction: str = "down", amount: int = 3)`
Прокрутка сторінки.

**Приклади:**
```python
scroll_page("down", 5)
scroll_page("top")
scroll_page("bottom")
```

## 🎯 Приклад використання для пошуку авто

```python
# 1. Відкрити сайт
navigate_to_url("https://auto.ria.com")

# 2. Дочекатися завантаження
wait_for_element(".search-form", 10)

# 3. Заповнити марку
fill_form_field('select[name="brand"]', "Ford")

# 4. Заповнити модель  
fill_form_field('select[name="model"]', "Mustang")

# 5. Заповнити рік
fill_form_field('input[name="year_from"]', "2024")

# 6. Запустити пошук
click_element('.search-button')

# 7. Дочекатися результатів
wait_for_element('.search-results', 15)

# 8. Зскрапити результати
results = scrape_page_content('[".ticket-item", ".price-ticket", ".bold"]')

# 9. Зробити скріншот
take_screenshot("mustang_search_results.png")
```

## 🔄 Автоматичні Fallback сценарії

Плагін автоматично переключається між методами при помилках:

### Сценарій 1: Selenium недоступний
```
Selenium (Chrome fail) → Selenium (Firefox) → Playwright → System Events
```

### Сценарій 2: Елемент не знайдено
```
CSS Selector → XPath → Text Search → Image Recognition → Manual Click
```

### Сценарій 3: Headless середовище
```
Selenium Headless → Playwright Headless → HTTP Requests
```

## ⚙️ Конфігурація

Плагін автоматично визначає доступні методи та налаштовується під платформу:

- **macOS**: Повна підтримка всіх методів + Safari
- **Linux**: Headless режим, без system events
- **Windows**: Повна підтримка всіх методів

## 🚨 Troubleshooting

### Помилка: "Chrome driver not found"
```bash
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Помилка: "Playwright browsers not installed"
```bash
python -m playwright install
```

### macOS: "Accessibility permissions required"
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Додати Terminal/VS Code/IDE
3. Перезапустити додаток

## 📊 Моніторинг та логування

Плагін логує всі спроби та fallback переключення:

```
INFO: Navigating to: https://auto.ria.com
INFO: Available web automation methods: ['selenium', 'playwright', 'system_events', 'http_requests']
WARNING: Selenium Chrome driver failed: ChromeDriver not found
INFO: Selenium Firefox driver initialized
INFO: Successfully navigated using selenium
```

Це забезпечує максимальну надійність виконання веб-завдань!
