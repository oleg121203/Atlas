import os
import json
from typing import Dict, List, Any
from intelligence.llm import AtlasLLM
from workflow.workflow_validator import WorkflowValidator
from workflow.workflow_feedback import WorkflowFeedback
from workflow.contextual_prompts import ContextualPromptGenerator

class NLWorkflowGenerator:
    """Class to convert natural language input into executable workflow structures"""
    
    def __init__(self, model_name: str = "atlas-workflow-v1"):
        """Initialize the natural language to workflow generator
        
        Args:
            model_name (str): Name of the LLM model to use for workflow generation
        """
        self.llm = AtlasLLM(model_name=model_name)
        self.workflow_patterns = self._load_workflow_patterns()
        self.user_history = self._load_user_history()
        self.validator = WorkflowValidator()
        self.feedback = WorkflowFeedback()
        self.prompt_generator = ContextualPromptGenerator()
        
    def _load_workflow_patterns(self) -> Dict[str, Any]:
        """Load existing workflow patterns from storage
        
        Returns:
            Dict[str, Any]: Dictionary of workflow pattern templates
        """
        pattern_file = os.path.join(os.path.dirname(__file__), "..", "workflow_patterns.json")
        try:
            with open(pattern_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workflow patterns: {e}")
            return {}
            
    def _load_user_history(self) -> List[Dict[str, Any]]:
        """Load user workflow history for context
        
        Returns:
            List[Dict[str, Any]]: List of historical user workflows
        """
        history_file = os.path.join(os.path.dirname(__file__), "..", "data", "user_workflow_history.json")
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            # If file doesn't exist or is corrupted, return empty list
            return []
            
    def fine_tune_model(self) -> bool:
        """Fine-tune the LLM with workflow patterns and user history
        
        Returns:
            bool: True if fine-tuning was successful, False otherwise
        """
        try:
            training_data = self._prepare_training_data()
            self.llm.fine_tune(training_data)
            return True
        except Exception as e:
            print(f"Error during fine-tuning: {e}")
            return False
            
    def _prepare_training_data(self) -> List[Dict[str, str]]:
        """Prepare training data for fine-tuning from patterns and history
        
        Returns:
            List[Dict[str, str]]: List of training examples with prompt and completion
        """
        training_data = []
        
        # Add workflow patterns as training examples
        for pattern_name, pattern_data in self.workflow_patterns.items():
            prompt = f"Create a workflow for {pattern_name}"
            completion = json.dumps(pattern_data)
            training_data.append({"prompt": prompt, "completion": completion})
            
        # Add user history as training examples
        for history_item in self.user_history:
            if "description" in history_item and "workflow" in history_item:
                prompt = history_item["description"]
                completion = json.dumps(history_item["workflow"])
                training_data.append({"prompt": prompt, "completion": completion})
                
        return training_data
        
    def generate_workflow(self, nl_input: str, user_id: str = "default", context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert natural language input to a structured workflow
        
        Args:
            nl_input (str): Natural language description of desired workflow
            user_id (str): Identifier for user-specific context
            context_data (Dict[str, Any]): Additional context data if available
            
        Returns:
            Dict[str, Any]: Structured workflow definition
        """
        try:
            base_prompt = self._construct_prompt(nl_input)
            contextual_prompt = self.prompt_generator.generate_contextual_prompt(base_prompt, user_id, context_data)
            response = self.llm.generate(contextual_prompt)
            workflow = json.loads(response)
            is_valid, errors = self.validator.validate_workflow(workflow)
            if not is_valid:
                print(f"Generated workflow validation failed: {errors}")
                # Attempt to fix or return empty on failure
                return {}
            # Record initial feedback (could be updated by user later)
            self.feedback.add_feedback(workflow, nl_input, 3, "Auto-generated initial feedback")
            return workflow
        except Exception as e:
            print(f"Error generating workflow: {e}")
            return {}
            
    def _construct_prompt(self, nl_input: str) -> str:
        """Construct a detailed prompt for the LLM based on user input
        
        Args:
            nl_input (str): Natural language input from user
            
        Returns:
            str: Formatted prompt for LLM
        """
        return f"""
        You are an expert in workflow automation. Convert the following natural language request
        into a structured JSON workflow definition with steps, dependencies, and parameters.
        
        User Request: {nl_input}
        
        Respond only with valid JSON representing the workflow structure.
        """
