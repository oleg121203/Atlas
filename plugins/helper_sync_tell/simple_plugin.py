"""
Helper Sync Tell - Minimal Working Version

A simplified version of the Helper Sync Tell plugin that focuses on core
functionality and should load without import issues.
"""

import logging
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
import sys
import json

#Platform detection - simplified to avoid import issues
import platform
import os

IS_MACOS = platform.system().lower() == 'darwin'
IS_LINUX = platform.system().lower() == 'linux'
IS_HEADLESS = os.environ.get('DISPLAY') is None and IS_LINUX

class SimpleHelperSyncTellTool:
    """
    A simplified version of the Helper Sync Tell tool that enhances Atlas
    helper responses through structured multi-step thinking.
    """

    def __init__(self, llm_manager=None, memory_manager=None):
        """Initialize the Helper Sync Tell tool."""
        self.name = "helper_sync_tell"
        self.description = "Enhances responses through structured multi-step thinking"
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        #Platform info
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
    
    def break_down_query(self, query: str) -> List[str]:
        """Break down a complex query into sub-questions."""
        if not self.llm_manager:
            #Simple fallback - just return the original query
            return [query]
        
        try:
            prompt = f"""
            Break down this complex query into 2-4 simpler sub-questions that together will help
            answer the original query thoroughly. Each sub-question should focus on a specific aspect.
            
            Original query: {query}
            
            Format each sub-question as a numbered list.
            """
            
            response = self.llm_manager.generate_text(prompt)
            
            #Extract numbered questions
            sub_questions = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() and ". " in line):
                    question = line[line.find(". ")+2:].strip()
                    if question:
                        sub_questions.append(question)
            
            #Fallback to original query if no sub-questions found
            return sub_questions if sub_questions else [query]
            
        except Exception as e:
            self.logger.error(f"Error breaking down query: {e}")
            return [query]
    
    def analyze_sub_question(self, sub_question: str, available_tools: Dict[str, Callable]) -> str:
        """Analyze a sub-question using available tools."""
        try:
            #Try to use available tools
            tool_results = {}
            for tool_name, tool_fn in available_tools.items():
                try:
                    result = tool_fn(sub_question)
                    if result:
                        tool_results[tool_name] = str(result)[:500]  #Limit result size
                except Exception as e:
                    self.logger.debug(f"Tool {tool_name} failed: {e}")
            
            #Use LLM to analyze if available
            if self.llm_manager:
                if tool_results:
                    analysis_prompt = f"""
                    Analyze this question based on the tool results:
                    
                    Question: {sub_question}
                    
                    Tool results:
                    {json.dumps(tool_results, indent=2)}
                    
                    Provide a clear analysis based on these results.
                    """
                else:
                    analysis_prompt = f"""
                    Provide an analysis for this question:
                    
                    Question: {sub_question}
                    """
                
                return self.llm_manager.generate_text(analysis_prompt)
            else:
                #Simple fallback
                if tool_results:
                    return f"Analysis of '{sub_question}':\n" + "\n".join([f"- {tool}: {result}" for tool, result in tool_results.items()])
                else:
                    return f"Analysis of '{sub_question}': No specific analysis available."
                    
        except Exception as e:
            self.logger.error(f"Error analyzing sub-question: {e}")
            return f"Error analyzing: {sub_question}"
    
    def synthesize_response(self, original_query: str, analyses: List[str]) -> str:
        """Synthesize a comprehensive response from analyses."""
        if not self.llm_manager:
            #Simple fallback
            return f"Analysis of your question:\n\n" + "\n\n".join(analyses)
        
        try:
            synthesis_prompt = f"""
            Create a comprehensive response to this query based on the analyses below.
            Make the response conversational and helpful.
            
            Original query: {original_query}
            
            Analyses:
            {chr(10).join(analyses)}
            
            Provide a well-structured response that addresses the original query.
            """
            
            return self.llm_manager.generate_text(synthesis_prompt)
            
        except Exception as e:
            self.logger.error(f"Error synthesizing response: {e}")
            return f"Analysis of your question:\n\n" + "\n\n".join(analyses)
    
    def __call__(self, query: str, available_tools: Dict[str, Callable] = None) -> str:
        """Process a query through structured thinking."""
        if available_tools is None:
            available_tools = {}
        
        thought_id = self._generate_thought_id()
        self.logger.info(f"Processing query with structured thinking {thought_id}")
        
        try:
            #Step 1: Break down the query
            sub_questions = self.break_down_query(query)
            
            #Step 2: Analyze each sub-question
            analyses = []
            for sub_question in sub_questions:
                analysis = self.analyze_sub_question(sub_question, available_tools)
                analyses.append(analysis)
            
            #Step 3: Synthesize response
            final_response = self.synthesize_response(query, analyses)
            
            self.logger.info(f"Completed structured thinking process {thought_id}")
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in structured thinking process: {e}")
            return f"I apologize, but I encountered an error while processing your question: {query}"

def register(llm_manager=None):
    """Register the simplified Helper Sync Tell tool."""
    try:
        #Create the tool
        tool = SimpleHelperSyncTellTool(llm_manager=llm_manager)
        
        logging.info("Helper Sync Tell tool registered successfully")
        
        return {
            "tools": [tool],
            "agents": []
        }
        
    except Exception as e:
        logging.error(f"Failed to register Helper Sync Tell plugin: {e}")
        return {"tools": [], "agents": []}
