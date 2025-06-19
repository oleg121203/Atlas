# Chat Context Management Rules

## Core Principles

### 1. English-Only Internal Processing
**CRITICAL RULE**: All internal processing, keywords, patterns, and system prompts MUST be in English only.

**Rationale**: 
- LLM providers process in English
- Two-way translation exists in chat interface
- Cyrillic/Ukrainian keywords in internal context cause processing errors
- Context analysis must be language-agnostic

**Implementation**:
- All `keywords` arrays in patterns: English only
- All regex patterns: English words only  
- All system prompts to LLM: English only
- All internal logs: English only
- All development comments: English only

**Example**:
```python
# ❌ WRONG - Cyrillic in internal processing
'keywords': ['memory', 'пам\'ять', 'довгострокова']

# ✅ CORRECT - English only internally
'keywords': ['memory', 'remember', 'long-term', 'storage']
```

### 2. User Interface Translation
- Users can write in any language (Ukrainian, Russian, English)
- Translation layer handles user input/output
- Internal processing stays English-only
- Response generation in English, then translated for user

### 3. Context Detection Strategy
Instead of matching Cyrillic keywords directly:
- Detect language first
- Translate user input to English if needed
- Process English version for context detection
- Generate English response
- Translate response back to user's language

### 4. Pattern Matching Rules
- Use semantic English patterns
- Focus on intent, not specific language
- Rely on translation layer for language handling
- Keep patterns simple and universal

### 5. Development Guidelines
- All code comments: English
- All variable names: English
- All documentation: English (with Ukrainian version separate)
- All debug logs: English
- All error messages: English

## Implementation Checklist

### For Chat Context Manager:
- [ ] Remove all Cyrillic keywords from patterns
- [ ] Convert all system prompts to English-only
- [ ] Update regex patterns to English words only
- [ ] Ensure all response templates are English
- [ ] Remove Ukrainian text from internal processing

### For Future Development:
- [ ] Language detection at input level
- [ ] Pre-translation before context analysis  
- [ ] Post-translation after response generation
- [ ] Consistent English-only internal state

## Examples

### Memory Question Handling:
```python
# User input (any language): "Чи забезпечена в тебе пам'ять?"
# Translation layer: "Do you have memory support?"
# Context detection: English keywords ["memory", "support", "have"]
# Response generation: English response about memory
# Translation back: Ukrainian response to user
```

### Pattern Example:
```python
# ❌ Wrong - mixed languages
'memory_patterns': [
    r'\b(memory|пам\'ять|забезпечена)\b'
]

# ✅ Correct - English only
'memory_patterns': [
    r'\b(memory|remember|storage|recall)\b'
]
```

## Rules to Add as Needed

1. **English-Only Internal Processing** (established above)

2. **System Help Mode Behavior** ⭐ NEW
   - MUST actively use code analysis tools for technical questions
   - MUST provide specific file paths and implementation details
   - MUST analyze actual codebase instead of giving generic answers
   - Should use: semantic_search, file_search, read_file, grep_search
   - Focus on technical expertise, not general overviews

3. **Tool Inquiry Mode Enhancement** ⭐ NEW
   - Detect technical implementation questions vs simple tool lists
   - For implementation questions: analyze codebase and provide file paths
   - For simple questions: provide organized tool lists
   - Use code analysis for "where implemented" and "how works" questions

4. **Mode Detection Improvements** ⭐ NEW
   - Enhanced translation includes technical terms
   - Better recognition of implementation-focused questions
   - Improved confidence scoring for technical queries

5. **Response Time Limits** - to be defined
6. **Context Confidence Thresholds** - to be defined  
7. **Mode Switching Logic** - to be defined
8. **Error Handling Protocols** - to be defined
9. **Memory Management Rules** - to be defined
10. **Development Mode Restrictions** - to be defined

---

*This document should be updated whenever new context management rules are established.*
