# Atlas Public API and SDK Documentation

This document provides detailed information on how to use the Atlas Public API and SDK for third-party developers to interact with Atlas functionalities.

## Table of Contents
- [Overview](#overview)
- [Public API](#public-api)
  - [Endpoints](#endpoints)
    - [Get Suggestion](#get-suggestion)
    - [Automate Task](#automate-task)
- [SDK Usage](#sdk-usage)
  - [Installation](#installation)
  - [Initialization](#initialization)
  - [Examples](#examples)
    - [Getting a Suggestion](#getting-a-suggestion)
    - [Automating a Task](#automating-a-task)

## Overview
The Atlas Public API and SDK allow developers to integrate with Atlas's AI capabilities, including context-aware suggestions and task automation. The API is RESTful, and the SDK provides a convenient Python interface to interact with these endpoints.

## Public API

### Endpoints

#### Get Suggestion
- **URL**: `/api/v1/suggestion`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <api_key>` (if required)
- **Request Body**:
  ```json
  {
    "model_name": "string",
    "context": {"key": "value"},
    "prompt_type": "string" (optional, default: "general")
  }
  ```
- **Response**:
  - Success (200):
    ```json
    {
      "suggestion": "string"
    }
    ```
  - Error (400, 500):
    ```json
    {
      "error": "string"
    }
    ```

#### Automate Task
- **URL**: `/api/v1/automate`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <api_key>` (if required)
- **Request Body**:
  ```json
  {
    "model_name": "string",
    "task_description": "string",
    "context": {"key": "value"} (optional)
  }
  ```
- **Response**:
  - Success (200):
    ```json
    {
      "plan": {
        "steps": [
          {
            "step": "string",
            "action": "string",
            "expected_outcome": "string"
          }
        ]
      }
    }
    ```
  - Error (400, 500):
    ```json
    {
      "error": "string"
    }
    ```

## SDK Usage

### Installation
The Atlas SDK will be available on PyPI. For now, you can use the provided `sdk.py` file directly in your project.

```bash
# Future installation command
# pip install atlas-sdk
```

### Initialization
```python
from core.sdk import AtlasSDK

# Initialize SDK with default or custom base URL and optional API key
sdk = AtlasSDK(base_url='http://localhost:5000/api/v1', api_key='your_api_key')
```

### Examples

#### Getting a Suggestion
```python
# Get a context-aware suggestion
context = {
    'user_input': 'How to improve code quality?'
}
response = sdk.get_suggestion(model_name='gpt-3.5-turbo', context=context, prompt_type='code')

if 'suggestion' in response:
    print(f"Suggestion: {response['suggestion']}")
else:
    print(f"Error: {response.get('error', 'Unknown error')}")
```

#### Automating a Task
```python
# Automate a task with AI
task_description = 'Write a Python script to read a CSV file.'
context = {
    'file_path': '/path/to/data.csv'
}
response = sdk.automate_task(model_name='gpt-4', task_description=task_description, context=context)

if 'plan' in response:
    print("Automation Plan:")
    for step in response['plan'].get('steps', []):
        print(f"- Step: {step['step']}, Action: {step['action']}, Outcome: {step['expected_outcome']}")
else:
    print(f"Error: {response.get('error', 'Unknown error')}")
```
