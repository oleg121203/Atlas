from typing import Dict, List, Any, Optional
import json
import os

class WorkflowFeedback:
    """Class to manage feedback for generated workflows to improve future generations"""
    
    def __init__(self, feedback_file: Optional[str] = None):
        """Initialize the workflow feedback system
        
        Args:
            feedback_file (Optional[str]): Path to file for storing feedback data
        """
        if feedback_file is None:
            feedback_file = os.path.join(os.path.dirname(__file__), "..", "data", "workflow_feedback.json")
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
        
    def _load_feedback(self) -> List[Dict[str, Any]]:
        """Load existing feedback data from file
        
        Returns:
            List[Dict[str, Any]]: List of feedback entries
        """
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading feedback data: {e}")
        return []
        
    def _save_feedback(self) -> None:
        """Save feedback data to file"""
        try:
            os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback data: {e}")
            
    def add_feedback(self, workflow: Dict[str, Any], user_input: str, rating: int, comments: str = "", modifications: Optional[Dict[str, Any]] = None) -> None:
        """Add user feedback for a generated workflow
        
        Args:
            workflow (Dict[str, Any]): The generated workflow structure
            user_input (str): The natural language input that generated this workflow
            rating (int): User rating of the workflow (1-5)
            comments (str): Additional user comments about the workflow
            modifications (Optional[Dict[str, Any]]): User modifications to the workflow, if any
        """
        feedback_entry = {
            "user_input": user_input,
            "original_workflow": workflow,
            "rating": max(1, min(5, rating)),  # Ensure rating is between 1 and 5
            "comments": comments,
            "modifications": modifications if modifications else {},
            "timestamp": str(__import__('datetime').datetime.now())
        }
        self.feedback_data.append(feedback_entry)
        self._save_feedback()
        print(f"Feedback recorded with rating {rating}/5")
        
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Generate a summary of feedback for analysis
        
        Returns:
            Dict[str, Any]: Summary statistics and insights from feedback
        """
        total_entries = len(self.feedback_data)
        if total_entries == 0:
            return {"total": 0, "average_rating": 0, "common_issues": []}
            
        total_rating = sum(entry["rating"] for entry in self.feedback_data)
        avg_rating = total_rating / total_entries
        
        # Analyze comments for common themes (simple keyword counting for now)
        common_issues = []
        all_comments = " ".join(entry["comments"].lower() for entry in self.feedback_data if entry["comments"])
        keywords = ["missing", "error", "wrong", "incorrect", "broken", "fail", "bad"]
        for word in keywords:
            if word in all_comments:
                count = all_comments.count(word)
                if count > total_entries // 3:  # Mentioned in at least 1/3 of feedback
                    common_issues.append(f"'{word}' mentioned {count} times")
                    
        return {
            "total": total_entries,
            "average_rating": round(avg_rating, 2),
            "common_issues": common_issues,
            "modification_rate": round(sum(1 for entry in self.feedback_data if entry["modifications"]) / total_entries * 100, 1)
        }
