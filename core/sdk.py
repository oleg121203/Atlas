"""
SDK Module for Atlas

This module provides a Python SDK for third-party developers to interact with Atlas APIs.
"""

import requests
from typing import Dict, Any, Optional

class AtlasSDK:
    """SDK for interacting with Atlas API endpoints."""
    
    def __init__(self, base_url: str = 'http://localhost:5000/api/v1', api_key: Optional[str] = None):
        """
        Initialize the Atlas SDK.
        
        Args:
            base_url (str): Base URL of the Atlas API
            api_key (str, optional): API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def get_suggestion(self, model_name: str, context: Dict[str, Any], prompt_type: str = 'general') -> Dict[str, Any]:
        """
        Get context-aware suggestion from AI model.
        
        Args:
            model_name (str): Name of the AI model to use
            context (dict): Context information including user input
            prompt_type (str): Type of suggestion prompt (default: "general")
        
        Returns:
            dict: Response containing suggestion text or error message
        """
        payload = {
            'model_name': model_name,
            'context': context,
            'prompt_type': prompt_type
        }
        response = requests.post(f'{self.base_url}/suggestion', json=payload, headers=self.headers)
        return response.json()
    
    def automate_task(self, model_name: str, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automate a task using AI model based on natural language description.
        
        Args:
            model_name (str): Name of the AI model to use
            task_description (str): Natural language description of the task
            context (dict, optional): Context information for the task
        
        Returns:
            dict: Response containing automation plan or error message
        """
        payload = {
            'model_name': model_name,
            'task_description': task_description,
            'context': context or {}
        }
        response = requests.post(f'{self.base_url}/automate', json=payload, headers=self.headers)
        return response.json()
