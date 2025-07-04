# 🔧 Інструкція: Як правильно налаштувати Groq в Atlas

## ✅ Проблема вирішена!

Система збереження налаштувань тепер працює правильно. Ваші налаштування Groq будуть зберігатися та відновлюватися при кожному запуску.

## 🎯 Покрокова інструкція

### 1. **Відкрийте Atlas**

### 2. **Перейдіть до вкладки "Settings"**
- Знайдіть поле "Groq API Key"
- Введіть ваш реальний Groq API ключ (починається з `gsk_`)

### 3. **Перейдіть до вкладки "Enhanced Settings"**
- У розділі "LLM Configuration":
  - Виберіть "Groq" як **Current Provider**
  - Виберіть модель (наприклад, "llama3-8b-8192")

### 4. **Збережіть налаштування**
- Натисніть кнопку **"Save Settings"**
- Ви побачите повідомлення: `Settings saved and applied successfully. Current provider: groq, model: llama3-8b-8192`

### 5. **Перезапустіть Atlas**
- Закрийте Atlas
- Запустіть Atlas знову

### 6. **Перевірте налаштування**
При запуску ви побачите повідомлення:
```
Settings loaded successfully. Current provider: groq, model: llama3-8b-8192
```

## 🔍 Перевірка налаштувань

### Через термінал:
```bash
cat ~/.atlas/config.yaml
```

Ви повинні побачити:
```yaml
current_provider: groq
current_model: llama3-8b-8192
api_keys:
  groq: ваш-реальний-ключ
  # ... інші ключі
```

### Через Atlas:
- Відкрийте вкладку "Chat"
- Запитайте: "What is my current LLM provider?"
- Atlas повинен відповісти, що використовує Groq

## 🛠️ Що було виправлено

### 1. **Покращена функція збереження**
- Тепер зберігається `current_provider` та `current_model`
- API ключі зберігаються правильно

### 2. **Покращена функція завантаження**
- LLM менеджер оновлюється з збереженими налаштуваннями
- Клієнти переініціалізуються з новими налаштуваннями

### 3. **Автоматичне збереження**
- Налаштування зберігаються при закритті програми
- При запуску налаштування автоматично відновлюються

## 🧪 Тестування

Система протестована і працює правильно:
- ✅ Збереження API ключів
- ✅ Збереження провайдера та моделі
- ✅ Правильне завантаження налаштувань
- ✅ Оновлення LLM менеджера

## 🚨 Важливі зауваження

### API ключ Groq:
- Повинен починатися з `gsk_`
- Не повинен містити пробілів або зайвих символів
- Повинен бути дійсним ключем від Groq

### Моделі Groq:
- `llama3-8b-8192` - швидка модель
- `llama3-70b-8192` - потужна модель
- `mixtral-8x7b-32768` - збалансована модель

## 🔧 Якщо налаштування не зберігаються

### 1. **Перевірте права доступу**
```bash
ls -la ~/.atlas/
```

### 2. **Перевірте файл конфігурації**
```bash
cat ~/.atlas/config.yaml
```

### 3. **Скиньте налаштування**
```bash
rm ~/.atlas/config.yaml
```

### 4. **Перезапустіть Atlas**
- Atlas створить новий файл конфігурації з дефолтними налаштуваннями

## 📞 Підтримка

Якщо у вас виникли проблеми:
1. Перевірте, чи правильно введений API ключ
2. Переконайтеся, що ви натиснули "Save Settings"
3. Перезапустіть Atlas після збереження
4. Перевірте логи в терміналі на наявність помилок

## 🎉 Результат

Після виконання всіх кроків:
- ✅ Ваш Groq API ключ буде збережено
- ✅ Groq буде встановлено як поточний провайдер
- ✅ Налаштування збережуться після перезавантаження
- ✅ Atlas буде використовувати Groq для всіх запитів 