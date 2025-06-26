"""Team Management Module for Atlas

This module provides functionality for managing teams, assigning tasks, and tracking progress.
"""

import json
import time
from typing import Dict, List, Optional

from core.config import Config

class TeamManager:
    def __init__(self):
        self.teams: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self._load_data()

    def _load_data(self):
        """Load team, user, and task data from storage."""
        try:
            with open('team_data.json', 'r') as f:
                data = json.load(f)
                self.teams = data.get('teams', {})
                self.users = data.get('users', {})
                self.tasks = data.get('tasks', {})
        except FileNotFoundError:
            # Initialize with default data if file doesn\'t exist
            self.teams = {
                'default': {
                    'id': 'default',
                    'name': 'Default Team',
                    'members': [],
                    'admins': [],
                    'tasks': []
                }
            }
            self.users = {}
            self.tasks = {}
            self._save_data()

    def _save_data(self):
        """Save team, user, and task data to storage."""
        data = {
            'teams': self.teams,
            'users': self.users,
            'tasks': self.tasks
        }
        with open('team_data.json', 'w') as f:
            json.dump(data, f)

    def create_team(self, team_name: str, admin_id: str) -> str:
        """Create a new team with the specified admin."""
        team_id = f"team_{hash(team_name)}_{int(time.time())}"
        self.teams[team_id] = {
            'id': team_id,
            'name': team_name,
            'members': [admin_id],
            'admins': [admin_id],
            'tasks': []
        }
        self._save_data()
        return team_id

    def add_user_to_team(self, team_id: str, user_id: str, is_admin: bool = False) -> bool:
        """Add a user to a team, optionally as an admin."""
        if team_id not in self.teams:
            return False
        if user_id not in self.teams[team_id]['members']:
            self.teams[team_id]['members'].append(user_id)
        if is_admin and user_id not in self.teams[team_id]['admins']:
            self.teams[team_id]['admins'].append(user_id)
        self._save_data()
        return True

    def remove_user_from_team(self, team_id: str, user_id: str) -> bool:
        """Remove a user from a team."""
        if team_id not in self.teams:
            return False
        if user_id in self.teams[team_id]['members']:
            self.teams[team_id]['members'].remove(user_id)
        if user_id in self.teams[team_id]['admins']:
            self.teams[team_id]['admins'].remove(user_id)
        self._save_data()
        return True

    def assign_task_to_team(self, team_id: str, task_id: str) -> bool:
        """Assign a task to a team."""
        if team_id not in self.teams or task_id not in self.tasks:
            return False
        if task_id not in self.teams[team_id]['tasks']:
            self.teams[team_id]['tasks'].append(task_id)
        self.tasks[task_id]['team_id'] = team_id
        self._save_data()
        return True

    def create_task(self, title: str, description: str, creator_id: str) -> str:
        """Create a new task."""
        task_id = f"task_{hash(title)}_{int(time.time())}"
        self.tasks[task_id] = {
            'id': task_id,
            'title': title,
            'description': description,
            'status': 'open',
            'creator_id': creator_id,
            'team_id': None,
            'assignee_id': None,
            'created': time.time(),
            'updated': time.time(),
            'progress': 0
        }
        self._save_data()
        return task_id

    def assign_task_to_user(self, task_id: str, user_id: str) -> bool:
        """Assign a task to a specific user within a team."""
        if task_id not in self.tasks:
            return False
        self.tasks[task_id]['assignee_id'] = user_id
        self.tasks[task_id]['updated'] = time.time()
        self._save_data()
        return True

    def update_task_status(self, task_id: str, status: str, progress: int) -> bool:
        """Update the status and progress of a task."""
        if task_id not in self.tasks:
            return False
        self.tasks[task_id]['status'] = status
        self.tasks[task_id]['progress'] = progress
        self.tasks[task_id]['updated'] = time.time()
        self._save_data()
        return True

    def get_team_tasks(self, team_id: str) -> List[Dict]:
        """Get all tasks assigned to a team."""
        if team_id not in self.teams:
            return []
        return [self.tasks[task_id] for task_id in self.teams[team_id]['tasks'] if task_id in self.tasks]

    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """Get all tasks assigned to a user."""
        return [task for task in self.tasks.values() if task['assignee_id'] == user_id]

    def get_team_progress(self, team_id: str) -> Dict:
        """Calculate progress metrics for a team."""
        if team_id not in self.teams:
            return {'total_tasks': 0, 'completed_tasks': 0, 'progress_percent': 0}
        
        tasks = self.get_team_tasks(team_id)
        if not tasks:
            return {'total_tasks': 0, 'completed_tasks': 0, 'progress_percent': 0}
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task['status'] == 'completed')
        progress_percent = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_percent': progress_percent
        }

    def add_user(self, user_id: str, name: str, email: str) -> bool:
        """Add a user to the system."""
        if user_id in self.users:
            return False
        self.users[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'teams': []
        }
        self._save_data()
        return True

    def get_user_teams(self, user_id: str) -> List[Dict]:
        """Get all teams a user belongs to."""
        if user_id not in self.users:
            return []
        return [self.teams[team_id] for team_id in self.teams if user_id in self.teams[team_id]['members']]
