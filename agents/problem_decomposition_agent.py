"""
Defines the Problem Decomposition Agent responsible for Tree-of-Thought reasoning.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from utils import llm_manager
from utils.logger import get_logger


@dataclass
class Thought:
    """Represents a single node in the Tree-of-Thought."""
    text: str
    parent: Optional["Thought"] = None
    children: List["Thought"] = field(default_factory=list)
    score: float = 0.0

class ProblemDecompositionAgent:
    """
    An agent that uses Tree-of-Thought (ToT) reasoning to decompose complex,
    ambiguous goals into a series of clear, actionable high-level objectives.
    """

    def __init__(self, llm_manager: llm_manager.LLMManager):
        """
        Initializes the ProblemDecompositionAgent.

        Args:
            llm_manager: The language model manager for API calls.
        """
        self.llm_manager = llm_manager
        self.logger = get_logger(self.__class__.__name__)

    def _get_generation_prompt(self) -> str:
        """Creates the system prompt for generating new thoughts."""
        return """\
You are a creative and strategic thinker.
Your task is to expand on a given thought or idea, generating several diverse and plausible next steps or alternative perspectives.
Based on the user's complex goal and the current thought, generate 3 distinct next thoughts.
Each thought should be a concrete step or a refined idea that builds upon the current one.
Output ONLY the thoughts as a numbered list. Do not add any preamble or commentary.

Example:
Complex Goal: "Create a new, innovative mobile application for local community engagement."
Current Thought: "Initial idea: a social network for neighbors."

Your Output:
1. Refine the idea: Focus on hyper-local events and volunteering opportunities.
2. Alternative perspective: Instead of a social network, create a utility app for sharing tools or services.
3. Next step: Conduct market research to validate the need for a neighbor-focused social network.
"""

    def _get_evaluation_prompt(self) -> str:
        """Creates the system prompt for evaluating a thought."""
        return """\
You are a critical and analytical thinker.
Your task is to evaluate a given thought on its potential to help achieve a complex goal.
Consider its clarity, feasibility, and relevance.
Provide a score from 0.0 (completely useless) to 1.0 (perfectly aligned and highly promising).
Output ONLY the numerical score. Do not add any explanation, preamble, or other text.

Example:
Complex Goal: "Create a new, innovative mobile application for local community engagement."
Thought to Evaluate: "Refine the idea: Focus on hyper-local events and volunteering opportunities."

Your Output:
0.9
"""

    def _generate_thoughts(self, current_thought: Thought, complex_goal: str) -> List[str]:
        """Generates a list of potential next thoughts based on the current state."""
        self.logger.debug(f"Generating next thoughts for: {current_thought.text}")
        system_prompt = self._get_generation_prompt()
        # Modified user prompt to focus on current thought, avoiding ambiguity with complex goal
        user_prompt = f'Current Thought to expand: "{current_thought.text}"'

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            llm_result = self.llm_manager.chat(messages)  # type: ignore
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for thought generation.")
                return []

            response_text = llm_result.response_text
            thoughts = re.findall(r"^\d+\.\s*(.*)", response_text, re.MULTILINE)
            # Filter out any thoughts that are empty or just whitespace
            thoughts = [t.strip() for t in thoughts if t.strip()]
            self.logger.debug(f"Generated thoughts: {thoughts}")
            return thoughts
        except Exception as e:
            self.logger.error(f"Thought generation failed: {e}", exc_info=True)
            return []

    def _evaluate_thought(self, thought_to_evaluate: str, complex_goal: str) -> float:
        """Evaluates the quality of a thought and returns a score."""
        self.logger.debug(f"Evaluating thought: {thought_to_evaluate}")
        system_prompt = self._get_evaluation_prompt()
        user_prompt = f'Complex Goal: "{complex_goal}"\nThought to Evaluate: "{thought_to_evaluate}"'

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            llm_result = self.llm_manager.chat(messages)  # type: ignore
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for thought evaluation.")
                return 0.0

            response_text = llm_result.response_text.strip()
            self.logger.debug(f"LLM raw response for thought evaluation: {response_text}")

            score_match = re.search(r"(\d\.\d+)", response_text)
            if score_match:
                return float(score_match.group(1))

            self.logger.warning(f"Could not parse score from LLM response: '{response_text}'. Defaulting to 0.0.")
            return 0.0
        except Exception as e:
            self.logger.error(f"Thought evaluation failed: {e}", exc_info=True)
            return 0.0

    def decompose_goal(self, complex_goal: str, max_depth: int = 3, breadth: int = 3, score_threshold: float = 0.6) -> Optional[List[str]]:
        """
        Decomposes a complex goal into a sequence of simpler sub-goals using a Tree-of-Thought approach.
        
        Args:
            complex_goal: The high-level goal to decompose.
            max_depth: Maximum depth of the thought tree.
            breadth: Maximum number of thoughts to consider at each level.
            score_threshold: Minimum score for a thought to be considered viable.
        
        Returns:
            A list of sub-goals representing the best path found, or None if no viable path is found.
        """
        self.logger.info(f"Decomposing complex goal using ToT: '{complex_goal}'")
        root = Thought(text=complex_goal, parent=None)
        thought_tree: Dict[str, Thought] = {f"root_{id(root)}": root}
        best_path: List[Thought] = [root]
        best_score = 0.0
        current_thought = root

        for depth in range(max_depth):
            # Generate new thoughts from the current thought
            new_thoughts = self._generate_thoughts(current_thought, complex_goal)
            if not new_thoughts:
                self.logger.error("ToT process failed to find a viable path.")
                return None

            self.logger.debug(f"Depth {depth + 1}: Generated thoughts: {new_thoughts}")
            print(f"Depth {depth + 1}: Generated thoughts: {new_thoughts}")

            # Evaluate and score the new thoughts
            scored_thoughts = []
            for thought_text in new_thoughts:
                score = self._evaluate_thought(thought_text, complex_goal)
                if score >= score_threshold:  # Only consider thoughts above threshold
                    new_thought = Thought(text=thought_text, parent=current_thought, score=score)
                    thought_tree[f"thought_{id(new_thought)}"] = new_thought
                    scored_thoughts.append(new_thought)
                    self.logger.debug(f"Depth {depth + 1}: Thought '{thought_text}' scored {score}")
                    print(f"Depth {depth + 1}: Thought '{thought_text}' scored {score}")

            if not scored_thoughts:
                self.logger.error("ToT process failed to find a viable path.")
                return None

            # Prune to the top 'breadth' thoughts
            scored_thoughts.sort(key=lambda x: x.score, reverse=True)
            top_thoughts = scored_thoughts[:breadth]
            self.logger.debug(f"Depth {depth + 1}: Top thoughts after pruning: {[t.text for t in top_thoughts]}")
            print(f"Depth {depth + 1}: Top thoughts after pruning: {[t.text for t in top_thoughts]}")

            # Select the best thought to continue from, preferring one not already in the path
            best_new_thought = None
            path_texts = [t.text for t in best_path[1:]]  # Exclude the root node from duplicate check
            self.logger.debug(f"Depth {depth + 1}: Current path texts (excluding root): {path_texts}")
            print(f"Depth {depth + 1}: Current path texts (excluding root): {path_texts}")
            for thought in top_thoughts:
                if thought.text not in path_texts:
                    best_new_thought = thought
                    break
            if best_new_thought is None and top_thoughts:
                best_new_thought = top_thoughts[0]

            if best_new_thought:
                best_path.append(best_new_thought)
                best_score = best_new_thought.score
                current_thought = best_new_thought
                self.logger.debug(f"Depth {depth + 1}: Selected thought '{best_new_thought.text}' with score {best_score}")
                print(f"Depth {depth + 1}: Selected thought '{best_new_thought.text}' with score {best_score}")
            else:
                self.logger.error("No viable thought found at this depth.")
                break

        if len(best_path) <= 1:  # Only root node, no actual decomposition
            return None

        self.logger.info(f"Best path found with score {best_score}: {[t.text for t in best_path[1:]]}")
        return [t.text for t in best_path[1:]]
