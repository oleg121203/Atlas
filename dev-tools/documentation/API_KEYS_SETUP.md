# 🔧 Налаштування API ключів та провайдерів в Atlas

## 📁 Де зберігаються налаштування

Всі налаштування Atlas зберігаються в файлі:
```
~/.atlas/config.yaml
```

## 🔑 Як додати API ключі

### Через GUI (Рекомендовано):

1. **Запустіть Atlas** - `python main.py`

2. **Перейдіть на вкладку "Settings"** в інтерфейсі

3. **Заповніть API ключі:**
   - **OpenAI API Key** - для ChatGPT/GPT-4
   - **Gemini API Key** - для Google Gemini
   - **Anthropic API Key** - для Claude

4. **Оберіть провайдера** в розділі "Agent Configuration"

5. **Натисніть "Save Settings"** - це збереже всі налаштування в `~/.atlas/config.yaml`

### Через редагування файлу:

```yaml
api_keys:
  openai: 'sk-вашключ...'
  gemini: 'вашключ...'
  anthropic: 'вашключ...'
current_provider: 'gemini'
current_model: 'gemini-1.5-flash'
```

## ⚠️ Типові проблеми та рішення

### Проблема: Налаштування втрачаються після перезапуску

**Причина:** Налаштування не зберігаються або зберігаються в неправильному форматі.

**Рішення:**
1. Переконайтеся, що ви натиснули **"Save Settings"** після внесення змін
2. Перевірте права доступу до директорії `~/.atlas/`
3. Перегляньте файл `~/.atlas/config.yaml` - він має містити ваші API ключі

### Проблема: "API key not found in config"

**Причина:** LLMManager не може знайти API ключ.

**Рішення:**
1. Перевірте, що API ключ збережений в `~/.atlas/config.yaml`
2. Перезапустіть Atlas після збереження налаштувань
3. Переконайтеся, що ключ не містить зайвих пробілів

### Проблема: Провайдер не змінюється

**Причина:** Налаштування провайдера не зберігаються.

**Рішення:**
1. Виберіть провайдера в GUI
2. Обов'язково натисніть **"Save Settings"**
3. Перезапустіть Atlas

## 🔍 Перевірка налаштувань

Щоб перевірити поточні налаштування:

```bash
cat ~/.atlas/config.yaml
```

Файл повинен виглядати приблизно так:
```yaml
api_keys:
  openai: 'sk-ваш-openai-ключ'
  gemini: 'ваш-gemini-ключ'
  anthropic: 'ваш-anthropic-ключ'
current_provider: 'gemini'
current_model: 'gemini-1.5-flash'
agents:
  Browser Agent:
    provider: gemini
    model: gemini-1.5-flash
  # ... інші агенти
```

## 🎯 Рекомендовані налаштування

### Для економії токенів:
- **Провайдер:** Gemini
- **Модель:** gemini-1.5-flash

### Для найкращої якості:
- **Провайдер:** OpenAI
- **Модель:** gpt-4-turbo

### Для швидкості:
- **Провайдер:** Gemini
- **Модель:** gemini-1.5-flash

## 🔄 Після збереження налаштувань

1. Atlas автоматично перезавантажить LLM клієнти
2. Ви побачите повідомлення про успішне збереження
3. API ключі будуть доступні для всіх агентів

---

💡 **Порада:** Завжди зберігайте резервну копію файлу `~/.atlas/config.yaml` з вашими налаштуваннями!
