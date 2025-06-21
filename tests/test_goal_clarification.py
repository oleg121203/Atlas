import json
import unittest
from unittest.mock import MagicMock, patch

from agents.master_agent import MasterAgent
from utils.llm_manager import LLMManager, LLMResponse


class TestGoalClarification(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_agent_manager = MagicMock()
        self.mock_memory_manager = MagicMock()
        self.mock_context_engine = MagicMock()
        self.mock_status_callback = MagicMock()
        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            agent_manager=self.mock_agent_manager,
            memory_manager=self.mock_memory_manager,
            context_awareness_engine=self.mock_memory_manager,
            status_callback=self.mock_status_callback,
        )
        # Ensure status_callback is set to our mock from the beginning
        self.master_agent.status_callback = self.mock_status_callback

    def test_clear_goal_does_not_trigger_clarification(self):
        """Verify that a clear, unambiguous goal proceeds without clarification."""
        clear_goal = "Take a screenshot of the entire screen."
        #Mock the LLM to return a non-ambiguous response
        mock_response = LLMResponse(response_text=json.dumps({"is_ambiguous": False, "question": ""}), model="", prompt_tokens=0, completion_tokens=0, total_tokens=0)
        self.mock_llm_manager.chat.return_value = mock_response

        #Ensure the agent is running
        self.master_agent.is_running = True

        #Debug: Print agent state before run_once
        print(f"Agent state before run_once - is_running: {self.master_agent.is_running}, is_paused: {self.master_agent.is_paused}")

        #Mock the execution to prevent further processing
        with patch.object(self.master_agent, "_execute_objective_with_retries", return_value=None) as mock_execute:
            self.master_agent.run_once(clear_goal)

            #Assert that clarification was NOT requested
            self.assertFalse(self.master_agent.is_clarifying)
            self.assertIsNone(self.master_agent.clarification_question)

            #Debug: Print all status callback calls
            print("Status Callback Calls:")
            for call in self.mock_status_callback.call_args_list:
                print(f"Call: {call[0][0]}")

            #Check that the status callback for clarification was not called
            clarification_call_found = any(
                call[0][0].get("type") == "request_clarification"
                for call in self.mock_status_callback.call_args_list
            )
            self.assertFalse(clarification_call_found, "Clarification should not be requested for a clear goal.")
            mock_execute.assert_called_once_with(clear_goal)

    def test_ambiguous_goal_triggers_clarification(self):
        """Verify that an ambiguous goal correctly triggers the clarification process."""
        ambiguous_goal = "Process the document."
        clarification_question = "Which document do you mean, and what does 'process' entail?"
        #Mock the LLM to return an ambiguous response
        mock_response = LLMResponse(response_text=json.dumps({"is_ambiguous": True, "question": clarification_question}), model="", prompt_tokens=0, completion_tokens=0, total_tokens=0)
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
        ambiguous_response = LLMResponse(response_text=json.dumps({"is_ambiguous": True, "question": "Which file?"}), model="", prompt_tokens=0, completion_tokens=0, total_tokens=0)
        self.mock_llm_manager.chat.return_value = ambiguous_response

        self.master_agent.is_running = True
        self.master_agent.goals = [ambiguous_goal]

        #Run to the point of asking for clarification
        with patch.object(self.master_agent, "pause", lambda: None): #Prevent real pausing
            self.master_agent.run_once(ambiguous_goal)

        #Update mock to return non-ambiguous response for the clarified goal before providing clarification
        clear_response = LLMResponse(response_text=json.dumps({"is_ambiguous": False, "question": ""}), model="", prompt_tokens=0, completion_tokens=0, total_tokens=0)
        self.mock_llm_manager.chat.return_value = clear_response

        #Mock execution to check if it's called with the new goal, applying mock before provide_clarification
        with patch.object(self.master_agent, "_execute_objective_with_retries", return_value=None) as mock_execute:
            #Manually provide clarification
            self.master_agent.provide_clarification(user_clarification)

            #Assert state after clarification
            self.assertFalse(self.master_agent.is_clarifying)
            self.assertFalse(self.master_agent.is_paused)
            self.assertEqual(self.master_agent.goals[-1], clarified_goal)

            #Verify that the agent attempts to execute the now-clarified goal
            mock_execute.assert_called_with(clarified_goal)


if __name__ == "__main__":
    unittest.main()
