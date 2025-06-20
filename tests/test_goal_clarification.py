import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import json

#Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.master_agent import MasterAgent
from agents.llm_manager import LLMManager, LLMResult


class TestGoalClarification(unittest.TestCase):

    def setUp(self):
        """Set up a mock environment for each test."""
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_agent_manager = MagicMock()
        self.mock_memory_manager = MagicMock()
        self.mock_status_callback = MagicMock()

        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            agent_manager=self.mock_agent_manager,
            memory_manager=self.mock_memory_manager,
            status_callback=self.mock_status_callback
        )

    def test_clear_goal_does_not_trigger_clarification(self):
        """Verify that a clear, unambiguous goal proceeds without clarification."""
        clear_goal = "Take a screenshot of the entire screen."
        #Mock the LLM to return a non-ambiguous response
        mock_response = LLMResult(response_text=json.dumps({"is_ambiguous": False, "question": ""}), tool_calls=None)
        self.mock_llm_manager.chat.return_value = mock_response

        #Mock the decomposition to prevent further execution
        with patch.object(self.master_agent, '_decompose_goal', return_value=[clear_goal]) as mock_decompose:
            self.master_agent.run_once(clear_goal)

            #Assert that clarification was NOT requested
            self.assertFalse(self.master_agent.is_clarifying)
            self.assertIsNone(self.master_agent.clarification_question)
            self.mock_status_callback.assert_any_call({"type": "info", "content": "Checking goal for ambiguity..."})
            
            #Check that the status callback for clarification was not called
            clarification_call_found = any(
                call.args[0].get("type") == "request_clarification"
                for call in self.mock_status_callback.call_args_list
            )
            self.assertFalse(clarification_call_found, "Clarification should not be requested for a clear goal.")
            mock_decompose.assert_called_once_with(clear_goal)

    def test_ambiguous_goal_triggers_clarification(self):
        """Verify that an ambiguous goal correctly triggers the clarification process."""
        ambiguous_goal = "Process the document."
        clarification_question = "Which document do you mean, and what does 'process' entail?"
        #Mock the LLM to return an ambiguous response
        mock_response = LLMResult(response_text=json.dumps({"is_ambiguous": True, "question": clarification_question}), tool_calls=None)
        self.mock_llm_manager.chat.return_value = mock_response

        #We don't need to mock decomposition as it should pause before that
        self.master_agent.is_running = True #Simulate running state
        self.master_agent.run_once(ambiguous_goal)

        #Assert that clarification was requested
        self.assertTrue(self.master_agent.is_clarifying)
        self.assertEqual(self.master_agent.clarification_question, clarification_question)
        self.assertTrue(self.master_agent.is_paused)
        self.mock_status_callback.assert_any_call({"type": "request_clarification", "content": clarification_question})

    def test_agent_resumes_with_clarified_goal(self):
        """Verify that the agent correctly updates the goal and resumes after clarification."""
        ambiguous_goal = "Analyze the file."
        user_clarification = "I want you to summarize the text content of '/path/to/my/file.txt'"
        clarified_goal = f"{ambiguous_goal} (User clarification: {user_clarification})"

        #Initial ambiguous response
        ambiguous_response = LLMResult(response_text=json.dumps({"is_ambiguous": True, "question": "Which file?"}), tool_calls=None)
        self.mock_llm_manager.chat.return_value = ambiguous_response

        self.master_agent.is_running = True
        self.master_agent.goals = [ambiguous_goal]

        #Run to the point of asking for clarification
        #We need to run this in a way that doesn't block the test
        with patch.object(self.master_agent, 'pause', lambda: None): #Prevent real pausing
            self.master_agent.run_once(ambiguous_goal)

        #Manually provide clarification
        self.master_agent.provide_clarification(user_clarification)

        #Assert state after clarification
        self.assertFalse(self.master_agent.is_clarifying)
        self.assertFalse(self.master_agent.is_paused)
        self.assertEqual(self.master_agent.goals[-1], clarified_goal)

        #Now, mock the next step (ambiguity check for the *new* goal) to be clear
        clear_response = LLMResult(response_text=json.dumps({"is_ambiguous": False, "question": ""}), tool_calls=None)
        self.mock_llm_manager.chat.return_value = clear_response

        #Mock decomposition to check if it's called with the new goal
        with patch.object(self.master_agent, '_decompose_goal', return_value=[clarified_goal]) as mock_decompose:
            #The execution continues inside run_once after the pause loop
            #To simulate this, we can't call run_once again. We need to check the state.
            #This part is tricky to test without threading. Let's check the goal was updated.
            self.assertEqual(self.master_agent.goals[-1], clarified_goal)


if __name__ == '__main__':
    unittest.main()
