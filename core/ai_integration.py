"""
AI Integration Module for Atlas

This module provides integration with AI models for natural language processing,
context-aware suggestions, and automation capabilities.
"""

import os
import json
from typing import Optional, Dict, List, Any
import logging
from pathlib import Path
import time
import statistics

import requests

from core.logging import get_logger

try:
    from core.config import load_config
except ImportError:
    def load_config(config_path: Optional[str] = None, environment: str = "dev") -> Dict[str, Any]:
        print("Config loading not available, using default configuration.")
        return {}

# Set up logging
logger = get_logger("AIIntegration")

# Performance metrics storage
_performance_metrics = {
    'inference_times': {},
    'success_rates': {},
    'error_counts': {}
}

class AIIntegrationError(Exception):
    """Custom exception for AI integration errors."""
    pass

class AIModelManager:
    """Manages AI model integration and inference for Atlas."""
    
    _instance = None
    
    def __new__(cls, config_path: Optional[str] = None, environment: str = "dev"):
        """
        Singleton pattern to ensure only one instance of AIModelManager exists.
        
        Args:
            config_path: Path to configuration file, if any
            environment: Target environment for AI integration
        
        Returns:
            AIModelManager: Singleton instance of the manager
        """
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "dev"):
        """
        Initialize the AIModelManager with configuration and environment.
        
        Args:
            config_path: Path to configuration file, if any
            environment: Target environment for AI integration (dev, staging, prod)
        """
        if not hasattr(self, '_initialized') or not self._initialized:
            self.environment = environment.lower()
            self.config = load_config(config_path, environment=self.environment)
            self.models: Dict[str, Any] = {}
            self.default_models: Dict[str, Any] = self.config.get("ai_models", {})
            self.storage_path = Path(self.config.get("ai_models_storage", "config/ai_models.json"))
            self.api_keys: Dict[str, str] = self.config.get("api_keys", {})
            self.setup_logging()
            self.load_models()
            self._initialized = True
            logger.info("AIModelManager initialized for environment: %s", self.environment)
    
    def setup_logging(self) -> None:
        """Set up logging configuration for AI integration."""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_file = self.config.get("logging", {}).get("file", "atlas_ai_integration.log")
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logger.info("Logging configured for AIModelManager")
    
    def load_models(self) -> None:
        """Load AI model configurations from storage or use defaults from config."""
        logger.info("Loading AI model configurations")
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    stored_models = json.load(f)
                    # Merge stored models with defaults, giving precedence to stored
                    self.models = {**self.default_models, **stored_models}
                    logger.info("Loaded AI models from storage: %s", self.storage_path)
            else:
                # If no storage file exists, use the defaults from config
                self.models = self.default_models.copy()
                logger.info("No stored models found, using default AI models")
            
            # Apply environment-specific overrides if they exist
            env_overrides = self.config.get("ai_model_overrides", {}).get(self.environment, {})
            if env_overrides:
                self.models.update(env_overrides)
                logger.info("Applied environment-specific overrides for: %s", self.environment)
        except Exception as e:
            logger.error("Error loading AI models: %s", str(e), exc_info=True)
            # Fall back to default models on error
            self.models = self.default_models.copy()
            logger.info("Falling back to default AI models due to load error")
    
    def save_models(self) -> None:
        """Save current AI model configurations to storage."""
        logger.info("Saving AI model configurations to storage: %s", self.storage_path)
        try:
            # Ensure storage directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w") as f:
                json.dump(self.models, f, indent=2)
            logger.info("AI model configurations saved successfully")
        except Exception as e:
            logger.error("Error saving AI model configurations: %s", str(e), exc_info=True)
            raise AIIntegrationError(f"Failed to save AI model configurations: {str(e)}")
    
    def get_model(self, model_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific AI model.
        
        Args:
            model_name: Name of the AI model to retrieve
        
        Returns:
            Optional[Dict]: Configuration of the AI model or None if not found
        """
        model_config = self.models.get(model_name)
        if model_config:
            logger.debug("Retrieved configuration for model: %s", model_name)
        else:
            logger.warning("Model %s not found", model_name)
        return model_config
    
    def set_model(self, model_name: str, config: Dict) -> None:
        """
        Set configuration for an AI model and save to storage.
        
        Args:
            model_name: Name of the AI model to set
            config: Configuration dictionary for the model
        """
        logger.info("Setting configuration for AI model %s", model_name)
        self.models[model_name] = config
        self.save_models()
    
    def infer(self, model_name: str, input_data: Any, context: Optional[Dict] = None) -> Any:
        """
        Perform inference using the specified AI model.
        
        Args:
            model_name: Name of the AI model to use for inference
            input_data: Input data for the model
            context: Optional context information for context-aware processing
        
        Returns:
            Any: Inference results
        """
        logger.info("Performing inference with model: %s", model_name)
        start_time = time.time()
        model_config = self.get_model(model_name)
        if not model_config:
            raise AIIntegrationError(f"Model {model_name} not found")
        
        provider = model_config.get("provider", "")
        try:
            if provider.lower() == "openai":
                result = self._infer_openai(model_config, input_data, context)
                _record_performance(model_name, start_time, True)
                return result
            elif provider.lower() == "anthropic":
                result = self._infer_anthropic(model_config, input_data, context)
                _record_performance(model_name, start_time, True)
                return result
            elif provider.lower() == "local":
                result = self._infer_local(model_config, input_data, context)
                _record_performance(model_name, start_time, True)
                return result
            else:
                raise AIIntegrationError(f"Unsupported provider {provider} for model {model_name}")
        except Exception as e:
            _record_performance(model_name, start_time, False, str(e))
            raise
    
    def _infer_openai(self, model_config: Dict, input_data: Any, context: Optional[Dict] = None) -> Any:
        """
        Perform inference using OpenAI API.
        
        Args:
            model_config: Configuration for the OpenAI model
            input_data: Input data for the model
            context: Optional context information
        
        Returns:
            Any: Inference results from OpenAI
        """
        logger.debug("Using OpenAI provider for inference")
        try:
            api_key = self.api_keys.get("openai", os.environ.get("OPENAI_API_KEY", ""))
            if not api_key:
                raise AIIntegrationError("OpenAI API key not found")
            
            endpoint = model_config.get("endpoint", "https://api.openai.com/v1/chat/completions")
            model_id = model_config.get("model_id", "gpt-3.5-turbo")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if context and context.get("history"):
                messages.extend(context.get("history", []))
            
            if isinstance(input_data, str):
                messages.append({"role": "user", "content": input_data})
            else:
                messages.append({"role": "user", "content": json.dumps(input_data)})
            
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": model_config.get("temperature", 0.7),
                "max_tokens": model_config.get("max_tokens", 2048)
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            logger.info("OpenAI inference completed successfully")
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error("Error in OpenAI inference: %s", str(e), exc_info=True)
            raise AIIntegrationError(f"OpenAI inference failed: {str(e)}")
    
    def _infer_anthropic(self, model_config: Dict, input_data: Any, context: Optional[Dict] = None) -> Any:
        """
        Perform inference using Anthropic API.
        
        Args:
            model_config: Configuration for the Anthropic model
            input_data: Input data for the model
            context: Optional context information
        
        Returns:
            Any: Inference results from Anthropic
        """
        logger.debug("Using Anthropic provider for inference")
        try:
            api_key = self.api_keys.get("anthropic", os.environ.get("ANTHROPIC_API_KEY", ""))
            if not api_key:
                raise AIIntegrationError("Anthropic API key not found")
            
            endpoint = model_config.get("endpoint", "https://api.anthropic.com/v1/messages")
            model_id = model_config.get("model_id", "claude-3-opus-20240229")
            
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            messages = []
            if context and context.get("history"):
                messages.extend(context.get("history", []))
            
            if isinstance(input_data, str):
                messages.append({"role": "user", "content": input_data})
            else:
                messages.append({"role": "user", "content": json.dumps(input_data)})
            
            payload = {
                "model": model_id,
                "messages": messages,
                "max_tokens": model_config.get("max_tokens", 2048),
                "temperature": model_config.get("temperature", 0.7)
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            logger.info("Anthropic inference completed successfully")
            return result.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error("Error in Anthropic inference: %s", str(e), exc_info=True)
            raise AIIntegrationError(f"Anthropic inference failed: {str(e)}")
    
    def _infer_local(self, model_config: Dict, input_data: Any, context: Optional[Dict] = None) -> Any:
        """
        Perform inference using a local AI model.
        
        Args:
            model_config: Configuration for the local model
            input_data: Input data for the model
            context: Optional context information
        
        Returns:
            Any: Inference results from local model
        """
        logger.debug("Using local provider for inference")
        try:
            # Placeholder for local model inference
            # This would require additional dependencies and setup
            logger.warning("Local AI model inference not implemented yet")
            return "Local AI model inference is not implemented in this version of Atlas."
        except Exception as e:
            logger.error("Error in local model inference: %s", str(e), exc_info=True)
            raise AIIntegrationError(f"Local model inference failed: {str(e)}")
    
    def get_suggestion(self, model_name: str, context: Dict, prompt_type: str = "general") -> str:
        """
        Get context-aware suggestion based on user input and history.
        
        Args:
            model_name: Name of the AI model to use for suggestion
            context: Context information including user input and history
            prompt_type: Type of suggestion prompt (general, code, task, etc.)
        
        Returns:
            str: Suggestion text
        """
        logger.info("Generating suggestion with model: %s, type: %s", model_name, prompt_type)
        model_config = self.get_model(model_name)
        if not model_config:
            raise AIIntegrationError(f"Model {model_name} not found")
        
        # Craft specialized prompt based on type
        if prompt_type == "code":
            input_text = self._craft_code_prompt(context)
        elif prompt_type == "task":
            input_text = self._craft_task_prompt(context)
        else:
            input_text = self._craft_general_prompt(context)
        
        return self.infer(model_name, input_text, context)
    
    def _craft_code_prompt(self, context: Dict) -> str:
        """
        Craft a prompt for code-related suggestions.
        
        Args:
            context: Context information including user input and code context
        
        Returns:
            str: Crafted prompt for code suggestions
        """
        user_input = context.get("user_input", "")
        code_context = context.get("code_context", "")
        
        prompt = f"""You are a highly skilled programming assistant. I am working on some code and need help.
Current code context:
{code_context}

My request: {user_input}

Please provide relevant code suggestions, explanations, or solutions. Make sure your response is concise and directly addresses my request."""
        return prompt
    
    def _craft_task_prompt(self, context: Dict) -> str:
        """
        Craft a prompt for task-related suggestions.
        
        Args:
            context: Context information including user input and task context
        
        Returns:
            str: Crafted prompt for task suggestions
        """
        user_input = context.get("user_input", "")
        task_context = context.get("task_context", "")
        
        prompt = f"""You are a productivity assistant helping with task management.
Current tasks or context:
{task_context}

My request: {user_input}

Please provide suggestions for task prioritization, organization, or completion strategies. Keep your response focused and practical."""
        return prompt
    
    def _craft_general_prompt(self, context: Dict) -> str:
        """
        Craft a general purpose prompt for suggestions.
        
        Args:
            context: Context information including user input
        
        Returns:
            str: Crafted general purpose prompt
        """
        user_input = context.get("user_input", "")
        
        prompt = f"""You are a helpful AI assistant. I have a question or request.
My request: {user_input}

Please provide a clear and concise response that directly addresses my request."""
        return prompt
    
    def automate_task(self, model_name: str, task_description: str, context: Optional[Dict] = None) -> Dict:
        """
        Automate a task based on natural language description.
        
        Args:
            model_name: Name of the AI model to use for task automation
            task_description: Natural language description of the task to automate
            context: Optional context information for the task
        
        Returns:
            Dict: Automation plan with steps and expected outcomes
        """
        logger.info("Automating task with model: %s", model_name)
        model_config = self.get_model(model_name)
        if not model_config:
            raise AIIntegrationError(f"Model {model_name} not found")
        
        prompt = f"""You are an automation expert. I need to automate a task.
Task description: {task_description}

Please provide a step-by-step plan to automate this task. Include expected outcomes for each step.
Format your response as a JSON object with 'steps' as a list of objects with 'step', 'action', and 'expected_outcome' fields."""
        
        if context:
            prompt += f"""
Additional context:
{json.dumps(context, indent=2)}"""
        
        response = self.infer(model_name, prompt, context)
        try:
            # Attempt to parse response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Could not parse automation response as JSON, returning raw text")
            return {"steps": [], "raw_response": response}

def _record_performance(model_name: str, start_time: float, success: bool, error_message: str = None):
    """
    Record performance metrics for AI model inference.
    
    Args:
        model_name: Name of the AI model
        start_time: Start time of the inference
        success: Whether the inference was successful
        error_message: Error message if inference failed
    """
    duration = time.time() - start_time
    
    # Update inference times
    if model_name not in _performance_metrics['inference_times']:
        _performance_metrics['inference_times'][model_name] = []
    _performance_metrics['inference_times'][model_name].append(duration)
    
    # Update success rates
    if model_name not in _performance_metrics['success_rates']:
        _performance_metrics['success_rates'][model_name] = {'success': 0, 'total': 0}
    _performance_metrics['success_rates'][model_name]['total'] += 1
    if success:
        _performance_metrics['success_rates'][model_name]['success'] += 1
    
    # Update error counts
    if not success:
        if model_name not in _performance_metrics['error_counts']:
            _performance_metrics['error_counts'][model_name] = {}
        error_type = error_message.split(':')[0] if error_message else 'Unknown'
        _performance_metrics['error_counts'][model_name][error_type] = _performance_metrics['error_counts'][model_name].get(error_type, 0) + 1
    
    logger.debug(f"Performance recorded for {model_name}: Duration={duration:.2f}s, Success={success}")

def get_performance_report(model_name: str = None) -> Dict:
    """
    Generate a performance report for AI models.
    
    Args:
        model_name: Optional specific model name to report on
    
    Returns:
        Dict: Performance statistics for the specified model or all models
    """
    report = {}
    models = [model_name] if model_name else _performance_metrics['inference_times'].keys()
    
    for model in models:
        if model in _performance_metrics['inference_times']:
            times = _performance_metrics['inference_times'][model]
            success_data = _performance_metrics['success_rates'].get(model, {'success': 0, 'total': 0})
            success_rate = success_data['success'] / success_data['total'] if success_data['total'] > 0 else 0
            
            report[model] = {
                'average_time': statistics.mean(times) if times else 0,
                'min_time': min(times) if times else 0,
                'max_time': max(times) if times else 0,
                'total_calls': len(times),
                'success_rate': success_rate,
                'errors': _performance_metrics['error_counts'].get(model, {})
            }
    
    return report

def optimize_model_selection(context: Dict) -> str:
    """
    Select the optimal AI model based on context and performance metrics.
    
    Args:
        context: Context information including task type and requirements
    
    Returns:
        str: Name of the optimal model to use
    """
    task_type = context.get('task_type', 'general')
    performance_report = get_performance_report()
    
    # Default model selection logic
    if task_type == 'code':
        preferred_model = 'gpt-4-turbo'  # Known for strong coding capabilities
    elif task_type == 'task_automation':
        preferred_model = 'claude-3-opus'  # Strong in task planning
    else:
        preferred_model = 'gpt-4'
    
    # Adjust based on performance metrics if available
    if performance_report:
        best_model = None
        best_score = -1
        
        for model, metrics in performance_report.items():
            # Calculate a simple performance score (lower time, higher success rate = better)
            score = metrics['success_rate'] / (metrics['average_time'] + 1)  # +1 to avoid division by zero
            if score > best_score:
                best_score = score
                best_model = model
        
        if best_model and best_model != preferred_model:
            logger.info(f"Optimized model selection: Using {best_model} instead of {preferred_model} based on performance")
            return best_model
    
    return preferred_model

# Global function to get the AI model manager instance
def get_ai_model_manager(config_path: Optional[str] = None, environment: str = "dev") -> AIModelManager:
    """
    Get the singleton instance of the AIModelManager.
    
    Args:
        config_path: Path to configuration file, if any
        environment: Target environment for AI integration
    
    Returns:
        AIModelManager: Singleton instance of the AI model manager
    """
    return AIModelManager(config_path=config_path, environment=environment)

# Convenience functions for easy access to AI capabilities
def get_ai_suggestion(model_name: str, context: Dict, prompt_type: str = "general", 
                     config_path: Optional[str] = None, environment: str = "dev") -> str:
    """
    Get context-aware suggestion from AI model.
    
    Args:
        model_name: Name of the AI model to use
        context: Context information including user input
        prompt_type: Type of suggestion prompt (general, code, task, etc.)
        config_path: Path to configuration file, if any
        environment: Target environment for AI integration
    
    Returns:
        str: Suggestion text from AI model
    """
    return get_ai_model_manager(config_path, environment).get_suggestion(model_name, context, prompt_type)

def automate_ai_task(model_name: str, task_description: str, context: Optional[Dict] = None,
                    config_path: Optional[str] = None, environment: str = "dev") -> Dict:
    """
    Automate a task using AI model based on natural language description.
    
    Args:
        model_name: Name of the AI model to use
        task_description: Natural language description of the task
        context: Optional context information for the task
        config_path: Path to configuration file, if any
        environment: Target environment for AI integration
    
    Returns:
        Dict: Automation plan with steps
    """
    return get_ai_model_manager(config_path, environment).automate_task(model_name, task_description, context)
