"""
Helper Sync Tell - Advanced Thinking Plugin

This plugin enhances the Atlas helper system with structured multi-step thinking,
allowing for more nuanced and comprehensive responses to complex queries.
It works by breaking down complex requests, analyzing them step by step,
and synthesizing the results into a comprehensive response.

The plugin implements a synchronous "thinking" process by:
1. Breaking down complex queries into sub-questions
2. Analyzing each sub-question independently
3. Collecting results from tools and micro-analyses
4. Synthesizing a comprehensive response
5. Performing self-refinement if needed
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
import sys
import json

from utils.platform_utils import IS_MACOS, IS_LINUX, IS_HEADLESS
from agents.enhanced_memory_manager import MemoryScope, MemoryType, EnhancedMemoryManager

class HelperSyncTellTool:
    """
    A tool that enhances the Atlas helper with structured multi-step thinking.
    This allows for breaking down complex queries, analyzing them step-by-step,
    and synthesizing comprehensive responses.
    """

    def __init__(self, llm_manager=None, memory_manager=None):
        """
        Initialize the Helper Sync Tell tool.
        
        Args:
            llm_manager: The LLM manager for generating responses
            memory_manager: The memory manager for storing thinking steps
        """
        self.name = "helper_sync_tell"
        self.description = "Enhances responses through structured multi-step thinking"
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Check platform compatibility
        self.platform_info = {
            "is_macos": IS_MACOS,
            "is_linux": IS_LINUX,
            "is_headless": IS_HEADLESS,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}"
        }
        
        self.logger.info(f"HelperSyncTell tool initialized on {self.platform_info}")

    def _generate_thought_id(self) -> str:
        """Generate a unique ID for a thinking process."""
        return f"thought_{uuid.uuid4().hex[:8]}"
    
    def _store_thinking_step(self, thought_id: str, step_name: str, content: str) -> None:
        """Store a thinking step in memory if memory manager is available."""
        if self.memory_manager:
            metadata = {
                "thought_id": thought_id,
                "step": step_name,
                "timestamp": time.time()
            }
            
            self.memory_manager.add_memory_for_agent(
                agent_type=MemoryScope.DEPUTY_AGENT, 
                memory_type=MemoryType.KNOWLEDGE,
                content=content,
                metadata=metadata
            )
            
            self.logger.debug(f"Stored thinking step '{step_name}' for thought {thought_id}")
    
    def break_down_query(self, query: str) -> List[str]:
        """
        Break down a complex query into sub-questions.
        
        Args:
            query: The original complex query
            
        Returns:
            A list of sub-questions
        """
        if not self.llm_manager:
            # Simple fallback if LLM not available
            return [query]
        
        prompt = f"""
        Break down this complex query into 2-5 simpler sub-questions that together will help
        answer the original query thoroughly. Each sub-question should focus on a specific aspect.
        
        Original query: {query}
        
        Format each sub-question as a numbered list without additional explanation.
        """
        
        response = self.llm_manager.generate_text(prompt)
        
        # Extract just the numbered questions
        sub_questions = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() and line[1:].startswith(". ")):
                sub_questions.append(line[line.find(" ")+1:])
        
        # If no sub-questions were identified, use the original query
        if not sub_questions:
            sub_questions = [query]
            
        return sub_questions
    
    def analyze_sub_question(self, sub_question: str, available_tools: Dict[str, Callable]) -> str:
        """
        Analyze a sub-question using available tools and micro-analyses.
        
        Args:
            sub_question: The sub-question to analyze
            available_tools: Dictionary of tools that can be used for analysis
            
        Returns:
            Analysis result for the sub-question
        """
        # Simple analysis fallback if no tools or LLM available
        if not available_tools and not self.llm_manager:
            return f"Analysis of: {sub_question}\nNo tools available for detailed analysis."
        
        # Use LLM to determine which tools to use
        if self.llm_manager:
            tool_selection_prompt = f"""
            Determine which tools would be most helpful to answer this question:
            
            Question: {sub_question}
            
            Available tools: {", ".join(available_tools.keys())}
            
            Specify the tool names to use, or "none" if no tool is appropriate.
            """
            
            tools_to_use = self.llm_manager.generate_text(tool_selection_prompt)
            
            # Extract tool names from response
            suggested_tools = [
                tool.strip() for tool in tools_to_use.split(",")
                if tool.strip() in available_tools
            ]
        else:
            suggested_tools = []
        
        # Results from each tool
        tool_results = {}
        
        # Run selected tools
        for tool_name in suggested_tools:
            try:
                if tool_name in available_tools:
                    tool_fn = available_tools[tool_name]
                    result = tool_fn(sub_question)
                    tool_results[tool_name] = result
            except Exception as e:
                self.logger.error(f"Error using tool {tool_name}: {e}")
                tool_results[tool_name] = f"Error: {str(e)}"
        
        # Use LLM to analyze results if available
        if self.llm_manager and tool_results:
            analysis_prompt = f"""
            Analyze the following results to answer this question:
            
            Question: {sub_question}
            
            Tool results:
            {json.dumps(tool_results, indent=2)}
            
            Provide a clear, concise analysis based on these results.
            """
            
            analysis = self.llm_manager.generate_text(analysis_prompt)
        elif self.llm_manager:
            # Direct LLM analysis if no tools used
            analysis_prompt = f"""
            Provide an analysis for this question based on your knowledge:
            
            Question: {sub_question}
            """
            
            analysis = self.llm_manager.generate_text(analysis_prompt)
        else:
            # Simple fallback
            analysis = f"No analysis available for: {sub_question}"
        
        return analysis
    
    def synthesize_response(self, original_query: str, analyses: List[str]) -> str:
        """
        Synthesize a comprehensive response from individual analyses.
        
        Args:
            original_query: The original complex query
            analyses: List of analysis results for sub-questions
            
        Returns:
            Synthesized comprehensive response
        """
        if not self.llm_manager:
            # Simple fallback
            return "\n\n".join(["Here's what I found:"] + analyses)
        
        synthesis_prompt = f"""
        Synthesize a comprehensive, clear response to the original query based on these analyses.
        
        Original query: {original_query}
        
        Analyses:
        {"\n\n".join(analyses)}
        
        Create a well-structured, cohesive response that addresses the original query fully.
        Make the response conversational and human-like, without mentioning the underlying
        process or the fact that the query was broken down.
        """
        
        synthesis = self.llm_manager.generate_text(synthesis_prompt)
        return synthesis
    
    def refine_response(self, original_query: str, draft_response: str) -> str:
        """
        Optionally refine the response for clarity, accuracy, and completeness.
        
        Args:
            original_query: The original complex query
            draft_response: The draft synthesized response
            
        Returns:
            Refined response
        """
        if not self.llm_manager:
            return draft_response
        
        refinement_prompt = f"""
        Review and refine this draft response to the user's query.
        
        Original query: {original_query}
        
        Draft response:
        {draft_response}
        
        Please improve the response by:
        1. Ensuring all parts of the query are addressed
        2. Making the explanation clear and easy to understand
        3. Removing any AI-like phrasing or mentions of "analysis"
        4. Making the tone conversational and helpful
        5. Adding specific details where beneficial
        
        Provide the refined response only, without explaining your changes.
        """
        
        refined_response = self.llm_manager.generate_text(refinement_prompt)
        return refined_response
    
    def __call__(self, query: str, available_tools: Dict[str, Callable] = None) -> str:
        """
        Process a complex query through structured thinking steps.
        
        Args:
            query: The complex query to process
            available_tools: Dictionary of tools that can be used in the analysis
            
        Returns:
            A comprehensive response to the query
        """
        thought_id = self._generate_thought_id()
        if available_tools is None:
            available_tools = {}
        
        self.logger.info(f"Starting structured thinking process {thought_id} for query: {query}")
        
        # Step 1: Break down the query
        self.logger.debug(f"Breaking down query: {query}")
        sub_questions = self.break_down_query(query)
        self._store_thinking_step(thought_id, "breakdown", 
                                 f"Broke down query into {len(sub_questions)} sub-questions: {sub_questions}")
        
        # Step 2: Analyze each sub-question
        analyses = []
        for i, sub_question in enumerate(sub_questions):
            self.logger.debug(f"Analyzing sub-question {i+1}: {sub_question}")
            analysis = self.analyze_sub_question(sub_question, available_tools)
            analyses.append(analysis)
            self._store_thinking_step(
                thought_id, 
                f"analysis_{i+1}", 
                f"Sub-question: {sub_question}\n\nAnalysis: {analysis}"
            )
        
        # Step 3: Synthesize a comprehensive response
        self.logger.debug("Synthesizing response from analyses")
        draft_response = self.synthesize_response(query, analyses)
        self._store_thinking_step(thought_id, "synthesis", draft_response)
        
        # Step 4: Refine the response if needed
        self.logger.debug("Refining response")
        final_response = self.refine_response(query, draft_response)
        self._store_thinking_step(thought_id, "refinement", final_response)
        
        self.logger.info(f"Completed structured thinking process {thought_id}")
        
        return final_response


def register(llm_manager=None):
    """
    Register the Helper Sync Tell tool with the plugin system.
    
    Args:
        llm_manager: LLM manager instance
        
    Returns:
        Plugin registration data
    """
    try:
        # Try to import memory manager
        from agents.enhanced_memory_manager import EnhancedMemoryManager
        memory_manager = None
        
        # Look for memory manager in the agent manager if available
        try:
            from agents.agent_manager import AgentManager
            agent_manager = AgentManager.get_instance()
            if agent_manager and hasattr(agent_manager, 'memory_manager'):
                memory_manager = agent_manager.memory_manager
        except (ImportError, AttributeError):
            pass
            
        # Create the tool
        helper_sync_tell_tool = HelperSyncTellTool(
            llm_manager=llm_manager,
            memory_manager=memory_manager
        )
        
        # Set up integration with helper mode
        from .integration import get_integration
        integration = get_integration(helper_sync_tell_tool)
        
        # Try to patch the main application
        try:
            import sys
            # Find main app instance if it exists
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'app'):
                # Patch the main application
                integration.patch_main_application(main_module.app)
                logging.info("Successfully integrated Helper Sync Tell with main application")
        except Exception as e:
            logging.warning(f"Could not integrate with main application: {e}")
        
        # Return registration data
        return {
            "tools": [helper_sync_tell_tool],
            "agents": []
        }
        
    except Exception as e:
        logging.error(f"Failed to register Helper Sync Tell plugin: {e}", exc_info=True)
        return {"tools": [], "agents": []}
