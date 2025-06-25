"""
Helper Sync Tell - Advanced Thinking Plugin

This plugin enhances the Atlas helper system with structured multi-step thinking,
allowing for more nuanced and comprehensive responses to complex queries.

Features:
- Multi-step query breakdown and analysis
- Tool integration for enhanced responses
- Memory storage of thinking processes
- Cross-platform compatibility (Linux/macOS)
- Graceful degradation when components are unavailable
"""

import json
import logging
import sys
import time
import uuid
from typing import Any, Callable, Dict, List

#Use Atlas platform detection utilities
try:
    from utils.platform_utils import IS_HEADLESS, IS_LINUX, IS_MACOS, get_platform_info
    PLATFORM_UTILS_AVAILABLE = True
except ImportError:
    #Fallback platform detection
    import os
    import platform
    IS_MACOS = platform.system().lower() == "darwin"
    IS_LINUX = platform.system().lower() == "linux"
    IS_HEADLESS = os.environ.get("DISPLAY") is None and IS_LINUX
    PLATFORM_UTILS_AVAILABLE = False

    def get_platform_info():
        return {
            "system": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "is_macos": IS_MACOS,
            "is_linux": IS_LINUX,
            "is_headless": IS_HEADLESS,
        }

#Try to import memory manager components
try:
    from modules.agents.enhanced_memory_manager import MemoryScope, MemoryType
    MEMORY_INTEGRATION_AVAILABLE = True
except ImportError:
    MEMORY_INTEGRATION_AVAILABLE = False
    #Dummy classes for fallback
    class MemoryScope:
        DEPUTY_AGENT = "deputy_agent"
        HELPER_SYSTEM = "helper_system"

    class MemoryType:
        KNOWLEDGE = "knowledge"
        THINKING_PROCESS = "thinking_process"

class EnhancedHelperSyncTellTool:
    """
    Enhanced version of the Helper Sync Tell tool with comprehensive features.
    
    This tool enhances Atlas helper responses through structured multi-step thinking,
    providing more thorough and nuanced responses to complex queries.
    
    Features:
    - Intelligent query breakdown
    - Multi-tool integration
    - Memory storage of thinking processes
    - Cross-platform compatibility
    - Performance optimization
    - Error resilience
    """

    def __init__(self, llm_manager=None, memory_manager=None, config_manager=None):
        """
        Initialize the Enhanced Helper Sync Tell tool.
        
        Args:
            llm_manager: The LLM manager for text generation
            memory_manager: The memory manager for storing thinking processes
            config_manager: Configuration manager for settings
        """
        self.name = "helper_sync_tell"
        self.description = "Enhances responses through structured multi-step thinking and analysis"
        self.version = "2.0.0"

        #Core components
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)

        #Platform and compatibility info
        self.platform_info = get_platform_info()
        self.capabilities = self._assess_capabilities()

        #Configuration
        self.config = self._load_configuration()

        #Performance tracking
        self.performance_stats = {
            "queries_processed": 0,
            "average_response_time": 0.0,
            "successful_breakdowns": 0,
            "tool_usage_count": {},
            "memory_operations": 0,
        }

        self.logger.info("Enhanced HelperSyncTell tool initialized")
        self.logger.info(f"Platform: {self.platform_info.get('system', 'Unknown')}")
        self.logger.info(f"Capabilities: {list(self.capabilities.keys())}")

    def _assess_capabilities(self) -> Dict[str, bool]:
        """Assess what capabilities are available."""
        capabilities = {
            "llm_generation": self.llm_manager is not None,
            "memory_storage": self.memory_manager is not None and MEMORY_INTEGRATION_AVAILABLE,
            "platform_detection": PLATFORM_UTILS_AVAILABLE,
            "configuration": self.config_manager is not None,
            "headless_operation": IS_HEADLESS,
            "macos_features": IS_MACOS,
            "linux_features": IS_LINUX,
        }

        #Check Python version compatibility
        python_version = sys.version_info
        capabilities["python_312_plus"] = python_version >= (3, 12)
        capabilities["python_313_plus"] = python_version >= (3, 13)

        return capabilities

    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration settings for the tool."""
        default_config = {
            "max_sub_questions": 5,
            "min_sub_questions": 2,
            "enable_memory_storage": True,
            "enable_tool_integration": True,
            "response_refinement": True,
            "performance_tracking": True,
            "max_tool_response_length": 1000,
            "thinking_timeout": 30.0,
            "enable_caching": True,
        }

        if self.config_manager:
            try:
                #Try to load plugin-specific configuration using different methods
                plugin_config = {}
                if hasattr(self.config_manager, "get"):
                    plugin_config = self.config_manager.get("helper_sync_tell", {})
                elif hasattr(self.config_manager, "get_section"):
                    plugin_config = self.config_manager.get_section("helper_sync_tell", {})
                elif hasattr(self.config_manager, "config") and hasattr(self.config_manager.config, "get"):
                    #Try accessing through config attribute
                    if self.config_manager.config.has_section("helper_sync_tell"):
                        plugin_config = dict(self.config_manager.config.items("helper_sync_tell"))

                if plugin_config:
                    default_config.update(plugin_config)
                    self.logger.info(f"Loaded plugin configuration: {list(plugin_config.keys())}")

            except Exception as e:
                self.logger.debug(f"Could not load configuration (using defaults): {e}")

        return default_config

    def _store_thinking_step(self, thought_id: str, step_name: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Store a thinking step in memory with enhanced metadata.
        
        Args:
            thought_id: Unique identifier for the thinking process
            step_name: Name of the thinking step
            content: Content of the thinking step
            metadata: Additional metadata
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.capabilities["memory_storage"] or not self.config["enable_memory_storage"]:
            return False

        try:
            full_metadata = {
                "thought_id": thought_id,
                "step": step_name,
                "timestamp": time.time(),
                "platform": self.platform_info.get("system", "unknown"),
                "tool_version": self.version,
                **(metadata or {}),
            }

            self.memory_manager.add_memory_for_agent(
                agent_type=MemoryScope.HELPER_SYSTEM,
                memory_type=MemoryType.THINKING_PROCESS,
                content=content,
                metadata=full_metadata,
            )

            self.performance_stats["memory_operations"] += 1
            self.logger.debug(f"Stored thinking step '{step_name}' for thought {thought_id}")
            return True

        except Exception as e:
            self.logger.warning(f"Failed to store thinking step: {e}")
            return False

    def _generate_thought_id(self) -> str:
        """Generate a unique ID for a thinking process."""
        return f"thought_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    def _validate_query(self, query: str) -> bool:
        """Validate that the query is suitable for processing."""
        if not query or not query.strip():
            return False
        if len(query.strip()) < 10:  #Too short for meaningful breakdown
            return False
        return True

    def break_down_query(self, query: str) -> List[str]:
        """
        Break down a complex query into sub-questions with enhanced logic.
        
        Args:
            query: The original complex query
            
        Returns:
            A list of sub-questions
        """
        if not self._validate_query(query):
            return [query]

        if not self.capabilities["llm_generation"]:
            #Simple heuristic-based breakdown for fallback
            return self._heuristic_breakdown(query)

        try:
            max_questions = self.config["max_sub_questions"]
            min_questions = self.config["min_sub_questions"]

            prompt = f"""
            Break down this complex query into {min_questions}-{max_questions} simpler sub-questions that together will help
            answer the original query thoroughly. Each sub-question should focus on a specific aspect.
            
            Guidelines:
            - Make sub-questions specific and actionable
            - Ensure sub-questions cover all aspects of the original query
            - Avoid redundant or overlapping questions
            - Use clear, concise language
            
            Original query: {query}
            
            Format each sub-question as a numbered list (1. 2. 3. etc.).
            """

            response = self.llm_manager.generate_text(prompt)

            #Enhanced extraction of numbered questions
            sub_questions = []
            for line in response.split("\n"):
                line = line.strip()
                #Look for numbered patterns: "1.", "1)", "1 -", etc.
                if line and len(line) > 3:
                    if (line[0].isdigit() and line[1:3] in [". ", ") ", " -", "- "]):
                        #Extract the question part
                        question = line[2:].strip() if line[1] == "." else line[3:].strip()
                        if question and len(question) > 5:
                            #Clean up the question
                            question = question.rstrip("?") + "?" if not question.endswith("?") else question
                            sub_questions.append(question)

            #Validate the breakdown
            if len(sub_questions) < min_questions or len(sub_questions) > max_questions:
                self.logger.warning(f"Breakdown resulted in {len(sub_questions)} questions, expected {min_questions}-{max_questions}")
                if not sub_questions:
                    return [query]

            self.performance_stats["successful_breakdowns"] += 1
            return sub_questions if sub_questions else [query]

        except Exception as e:
            self.logger.error(f"Error breaking down query: {e}")
            return [query]

    def _heuristic_breakdown(self, query: str) -> List[str]:
        """Fallback heuristic-based query breakdown."""
        #Simple heuristic: look for "and", "or", question words
        keywords = ["what", "how", "why", "when", "where", "who", "which"]

        #Split on "and" if it appears to separate different aspects
        if " and " in query.lower():
            parts = [part.strip() for part in query.split(" and ")]
            if len(parts) <= self.config["max_sub_questions"]:
                return [part + "?" if not part.endswith("?") else part for part in parts if len(part) > 10]

        #If query contains multiple question words, try to extract aspects
        if sum(1 for kw in keywords if kw in query.lower()) > 1:
            return [
                f"What are the key aspects of: {query}?",
                f"How does this work: {query}?",
                f"What are the implications of: {query}?",
            ]

        #Default fallback
        return [query]

    def analyze_sub_question(self, sub_question: str, available_tools: Dict[str, Callable]) -> str:
        """
        Analyze a sub-question using available tools with enhanced integration.
        
        Args:
            sub_question: The sub-question to analyze
            available_tools: Dictionary of tools that can be used for analysis
            
        Returns:
            Analysis result for the sub-question
        """
        start_time = time.time()

        try:
            #Use available tools with better selection logic
            tool_results = {}
            relevant_tools = self._select_relevant_tools(sub_question, available_tools)

            for tool_name in relevant_tools:
                try:
                    tool_fn = available_tools[tool_name]
                    result = tool_fn(sub_question)
                    if result:
                        #Limit result size but preserve important information
                        max_length = self.config["max_tool_response_length"]
                        result_str = str(result)
                        if len(result_str) > max_length:
                            result_str = result_str[:max_length] + "... [truncated]"
                        tool_results[tool_name] = result_str

                        #Track tool usage
                        if tool_name not in self.performance_stats["tool_usage_count"]:
                            self.performance_stats["tool_usage_count"][tool_name] = 0
                        self.performance_stats["tool_usage_count"][tool_name] += 1

                except Exception as e:
                    self.logger.debug(f"Tool {tool_name} failed for question '{sub_question}': {e}")
                    tool_results[tool_name] = f"Tool error: {str(e)[:100]}"

            #Generate analysis using LLM if available
            if self.capabilities["llm_generation"]:
                if tool_results:
                    analysis_prompt = f"""
                    Analyze this question based on the tool results provided.
                    Provide a clear, comprehensive analysis that synthesizes the information.
                    
                    Question: {sub_question}
                    
                    Tool results:
                    {json.dumps(tool_results, indent=2)}
                    
                    Instructions:
                    - Focus on the most relevant information
                    - Provide specific insights, not just summaries
                    - If tools provided conflicting information, note this
                    - Make the analysis actionable and useful
                    
                    Analysis:
                    """
                else:
                    analysis_prompt = f"""
                    Provide a detailed analysis for this question based on your knowledge:
                    
                    Question: {sub_question}
                    
                    Instructions:
                    - Be specific and informative
                    - Consider multiple perspectives if relevant
                    - Provide actionable insights
                    - Keep the analysis focused and relevant
                    
                    Analysis:
                    """

                #Use the correct LLM method
                try:
                    messages = [{"role": "user", "content": analysis_prompt}]
                    response = self.llm_manager.chat(messages)
                    if response and hasattr(response, "content"):
                        analysis = response.content
                    elif response and hasattr(response, "response"):
                        analysis = response.response
                    else:
                        analysis = str(response)
                except Exception as llm_error:
                    self.logger.warning(f"LLM generation failed: {llm_error}")
                    #Fallback to simple analysis
                    if tool_results:
                        analysis_parts = [f"Analysis of '{sub_question}':"]
                        for tool, result in tool_results.items():
                            analysis_parts.append(f"• {tool}: {result}")
                        analysis = "\n".join(analysis_parts)
                    else:
                        analysis = f"Analysis of '{sub_question}': This question requires investigation of [key aspects that would need detailed examination]."
            #Fallback analysis without LLM
            elif tool_results:
                analysis_parts = [f"Analysis of '{sub_question}':"]
                for tool, result in tool_results.items():
                    analysis_parts.append(f"• {tool}: {result}")
                analysis = "\n".join(analysis_parts)
            else:
                analysis = f"Analysis of '{sub_question}': No specific analysis tools available, but this question requires attention to [key aspects that would need investigation]."

            #Track performance
            processing_time = time.time() - start_time
            self.logger.debug(f"Analyzed sub-question in {processing_time:.2f}s using {len(tool_results)} tools")

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing sub-question '{sub_question}': {e}")
            return f"Error analyzing: {sub_question} - {e!s}"

    def _select_relevant_tools(self, question: str, available_tools: Dict[str, Callable]) -> List[str]:
        """Select the most relevant tools for a given question."""
        if not available_tools:
            return []

        #Simple keyword-based tool selection
        question_lower = question.lower()
        tool_keywords = {
            "code_search": ["code", "function", "class", "method", "implementation", "source"],
            "file_info": ["file", "directory", "structure", "organization"],
            "memory_query": ["memory", "remember", "stored", "previous", "history"],
            "web_search": ["search", "find", "lookup", "information", "research"],
            "system_info": ["system", "platform", "environment", "configuration"],
        }

        relevant_tools = []
        for tool_name in available_tools:
            #Check if tool has associated keywords
            if tool_name in tool_keywords:
                keywords = tool_keywords[tool_name]
                if any(keyword in question_lower for keyword in keywords):
                    relevant_tools.append(tool_name)
            else:
                #If no keywords defined, consider it potentially relevant
                relevant_tools.append(tool_name)

        #Limit the number of tools to avoid overwhelming the analysis
        return relevant_tools[:3]

    def synthesize_response(self, original_query: str, analyses: List[str]) -> str:
        """
        Synthesize a comprehensive response from analyses with enhanced logic.
        
        Args:
            original_query: The original complex query
            analyses: List of analysis results for sub-questions
            
        Returns:
            Synthesized comprehensive response
        """
        if not analyses:
            return "I apologize, but I wasn't able to analyze your question properly."

        if not self.capabilities["llm_generation"]:
            #Enhanced fallback synthesis
            return self._fallback_synthesis(original_query, analyses)

        try:
            synthesis_prompt = f"""
            Create a comprehensive, well-structured response to this query based on the detailed analyses below.
            
            Original query: {original_query}
            
            Detailed analyses:
            {"\n".join([f"Analysis {i+1}:\n{analysis}\n" for i, analysis in enumerate(analyses)])}
            
            Instructions for the response:
            1. Create a cohesive narrative that addresses the original query completely
            2. Integrate insights from all analyses naturally
            3. Use a conversational, helpful tone
            4. Organize information logically with clear structure
            5. Provide specific, actionable information when possible
            6. Do not mention the analysis process or sub-questions
            7. Make the response feel like a natural, expert answer
            8. Include relevant details that add value
            
            Comprehensive response:
            """

            #Use the correct LLM method
            try:
                messages = [{"role": "user", "content": synthesis_prompt}]
                llm_response = self.llm_manager.chat(messages)
                if llm_response and hasattr(llm_response, "content"):
                    response = llm_response.content
                elif llm_response and hasattr(llm_response, "response"):
                    response = llm_response.response
                else:
                    response = str(llm_response)
            except Exception as llm_error:
                self.logger.warning(f"LLM synthesis failed: {llm_error}")
                response = self._fallback_synthesis(original_query, analyses)

            #Optional refinement if enabled
            if self.config["response_refinement"] and response != self._fallback_synthesis(original_query, analyses):
                response = self._refine_response(original_query, response)

            return response

        except Exception as e:
            self.logger.error(f"Error synthesizing response: {e}")
            return self._fallback_synthesis(original_query, analyses)

    def _fallback_synthesis(self, original_query: str, analyses: List[str]) -> str:
        """Fallback synthesis method when LLM is not available."""
        response_parts = [
            f"Here's a comprehensive analysis of your question: {original_query}",
            "",
        ]

        for i, analysis in enumerate(analyses, 1):
            response_parts.append(f"Key Insight {i}:")
            response_parts.append(analysis)
            response_parts.append("")

        response_parts.append("These insights should help address your question comprehensively.")

        return "\n".join(response_parts)

    def _refine_response(self, original_query: str, draft_response: str) -> str:
        """Refine the response for better quality."""
        if not self.capabilities["llm_generation"]:
            return draft_response

        try:
            refinement_prompt = f"""
            Refine this response to make it more helpful, clear, and engaging.
            
            Original query: {original_query}
            
            Draft response:
            {draft_response}
            
            Refinement goals:
            - Improve clarity and readability
            - Ensure all aspects of the query are addressed
            - Make the tone more conversational and helpful
            - Add specific examples or details where beneficial
            - Remove any redundancy or awkward phrasing
            - Ensure the response flows naturally
            
            Refined response:
            """

            #Use the correct LLM method
            try:
                messages = [{"role": "user", "content": refinement_prompt}]
                llm_response = self.llm_manager.chat(messages)
                if llm_response and hasattr(llm_response, "content"):
                    return llm_response.content
                if llm_response and hasattr(llm_response, "response"):
                    return llm_response.response
                return str(llm_response)
            except Exception as llm_error:
                self.logger.warning(f"LLM refinement failed: {llm_error}")
                return draft_response

        except Exception as e:
            self.logger.warning(f"Response refinement failed: {e}")
            return draft_response

    def __call__(self, query: str, available_tools: Dict[str, Callable] = None) -> str:
        """
        Process a query through enhanced structured thinking.
        
        Args:
            query: The complex query to process
            available_tools: Dictionary of tools that can be used in the analysis
            
        Returns:
            A comprehensive response to the query
        """
        start_time = time.time()

        if available_tools is None:
            available_tools = {}

        thought_id = self._generate_thought_id()
        self.logger.info(f"Starting enhanced structured thinking process {thought_id}")

        try:
            #Validate and preprocess the query
            if not self._validate_query(query):
                return "I need a more detailed question to provide a comprehensive analysis."

            #Store initial query
            self._store_thinking_step(
                thought_id,
                "initial_query",
                f"Original query: {query}",
                {"query_length": len(query), "available_tools": list(available_tools.keys())},
            )

            #Step 1: Break down the query
            self.logger.debug(f"Breaking down query: {query}")
            sub_questions = self.break_down_query(query)
            self._store_thinking_step(
                thought_id,
                "breakdown",
                f"Broke down query into {len(sub_questions)} sub-questions:\n" +
                "\n".join([f"{i+1}. {q}" for i, q in enumerate(sub_questions)]),
                {"sub_question_count": len(sub_questions)},
            )

            #Step 2: Analyze each sub-question
            analyses = []
            for i, sub_question in enumerate(sub_questions):
                self.logger.debug(f"Analyzing sub-question {i+1}/{len(sub_questions)}: {sub_question}")
                analysis = self.analyze_sub_question(sub_question, available_tools)
                analyses.append(analysis)

                #Store individual analysis
                self._store_thinking_step(
                    thought_id,
                    f"analysis_{i+1}",
                    f"Sub-question: {sub_question}\n\nAnalysis:\n{analysis}",
                    {"sub_question_index": i+1, "analysis_length": len(analysis)},
                )

            #Step 3: Synthesize comprehensive response
            self.logger.debug("Synthesizing comprehensive response")
            final_response = self.synthesize_response(query, analyses)

            #Store final response
            self._store_thinking_step(
                thought_id,
                "final_response",
                final_response,
                {"response_length": len(final_response)},
            )

            #Update performance statistics
            processing_time = time.time() - start_time
            self.performance_stats["queries_processed"] += 1
            self.performance_stats["average_response_time"] = (
                (self.performance_stats["average_response_time"] * (self.performance_stats["queries_processed"] - 1) + processing_time) /
                self.performance_stats["queries_processed"]
            )

            self.logger.info(f"Completed enhanced structured thinking process {thought_id} in {processing_time:.2f}s")

            return final_response

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error while processing your question: {e!s}"
            self.logger.error(f"Error in structured thinking process {thought_id}: {e}")

            #Store error for debugging
            self._store_thinking_step(
                thought_id,
                "error",
                f"Error occurred: {e!s}",
                {"error_type": type(e).__name__},
            )

            return error_msg

    def process_help_request(self, message: str, available_tools: Dict[str, Callable] = None) -> str:
        """
        Process a help request with structured thinking approach.
        This is the main integration point for Atlas's helper mode.
        
        Args:
            message: The user's help request
            available_tools: Available analysis tools from Atlas
            
        Returns:
            Comprehensive response using structured thinking
        """
        #Add Atlas-specific tools to the available tools
        if available_tools is None:
            available_tools = {}

        #Use the main processing method
        return self(message, available_tools)

    def integrate_with_atlas_help_mode(self, main_app) -> bool:
        """
        Integrate the plugin with Atlas's main help mode handler.
        
        Args:
            main_app: The AtlasApp instance
            
        Returns:
            True if integration successful, False otherwise
        """
        try:
            #Get the original help mode handler
            if not hasattr(main_app, "_handle_help_mode"):
                self.logger.warning("Atlas app does not have _handle_help_mode method")
                return False

            original_handler = main_app._handle_help_mode

            def enhanced_help_mode_handler(message: str, context) -> str:
                """Enhanced help mode handler using structured thinking."""
                #Check if this is a simple command that should use the original handler
                simple_commands = ["read file", "list directory", "tree", "search for", "info about", "search functions"]
                message_lower = message.lower()

                #Use original handler for simple file operations and basic commands
                if any(cmd in message_lower for cmd in simple_commands):
                    return original_handler(message, context)

                #For complex analysis requests, check if helper sync tell should handle them
                complex_keywords = ["проаналізуй", "analyze", "як ти використовуєш", "how do you use",
                                  "вдосконалення", "improvement", "проблематика", "problems",
                                  "міркування", "reasoning", "пам'ять", "memory", "як працює", "how does work"]

                if any(keyword in message_lower for keyword in complex_keywords):
                    #Use our structured thinking for complex analysis
                    self.logger.info("Using Enhanced Helper Sync Tell for complex analysis")

                    #Get available tools from Atlas
                    available_tools = {}

                    #Add Atlas tools if available
                    if hasattr(main_app, "code_reader"):
                        available_tools.update({
                            "semantic_search": lambda q: main_app.code_reader.semantic_search(q) if hasattr(main_app.code_reader, "semantic_search") else f"Semantic search for: {q}",
                            "file_search": lambda q: main_app.code_reader.search_in_files(q) if hasattr(main_app.code_reader, "search_in_files") else f"File search for: {q}",
                            "read_file": lambda f: main_app.code_reader.read_file(f) if hasattr(main_app.code_reader, "read_file") else f"Read file: {f}",
                            "grep_search": lambda q: main_app.code_reader.search_in_files(q) if hasattr(main_app.code_reader, "search_in_files") else f"Grep search for: {q}",
                        })

                    #Add memory analysis tools
                    if hasattr(main_app, "agent_manager") and hasattr(main_app.agent_manager, "memory_manager"):
                        memory_manager = main_app.agent_manager.memory_manager
                        available_tools.update({
                            "memory_search": lambda q: f"Memory search for: {q} - {memory_manager.__class__.__name__} available",
                            "memory_analysis": lambda: f"Memory system analysis - using {memory_manager.__class__.__name__}",
                        })

                    try:
                        #Use structured thinking for the complex query
                        return self.process_help_request(message, available_tools)
                    except Exception as e:
                        self.logger.error(f"Error in enhanced help mode: {e}")
                        #Fallback to original handler
                        return original_handler(message, context)

                #For other cases, use the original handler
                return original_handler(message, context)

            #Replace the original handler
            main_app._handle_help_mode = enhanced_help_mode_handler
            main_app.helper_sync_tell_integration = True

            self.logger.info("Successfully integrated with Atlas help mode")
            return True

        except Exception as e:
            self.logger.error(f"Failed to integrate with Atlas help mode: {e}")
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the tool."""
        return {
            **self.performance_stats,
            "capabilities": self.capabilities,
            "platform_info": self.platform_info,
            "configuration": self.config,
        }

    def reset_performance_stats(self) -> None:
        """Reset performance statistics."""
        self.performance_stats = {
            "queries_processed": 0,
            "average_response_time": 0.0,
            "successful_breakdowns": 0,
            "tool_usage_count": {},
            "memory_operations": 0,
        }
        self.logger.info("Performance statistics reset")


#Create alias for backward compatibility
HelperSyncTellTool = EnhancedHelperSyncTellTool


def register(llm_manager=None, atlas_app=None, **kwargs):
    """
    Register the Enhanced Helper Sync Tell tool with comprehensive integration.
    
    Args:
        llm_manager: LLM manager instance
        atlas_app: Main Atlas application instance (for integration)
        **kwargs: Additional arguments (may include agent_manager, etc.)
        
    Returns:
        Plugin registration data with enhanced tool
    """
    try:
        #Try to get additional components
        memory_manager = None
        config_manager = None

        #Try to get atlas_app from kwargs if not provided directly
        if not atlas_app and "agent_manager" in kwargs:
            agent_manager = kwargs["agent_manager"]
            #Try to find the main app through agent manager
            if hasattr(agent_manager, "app"):
                atlas_app = agent_manager.app

        #Look for memory manager
        try:
            if "agent_manager" in kwargs:
                agent_manager = kwargs["agent_manager"]
                if hasattr(agent_manager, "memory_manager"):
                    memory_manager = agent_manager.memory_manager
            else:
                from modules.agents.agent_manager import AgentManager
                agent_manager = AgentManager.get_instance()
                if agent_manager and hasattr(agent_manager, "memory_manager"):
                    memory_manager = agent_manager.memory_manager
        except (ImportError, AttributeError):
            pass

        #Look for config manager
        try:
            from config_manager import ConfigManager
            config_manager = ConfigManager()
        except ImportError:
            pass

        #Create the enhanced tool
        tool = EnhancedHelperSyncTellTool(
            llm_manager=llm_manager,
            memory_manager=memory_manager,
            config_manager=config_manager,
        )

        #Attempt integration with Atlas app if provided
        integration_success = False
        if atlas_app:
            integration_success = tool.integrate_with_atlas_help_mode(atlas_app)

        logging.info("Enhanced Helper Sync Tell tool registered successfully")
        logging.info(f"Tool capabilities: {list(tool.capabilities.keys())}")

        if integration_success:
            logging.info("Successfully integrated with Atlas help mode")
        else:
            logging.info("Plugin registered but not integrated with help mode (atlas_app not provided)")

        #Store reference for potential integration
        tool._registration_context = {
            "llm_manager": llm_manager,
            "memory_manager": memory_manager,
            "config_manager": config_manager,
            "atlas_app": atlas_app,
            "integration_success": integration_success,
            "registration_time": time.time(),
        }

        return {
            "tools": [tool],
            "agents": [],
            "metadata": {
                "version": "2.0.0",
                "capabilities": tool.capabilities,
                "platform_info": tool.platform_info,
                "integration_status": integration_success,
            },
        }

    except Exception as e:
        logging.exception(f"Failed to register Enhanced Helper Sync Tell plugin: {e}")
        import traceback
        logging.exception(f"Traceback: {traceback.format_exc()}")
        return {
            "tools": [],
            "agents": [],
            "metadata": {"error": str(e)},
        }
