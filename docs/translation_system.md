# Chat Translation System

The Atlas chat translation system provides automatic translation support for Ukrainian and Russian users, ensuring that all internal processing happens in English while providing localized responses for better user experience.

## Overview

The translation system consists of three main components:

1. **TranslationTool** (`tools/translation_tool.py`) - Core translation functionality
2. **ChatTranslationManager** (`agents/chat_translation_manager.py`) - Chat-specific translation management
3. **Main Integration** - Integrated into the chat processing pipeline in `main.py`

## Features

### Automatic Language Detection

The system automatically detects when users write in Ukrainian or Russian with high accuracy:

- **Ukrainian Detection**: Recognizes Ukrainian-specific letters (і, ї, є, ґ), common words, and grammatical patterns
- **Russian Detection**: Identifies Russian-specific letters (ы, ъ, э, ё) and common vocabulary
- **Confidence Scoring**: Provides confidence levels for detection accuracy
- **Fallback to English**: Defaults to English for unclear or mixed-language input

### Translation Pipeline

#### Incoming Messages (User → System)
1. User types in Ukrainian/Russian
2. System detects language and confidence level
3. Message is translated to English for internal processing
4. All reasoning, planning, and tool invocation happens in English
5. Translation status is shown to user

#### Outgoing Responses (System → User)
1. System generates response in English
2. Response is automatically translated back to user's detected language
3. User sees response in their preferred language

### Internal Processing in English

**Critical Design Decision**: All internal Atlas operations remain in English:
- Goal planning and execution
- Tool invocation and reasoning
- Agent communication
- System logs and debugging
- Error messages (for developers)

This ensures maximum system stability and consistency.

## Usage

### For Users

Ukrainian/Russian users can simply chat naturally:

```
User (Ukrainian): Привіт! Чи можеш створити скріншот екрана?
System Response: 🌐 Detected Ukrainian. Processing in English and will translate response back.
System Response: Звичайно! Я створю скріншот екрана для вас. [creates screenshot]
```

### For Developers

#### Manual Translation
```python
from tools.translation_tool import TranslationTool

tool = TranslationTool(llm_manager)
result = tool.translate_to_english("Привіт, як справи?")
print(result.text)  # "Hello, how are you?"
```

#### Translation Manager
```python
from agents.chat_translation_manager import ChatTranslationManager

manager = ChatTranslationManager(llm_manager)
processed_msg, context = manager.process_incoming_message("Допоможи мені")
response = manager.process_outgoing_response("I can help you!", context.session_id)
```

## Configuration

### Language Support

Currently supported languages:
- **English** (en) - Default system language
- **Ukrainian** (uk) - Full translation support
- **Russian** (ru) - Full translation support

### Requirements

- LLM Manager must be configured and available
- Translation requires an active LLM provider (OpenAI, Gemini, etc.)
- Internet connection for LLM-based translation

## Technical Details

### Language Detection Patterns

#### Ukrainian Patterns
- Ukrainian-specific letters: `[іїєґ]`
- Common words: `привіт`, `день`, `можеш`, `допоможи`
- Apostrophes in contractions
- Grammatical endings and prefixes

#### Russian Patterns
- Russian-specific letters: `[ыъэё]`
- Common words: `привет`, `день`, `можешь`, `помоги`
- Cyrillic patterns specific to Russian

### Translation Quality

- **LLM-Powered**: Uses the same LLM as Atlas for high-quality translations
- **Context Preservation**: Maintains technical terms and intent
- **Tone Matching**: Preserves formality and style
- **Error Handling**: Graceful fallback to original text if translation fails

## Integration Points

### Main Chat Pipeline
- Integrated in `main.py` `_process_chat_message()` method
- Automatic translation of both incoming and outgoing messages
- Seamless user experience with translation status indicators

### Built-in Tools
- `translate_text` - Direct translation function
- `detect_language` - Language detection tool
- Available for system use if needed

### Tool Management
- Translation tools appear in Tool Management view
- Counted as built-in tools (now 24 total)
- Can be enabled/disabled like other tools

## Testing

Run the translation system tests:

```bash
python test_translation_system.py
```

Tests cover:
- Language detection accuracy
- Translation context management
- Status and debugging features
- Mock LLM translation scenarios

## Benefits

### For Users
- **Native Language Support**: Chat in Ukrainian or Russian naturally
- **Seamless Experience**: No need to switch languages or use translation services
- **Clear Communication**: Responses in familiar language improve understanding

### For System Stability
- **English Internal Processing**: All system logic remains in English for consistency
- **Reduced Errors**: Avoids language-related confusion in planning and execution
- **Better Tool Integration**: All tools receive consistent English input
- **Easier Debugging**: System logs and errors remain in English

### For Developers
- **Maintainable Code**: All code and comments remain in English
- **Consistent API**: Tool interfaces don't need localization
- **Extensible**: Easy to add more languages without changing core logic

## Future Enhancements

- Support for additional languages (Polish, Czech, etc.)
- User language preference persistence
- Translation quality feedback and improvement
- Offline translation options for privacy
- Custom translation models for technical terms

## Troubleshooting

### No Translation Occurring
1. Check if LLM manager is configured
2. Verify API keys are set for LLM provider
3. Ensure internet connectivity
4. Check confidence threshold (minimum 0.3 required)

### Incorrect Language Detection
1. Use longer, more characteristic phrases
2. Include language-specific words or letters
3. Check confidence scores in debug output
4. Report false positives for pattern improvement

### Translation Quality Issues
1. Verify LLM provider is working properly
2. Check if technical terms need to be preserved
3. Consider adjusting translation prompts if needed
4. Report specific issues for prompt refinement
