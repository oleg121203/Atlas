from typing import Dict, List, Any, Optional
import json
import os

class ContextualPromptGenerator:
    """Class to generate contextual prompts based on user role, history, and dashboards"""
    
    def __init__(self, user_data_dir: Optional[str] = None):
        """Initialize the contextual prompt generator
        
        Args:
            user_data_dir (Optional[str]): Directory for storing user data and history
        """
        if user_data_dir is None:
            user_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.user_data_dir = user_data_dir
        self.user_roles = self._load_user_roles()
        self.user_history = self._load_user_history()
        self.dashboard_configs = self._load_dashboard_configs()
        
    def _load_user_roles(self) -> Dict[str, Any]:
        """Load user role information
        
        Returns:
            Dict[str, Any]: User role data
        """
        roles_file = os.path.join(self.user_data_dir, "user_roles.json")
        try:
            if os.path.exists(roles_file):
                with open(roles_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading user roles: {e}")
        return {"default_role": {"name": "User", "permissions": ["create_workflow", "edit_workflow"], "preferences": {}}}
        
    def _load_user_history(self) -> List[Dict[str, Any]]:
        """Load user workflow creation history
        
        Returns:
            List[Dict[str, Any]]: List of historical workflow data
        """
        history_file = os.path.join(self.user_data_dir, "user_history.json")
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading user history: {e}")
        return []
        
    def _load_dashboard_configs(self) -> Dict[str, Any]:
        """Load active dashboard configurations
        
        Returns:
            Dict[str, Any]: Dashboard configuration data
        """
        dashboard_file = os.path.join(self.user_data_dir, "dashboard_configs.json")
        try:
            if os.path.exists(dashboard_file):
                with open(dashboard_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading dashboard configs: {e}")
        return {"active_dashboards": [], "metrics": {}}
        
    def generate_contextual_prompt(self, base_prompt: str, user_id: str = "default", context_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a contextual prompt based on user role, history, and dashboards
        
        Args:
            base_prompt (str): Base natural language prompt from user
            user_id (str): Identifier for the user to load specific context
            context_data (Optional[Dict[str, Any]]): Additional context data if available
            
        Returns:
            str: Enhanced prompt with contextual information
        """
        # Get user role information
        user_role = self.user_roles.get(user_id, self.user_roles.get("default_role", {}))
        role_name = user_role.get("name", "User")
        role_preferences = user_role.get("preferences", {})
        
        # Analyze user history for patterns
        user_history = [h for h in self.user_history if h.get("user_id") == user_id]
        common_actions = []
        if user_history:
            actions = [step.get("action", "") for h in user_history for step in h.get("workflow", {}).get("steps", [])]
            action_counts = {action: actions.count(action) for action in set(actions) if action}
            common_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
        # Get active dashboard information
        active_dashboards = self.dashboard_configs.get("active_dashboards", [])
        dashboard_metrics = self.dashboard_configs.get("metrics", {})
        
        # Construct contextual prefix
        contextual_prefix = f"You are assisting a {role_name} with workflow creation. "
        if role_preferences:
            pref_str = ", ".join([f"{k}={v}" for k, v in role_preferences.items() if k in ["style", "complexity", "domain"]])
            if pref_str:
                contextual_prefix += f"User preferences: {pref_str}. "
                
        if common_actions:
            actions_str = ", ".join([f"{action} ({count} times)" for action, count in common_actions])
            contextual_prefix += f"Frequently used actions: {actions_str}. "
            
        if active_dashboards:
            dashboards_str = ", ".join(active_dashboards)
            contextual_prefix += f"Active dashboards: {dashboards_str}. "
            
        if context_data and context_data.get("current_task"):
            contextual_prefix += f"Current user task: {context_data['current_task']}. "
            
        # Combine context with base prompt
        return contextual_prefix + "User request: " + base_prompt
