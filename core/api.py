"""
Public API Module for Atlas

This module defines the RESTful API endpoints for interacting with Atlas functionalities.
"""

import logging
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, Response

from core.logging import get_logger
from core.ai_integration import get_ai_suggestion, automate_ai_task

# Set up logging
logger = get_logger("PublicAPI")

app = Flask(__name__)

@app.route('/api/v1/suggestion', methods=['POST'])
def get_suggestion() -> Response:
    """
    Endpoint to get context-aware suggestions from AI model.
    
    Request Body:
        - model_name (str): Name of the AI model to use
        - context (dict): Context information including user input
        - prompt_type (str, optional): Type of suggestion prompt (default: "general")
    
    Returns:
        - JSON response with suggestion text or error message
    """
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        context = data.get('context', {})
        prompt_type = data.get('prompt_type', 'general')
        
        if not model_name:
            return jsonify({'error': 'model_name is required'}), 400
        
        suggestion = get_ai_suggestion(model_name, context, prompt_type)
        return jsonify({'suggestion': suggestion})
    except Exception as e:
        logger.error(f"Error in get_suggestion endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/automate', methods=['POST'])
def automate_task() -> Response:
    """
    Endpoint to automate a task using AI model based on natural language description.
    
    Request Body:
        - model_name (str): Name of the AI model to use
        - task_description (str): Natural language description of the task
        - context (dict, optional): Context information for the task
    
    Returns:
        - JSON response with automation plan or error message
    """
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        task_description = data.get('task_description')
        context = data.get('context', {})
        
        if not model_name or not task_description:
            return jsonify({'error': 'model_name and task_description are required'}), 400
        
        plan = automate_ai_task(model_name, task_description, context)
        return jsonify({'plan': plan})
    except Exception as e:
        logger.error(f"Error in automate_task endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
