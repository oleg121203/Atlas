import re
from typing import Dict, Any, Tuple
import logging

class TaskRecognizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = {
            'browser': [
                r'зайди в.*браузер',
                r'відкрий.*браузер',
                r'найди.*веб',
                r'перейди.*сайт',
                r'відкрий.*сайт',
                r'відкрий.*сторінку',
                r'перейди на.*сторінку'
            ],
            'email': [
                r'знайди.*листи',
                r'перевір.*почту',
                r'пошук.*email',
                r'виведи.*лістів',
                r'знайди.*повідомлення',
                r'перевір.*повідомлення'
            ],
            'security': [
                r'безпека.*екаунта',
                r'безпека.*акаунта',
                r'безпека.*профілю',
                r'зміни.*пароль',
                r'зміни.*логін'
            ]
        }

    def recognize_task_type(self, task: str) -> Tuple[str, Dict[str, Any]]:
        """Recognize task type and extract parameters."""
        task_type = 'unknown'
        params = {}
        
        # Check for browser patterns
        if self._matches_patterns(task, self.patterns['browser']):
            task_type = 'browser'
            params = self._extract_browser_params(task)
        
        # Check for email patterns
        if self._matches_patterns(task, self.patterns['email']):
            task_type = 'email'
            params = self._extract_email_params(task)
        
        # Check for security patterns
        if self._matches_patterns(task, self.patterns['security']):
            params['security'] = True
            
        return task_type, params

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern."""
        return any(re.search(pattern, text.lower()) for pattern in patterns)

    def _extract_browser_params(self, task: str) -> Dict[str, Any]:
        """Extract parameters for browser tasks."""
        params = {}
        
        # Extract URL or site name
        url_match = re.search(r'відкрий|зайди\s+(.+)', task.lower())
        if url_match:
            params['url'] = url_match.group(1).strip()
            
        # Extract browser name
        browser_match = re.search(r'в.*браузер\s+(.+)', task.lower())
        if browser_match:
            params['browser'] = browser_match.group(1).strip()
            
        return params

    def _extract_email_params(self, task: str) -> Dict[str, Any]:
        """Extract parameters for email tasks."""
        params = {}
        
        # Extract search terms
        search_match = re.search(r'знайди|перевір\s+(.+)', task.lower())
        if search_match:
            params['search_terms'] = search_match.group(1).strip()
            
        # Extract time range
        time_match = re.search(r'за\s+(\d+)\s+дні|за\s+(\d+)\s+годин|за\s+(\d+)\s+хвилин', task.lower())
        if time_match:
            params['time_range'] = time_match.group(0)
            
        return params

    def extract_subtasks(self, task: str) -> List[str]:
        """Extract subtasks from complex task."""
        # Split by common conjunctions
        subtasks = []
        
        # Split by 'and' or 'та'
        if 'та' in task.lower():
            subtasks.extend([t.strip() for t in task.split('та') if t.strip()])
        elif 'and' in task.lower():
            subtasks.extend([t.strip() for t in task.split('and') if t.strip()])
        
        # Split by 'then' or 'потім'
        if not subtasks and ('потім' in task.lower() or 'then' in task.lower()):
            subtasks.extend([t.strip() for t in task.split('потім') if t.strip()])
            
        # If no subtasks found, return original task
        return subtasks if subtasks else [task]

    def prioritize_tasks(self, tasks: List[str]) -> List[str]:
        """Prioritize tasks based on their type and urgency."""
        priorities = {
            'security': 1,
            'browser': 2,
            'email': 3
        }
        
        def get_priority(task: str) -> int:
            task_type, _ = self.recognize_task_type(task)
            return priorities.get(task_type, 4)
            
        return sorted(tasks, key=get_priority)
