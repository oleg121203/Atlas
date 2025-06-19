# Chat Context System Documentation

## Overview

Atlas now features an enhanced chat context management system that intelligently analyzes user messages and provides appropriate responses based on the conversation context.

## Chat Modes

The system recognizes 6 different conversation modes:

### 💬 Casual Chat
- General conversation and social interaction
- Examples: "How are you?", "Nice to meet you", "Good morning"
- Response: Friendly, conversational tone while maintaining Atlas identity

### 🎯 Goal Setting  
- Task requests that require system integration
- Examples: "Take a screenshot", "Click on the button", "Open Calculator"
- Response: Executes the goal using MasterAgent and specialized agents

### ❓ System Help
- Questions about Atlas features and capabilities  
- Examples: "What can you do?", "How does Atlas work?", "Explain your features"
- Response: Informative explanations about Atlas capabilities

### 🔧 Tool Inquiry
- Questions about available tools and functions
- Examples: "What tools are available?", "List all functions", "Show me commands"
- Response: Comprehensive tool listings organized by category

### 📊 Status Check
- Requests for system status and performance information
- Examples: "What is the current status?", "How are things running?", "System health?"
- Response: Status reports with operational metrics

### ⚙️ Configuration
- Questions about settings and configuration
- Examples: "How do I set up API keys?", "Configure settings", "Change preferences"
- Response: Step-by-step configuration guidance

## Features

### Context Analysis
- **Keyword Detection**: Identifies relevant keywords for each mode
- **Pattern Matching**: Uses regex patterns for accurate classification
- **Confidence Scoring**: Provides confidence levels for classification accuracy
- **Fallback Handling**: Defaults to casual chat for ambiguous messages

### Visual Indicators
- **Mode Display**: Shows current conversation mode in the chat interface
- **Confidence Levels**: Displays confidence when below 80%
- **Context History**: Maintains conversation context across messages

### User Controls
- **Clear Context**: Button to reset conversation history and context
- **Mode Tracking**: Visual feedback on how messages are being interpreted

## Technical Implementation

### Core Components
- `ChatContextManager`: Main class for context analysis
- `ChatContext`: Data structure containing mode, confidence, and metadata
- `ChatMode`: Enum defining the 6 conversation modes

### Integration Points
- Integrated into `main.py` `_process_chat_message()` method
- Connected to chat UI with visual indicators
- Linked to response generation system

### Response Generation
Each mode has dedicated response templates that:
- Provide appropriate system prompts for the LLM
- Include relevant context information
- Maintain consistent Atlas personality
- Optimize for the specific conversation type

## Usage Examples

```python
# Analyze a message
context = chat_context_manager.analyze_message("Take a screenshot")
# Returns: ChatMode.GOAL_SETTING with high confidence

# Generate appropriate response
prompt = chat_context_manager.generate_response_prompt(context, message, system_info)
# Returns: Goal-oriented system prompt for LLM
```

## Benefits

1. **Improved User Experience**: More contextually appropriate responses
2. **Better Task Recognition**: Accurate identification of goals vs. questions
3. **Consistent Personality**: Maintains Atlas identity across different modes
4. **Visual Feedback**: Users understand how their messages are interpreted
5. **Conversation Memory**: Context tracking improves follow-up interactions

## Future Enhancements

- **Learning from User Feedback**: Improve classification accuracy over time
- **Multi-language Support**: Extend keyword patterns for other languages
- **Advanced Context**: Consider conversation history for better classification
- **Custom Modes**: Allow users to define custom conversation modes
