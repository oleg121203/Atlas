"""
Ultimate AI Assistant Integration for Atlas

This module represents the pinnacle of AI assistant capabilities, integrating
meta-cognitive awareness, advanced contextual analysis, and sophisticated reasoning
based on real AI assistant experience.

Key features:
- Meta-cognitive self-awareness and adaptation
- Multi-dimensional contextual understanding
- Advanced reasoning with uncertainty handling
- Cross-domain knowledge integration
- Adaptive learning and improvement
- Human-like thinking patterns
- Sophisticated tool integration
- Real-time performance optimization
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import traceback

#Import our advanced components
try:
    from meta_cognitive_engine import (
        MetaCognitiveEngine, CognitiveMode, EpistemicState,
        CognitiveSnapshot, ReasoningTrace
    )
    from contextual_analyzer import (
        AdvancedContextualAnalyzer, ContextProfile, ContextualInsight,
        IntentCategory, UrgencyLevel
    )
    META_COGNITIVE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Advanced components not available: {e}")
    META_COGNITIVE_AVAILABLE = False
    
    #Create dummy classes for compatibility
    class ContextProfile:
        def __init__(self, domain="general", intent=None, urgency=None, 
                     complexity_score=0.5, knowledge_level="intermediate",
                     interaction_style="professional", emotional_tone="neutral",
                     uncertainty_areas=None):
            self.domain = domain
            self.intent = intent
            self.urgency = urgency
            self.complexity_score = complexity_score
            self.knowledge_level = knowledge_level
            self.interaction_style = interaction_style
            self.emotional_tone = emotional_tone
            self.uncertainty_areas = uncertainty_areas or []
    
    class ContextualInsight:
        def __init__(self, insight_type="", description="", confidence=0.5,
                     actionable_recommendations=None, evidence=None):
            self.insight_type = insight_type
            self.description = description
            self.confidence = confidence
            self.actionable_recommendations = actionable_recommendations or []
            self.evidence = evidence or []
    
    class CognitiveSnapshot:
        def __init__(self):
            self.timestamp = time.time()
            self.mode = "analytical"
            self.confidence_level = 0.5
    
    class ReasoningTrace:
        def __init__(self, step_id="", reasoning_type="", input_state=None,
                     cognitive_operation="", output_state=None, confidence_change=0,
                     epistemic_update="", meta_commentary="", processing_time=0):
            self.step_id = step_id
            self.reasoning_type = reasoning_type
            self.input_state = input_state or {}
            self.cognitive_operation = cognitive_operation
            self.output_state = output_state or {}
            self.confidence_change = confidence_change
            self.epistemic_update = epistemic_update
            self.meta_commentary = meta_commentary
            self.processing_time = processing_time
    
    class IntentCategory:
        INFORMATION_SEEKING = "information_seeking"
        PROBLEM_SOLVING = "problem_solving"
        CREATIVE_ASSISTANCE = "creative_assistance"
        LEARNING = "learning"
        DECISION_SUPPORT = "decision_support"
        TASK_COMPLETION = "task_completion"
        EXPLORATION = "exploration"
        VALIDATION = "validation"
    
    class UrgencyLevel:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
        BACKGROUND = "background"


class ProcessingMode(Enum):
    """Processing modes for different scenarios."""
    LIGHTNING = "lightning"         #Ultra-fast responses
    BALANCED = "balanced"           #Balance of speed and depth
    DEEP_THINK = "deep_think"      #Maximum depth and analysis
    COLLABORATIVE = "collaborative" #Multi-perspective integration
    CREATIVE = "creative"           #Innovation and creativity focus


class ResponseQuality(Enum):
    """Quality levels for response assessment."""
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"
    INADEQUATE = "inadequate"


@dataclass
class ProcessingSession:
    """Complete processing session with all metadata."""
    session_id: str
    query: str
    context_profile: Optional[ContextProfile] = None
    cognitive_snapshots: List[CognitiveSnapshot] = field(default_factory=list)
    reasoning_traces: List[ReasoningTrace] = field(default_factory=list)
    contextual_insights: List[ContextualInsight] = field(default_factory=list)
    
    #Processing metadata
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_processing_time: float = 0.0
    
    #Quality assessment
    response_quality: Optional[ResponseQuality] = None
    confidence_score: float = 0.5
    uncertainty_areas: List[str] = field(default_factory=list)
    
    #Tool integration
    tools_used: List[str] = field(default_factory=list)
    tool_effectiveness: Dict[str, float] = field(default_factory=dict)
    
    #Learning outcomes
    lessons_learned: List[str] = field(default_factory=list)
    improvement_opportunities: List[str] = field(default_factory=list)


class UltimateAIAssistant:
    """
    The ultimate AI assistant that combines all advanced capabilities:
    - Meta-cognitive awareness and self-monitoring
    - Sophisticated contextual understanding
    - Advanced reasoning with uncertainty handling
    - Adaptive learning and continuous improvement
    - Human-like thinking patterns
    """
    
    def __init__(self, llm_manager=None, memory_manager=None, config_manager=None):
        """Initialize the ultimate AI assistant."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.config_manager = config_manager
        
        #Initialize advanced components
        if META_COGNITIVE_AVAILABLE:
            self.meta_cognitive_engine = MetaCognitiveEngine(llm_manager, memory_manager)
            self.contextual_analyzer = AdvancedContextualAnalyzer(llm_manager, memory_manager)
        else:
            self.meta_cognitive_engine = None
            self.contextual_analyzer = None
            self.logger.warning("Running in compatibility mode without advanced components")
        
        #Core capabilities
        self.name = "Ultimate AI Assistant"
        self.description = "Advanced AI assistant with meta-cognitive awareness and sophisticated reasoning"
        self.version = "4.0.0"
        
        #Processing state
        self.current_session: Optional[ProcessingSession] = None
        self.processing_history: List[ProcessingSession] = []
        self.active_processing_mode = ProcessingMode.BALANCED
        
        #Learning and adaptation
        self.learned_patterns = {}
        self.strategy_effectiveness = {}
        self.user_interaction_patterns = {}
        
        #Performance tracking
        self.performance_stats = {
            "total_queries": 0,
            "successful_responses": 0,
            "average_processing_time": 0.0,
            "average_confidence": 0.0,
            "learning_adaptations": 0,
            "meta_cognitive_insights": 0,
            "contextual_adaptations": 0
        }
        
        #Tool integration
        self.available_tools = {}
        self.tool_usage_stats = {}
        
        self.logger.info("Ultimate AI Assistant initialized with advanced capabilities")
    
    def __call__(self, query: str, available_tools=None, context_hints=None) -> str:
        """Main entry point for query processing."""
        return self.process_query_ultimate(query, available_tools, context_hints)
    
    def process_query_ultimate(self, query: str, available_tools=None, context_hints=None) -> str:
        """
        Ultimate query processing with full AI assistant capabilities.
        
        This method orchestrates all advanced components for optimal response generation.
        """
        #Initialize processing session
        session = ProcessingSession(
            session_id=str(uuid.uuid4()),
            query=query
        )
        self.current_session = session
        
        try:
            #Phase 1: Contextual Analysis
            self.logger.info("Phase 1: Advanced contextual analysis")
            if self.contextual_analyzer:
                session.context_profile = self.contextual_analyzer.analyze_context(
                    query, context_hints or {}
                )
                session.contextual_insights = self.contextual_analyzer.generate_contextual_insights(
                    session.context_profile
                )
                self.performance_stats["contextual_adaptations"] += 1
            
            #Phase 2: Meta-Cognitive Assessment
            self.logger.info("Phase 2: Meta-cognitive query assessment")
            if self.meta_cognitive_engine:
                complexity_analysis = self.meta_cognitive_engine.assess_query_complexity(
                    query, context_hints or {}
                )
                cognitive_strategy = self.meta_cognitive_engine.select_cognitive_strategy(
                    complexity_analysis, context_hints or {}
                )
                
                #Create initial cognitive snapshot
                initial_snapshot = self.meta_cognitive_engine.create_cognitive_snapshot()
                session.cognitive_snapshots.append(initial_snapshot)
                self.performance_stats["meta_cognitive_insights"] += 1
            
            #Phase 3: Processing Mode Selection
            session.processing_mode = self._select_processing_mode(session)
            self.logger.info(f"Selected processing mode: {session.processing_mode.value}")
            
            #Phase 4: Advanced Reasoning
            self.logger.info("Phase 4: Advanced reasoning and analysis")
            reasoning_result = self._perform_advanced_reasoning(session, available_tools)
            
            #Phase 5: Response Generation
            self.logger.info("Phase 5: Contextually optimized response generation")
            response = self._generate_ultimate_response(session, reasoning_result, available_tools)
            
            #Phase 6: Quality Assessment and Learning
            self.logger.info("Phase 6: Response quality assessment and learning")
            self._assess_response_quality(session, response)
            self._extract_learning_insights(session)
            
            #Finalize session
            session.end_time = time.time()
            session.total_processing_time = session.end_time - session.start_time
            self.processing_history.append(session)
            
            #Update performance stats
            self._update_performance_stats(session)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in ultimate processing: {e}")
            self.logger.error(traceback.format_exc())
            
            #Fallback processing
            return self._fallback_processing(query, available_tools)
        finally:
            self.current_session = None
    
    def _select_processing_mode(self, session: ProcessingSession) -> ProcessingMode:
        """Select optimal processing mode based on context and requirements."""
        if not session.context_profile:
            return ProcessingMode.BALANCED
        
        profile = session.context_profile
        
        #Ultra-urgent queries
        if profile.urgency in [UrgencyLevel.CRITICAL]:
            return ProcessingMode.LIGHTNING
        
        #High complexity queries
        if profile.complexity_score > 0.8:
            return ProcessingMode.DEEP_THINK
        
        #Creative tasks
        if profile.intent == IntentCategory.CREATIVE_ASSISTANCE:
            return ProcessingMode.CREATIVE
        
        #Multiple perspectives needed
        if len(profile.related_topics) > 3 or "comparative" in str(profile.intent):
            return ProcessingMode.COLLABORATIVE
        
        return ProcessingMode.BALANCED
    
    def _perform_advanced_reasoning(self, session: ProcessingSession, available_tools=None) -> Dict[str, Any]:
        """Perform advanced reasoning based on processing mode and context."""
        reasoning_result = {
            "sub_questions": [],
            "analysis_steps": [],
            "synthesis": "",
            "confidence_assessment": {},
            "tool_recommendations": [],
            "uncertainty_tracking": {},
            "meta_commentary": []
        }
        
        profile = session.context_profile
        mode = session.processing_mode
        
        try:
            #Generate sub-questions based on complexity and mode
            if mode in [ProcessingMode.DEEP_THINK, ProcessingMode.COLLABORATIVE]:
                reasoning_result["sub_questions"] = self._generate_sub_questions(session.query, profile)
            
            #Perform analysis steps
            for i, sub_question in enumerate(reasoning_result["sub_questions"][:5]):  #Limit to 5
                step_result = self._analyze_sub_question(sub_question, profile, available_tools)
                reasoning_result["analysis_steps"].append(step_result)
                
                #Create reasoning trace
                if self.meta_cognitive_engine:
                    trace = ReasoningTrace(
                        step_id=f"step_{i+1}",
                        reasoning_type="sub_question_analysis",
                        input_state={"sub_question": sub_question},
                        cognitive_operation="analysis",
                        output_state=step_result,
                        confidence_change=step_result.get("confidence", 0.5),
                        epistemic_update=step_result.get("epistemic_update", "analysis_complete"),
                        meta_commentary=f"Analyzed sub-question {i+1} with {step_result.get('confidence', 0.5):.2f} confidence",
                        processing_time=time.time() - session.start_time
                    )
                    session.reasoning_traces.append(trace)
            
            #Synthesize findings
            reasoning_result["synthesis"] = self._synthesize_analysis(
                reasoning_result["analysis_steps"], profile, mode
            )
            
            #Assess overall confidence
            reasoning_result["confidence_assessment"] = self._assess_reasoning_confidence(
                reasoning_result, session
            )
            
            #Generate meta-commentary
            if self.meta_cognitive_engine:
                reasoning_result["meta_commentary"] = self.meta_cognitive_engine.generate_meta_commentary(
                    session.reasoning_traces
                )
            
        except Exception as e:
            self.logger.error(f"Error in advanced reasoning: {e}")
            reasoning_result["error"] = str(e)
        
        return reasoning_result
    
    def _generate_sub_questions(self, query: str, profile: Optional[ContextProfile]) -> List[str]:
        """Generate relevant sub-questions for deeper analysis."""
        sub_questions = []
        
        if not self.llm_manager:
            return ["What are the key components of this query?"]
        
        try:
            #Create prompt for sub-question generation
            messages = [
                {
                    "role": "user",
                    "content": f"""Given the following query, generate 3-5 specific sub-questions that would help provide a comprehensive answer.

Query: {query}

Context: {profile.domain if profile else 'general'} domain, {profile.complexity_score if profile else 0.5} complexity

Generate sub-questions that:
1. Break down the main query into components
2. Address potential edge cases or considerations
3. Explore implementation or practical aspects
4. Consider alternative approaches or perspectives

Respond with just the sub-questions, one per line, numbered."""
                }
            ]
            
            response = self.llm_manager.chat(messages)
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            #Parse sub-questions
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    #Remove numbering
                    if '. ' in line:
                        line = line.split('. ', 1)[1]
                    sub_questions.append(line)
            
        except Exception as e:
            self.logger.error(f"Error generating sub-questions: {e}")
            #Fallback sub-questions
            sub_questions = [
                "What are the main components or aspects to consider?",
                "What are the potential challenges or limitations?",
                "What are the best practices or recommended approaches?"
            ]
        
        return sub_questions[:5]  #Limit to 5
    
    def _analyze_sub_question(self, sub_question: str, profile: Optional[ContextProfile], available_tools=None) -> Dict[str, Any]:
        """Analyze a specific sub-question."""
        step_result = {
            "sub_question": sub_question,
            "analysis": "",
            "confidence": 0.5,
            "tools_considered": [],
            "epistemic_update": "analyzed",
            "insights": []
        }
        
        if not self.llm_manager:
            step_result["analysis"] = f"Analysis needed for: {sub_question}"
            return step_result
        
        try:
            #Determine if tools should be used
            tool_recommendations = self._recommend_tools_for_question(sub_question, available_tools)
            step_result["tools_considered"] = tool_recommendations
            
            #Create analysis prompt
            context_info = ""
            if profile:
                context_info = f"""
Context Information:
- Domain: {profile.domain}
- Complexity: {profile.complexity_score:.2f}
- Intent: {profile.intent.value if hasattr(profile.intent, 'value') else profile.intent}
- Knowledge Level: {profile.knowledge_level}
"""
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Analyze the following sub-question thoroughly:

{sub_question}

{context_info}

Provide:
1. A clear, detailed analysis
2. Key insights or considerations
3. Confidence level (0.0-1.0) in your analysis
4. Any uncertainties or limitations

Be specific and actionable in your response."""
                }
            ]
            
            response = self.llm_manager.chat(messages)
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            step_result["analysis"] = content
            
            #Extract confidence if mentioned
            confidence_match = None
            import re
            confidence_patterns = [
                r'confidence[:\s]*([0-9.]+)',
                r'confident[:\s]*([0-9.]+)',
                r'certainty[:\s]*([0-9.]+)'
            ]
            
            for pattern in confidence_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    try:
                        confidence_match = float(match.group(1))
                        if confidence_match > 1.0:
                            confidence_match = confidence_match / 100.0  #Convert percentage
                        break
                    except ValueError:
                        continue
            
            if confidence_match:
                step_result["confidence"] = max(0.0, min(1.0, confidence_match))
            else:
                #Estimate confidence based on response characteristics
                if "uncertain" in content.lower() or "unclear" in content.lower():
                    step_result["confidence"] = 0.4
                elif "definitely" in content.lower() or "clearly" in content.lower():
                    step_result["confidence"] = 0.8
                else:
                    step_result["confidence"] = 0.6
        
        except Exception as e:
            self.logger.error(f"Error analyzing sub-question: {e}")
            step_result["analysis"] = f"Error in analysis: {str(e)}"
            step_result["confidence"] = 0.3
        
        return step_result
    
    def _recommend_tools_for_question(self, question: str, available_tools=None) -> List[str]:
        """Recommend appropriate tools for a specific question."""
        if not available_tools:
            return []
        
        recommendations = []
        question_lower = question.lower()
        
        #Simple tool recommendation logic
        tool_keywords = {
            "screenshot": ["screen", "display", "visual", "ui", "interface"],
            "file_search": ["file", "search", "find", "locate"],
            "grep_search": ["search", "find", "text", "content"],
            "code_analysis": ["code", "function", "class", "method", "implementation"]
        }
        
        for tool_name, keywords in tool_keywords.items():
            if tool_name in available_tools and any(keyword in question_lower for keyword in keywords):
                recommendations.append(tool_name)
        
        return recommendations
    
    def _synthesize_analysis(self, analysis_steps: List[Dict[str, Any]], profile: Optional[ContextProfile], mode: ProcessingMode) -> str:
        """Synthesize analysis results into coherent insights."""
        if not analysis_steps:
            return "No specific analysis steps were completed."
        
        if not self.llm_manager:
            return "Synthesis requires LLM integration."
        
        try:
            #Prepare synthesis prompt
            analyses_text = "\n\n".join([
                f"Sub-question: {step['sub_question']}\nAnalysis: {step['analysis']}\nConfidence: {step['confidence']:.2f}"
                for step in analysis_steps
            ])
            
            mode_guidance = {
                ProcessingMode.LIGHTNING: "Provide a concise, actionable synthesis focusing on immediate solutions.",
                ProcessingMode.BALANCED: "Provide a well-structured synthesis that balances depth with clarity.",
                ProcessingMode.DEEP_THINK: "Provide a comprehensive, detailed synthesis with thorough analysis.",
                ProcessingMode.CREATIVE: "Provide an innovative synthesis that explores creative possibilities.",
                ProcessingMode.COLLABORATIVE: "Provide a synthesis that integrates multiple perspectives and approaches."
            }
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Synthesize the following analysis results into a coherent, insightful response:

{analyses_text}

Processing Mode: {mode.value}
Guidance: {mode_guidance.get(mode, '')}

Create a synthesis that:
1. Integrates all analysis results
2. Identifies key patterns and insights
3. Provides actionable conclusions
4. Acknowledges any uncertainties
5. Offers practical next steps

Focus on clarity, usefulness, and actionability."""
                }
            ]
            
            response = self.llm_manager.chat(messages)
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error in synthesis: {e}")
            return f"Synthesis error: {str(e)}"
    
    def _assess_reasoning_confidence(self, reasoning_result: Dict[str, Any], session: ProcessingSession) -> Dict[str, Any]:
        """Assess confidence in the reasoning process."""
        confidence_assessment = {
            "overall_confidence": 0.5,
            "confidence_breakdown": {},
            "uncertainty_factors": [],
            "confidence_justification": ""
        }
        
        #Calculate confidence from analysis steps
        step_confidences = [step.get("confidence", 0.5) for step in reasoning_result["analysis_steps"]]
        if step_confidences:
            confidence_assessment["overall_confidence"] = sum(step_confidences) / len(step_confidences)
        
        #Assess different aspects
        confidence_assessment["confidence_breakdown"] = {
            "analysis_quality": confidence_assessment["overall_confidence"],
            "synthesis_coherence": 0.7,  #Default assumption
            "completeness": min(1.0, len(reasoning_result["analysis_steps"]) / 3),
            "tool_integration": 0.8 if reasoning_result.get("tool_recommendations") else 0.5
        }
        
        #Identify uncertainty factors
        uncertainty_factors = []
        if confidence_assessment["overall_confidence"] < 0.6:
            uncertainty_factors.append("low_analysis_confidence")
        
        if len(reasoning_result["analysis_steps"]) < 2:
            uncertainty_factors.append("insufficient_analysis_depth")
        
        if session.context_profile and len(session.context_profile.uncertainty_areas) > 0:
            uncertainty_factors.append("contextual_uncertainties")
        
        confidence_assessment["uncertainty_factors"] = uncertainty_factors
        
        #Generate justification
        confidence_level = confidence_assessment["overall_confidence"]
        if confidence_level > 0.8:
            confidence_assessment["confidence_justification"] = "High confidence based on thorough analysis and clear evidence."
        elif confidence_level > 0.6:
            confidence_assessment["confidence_justification"] = "Good confidence with some minor uncertainties."
        elif confidence_level > 0.4:
            confidence_assessment["confidence_justification"] = "Moderate confidence - some significant uncertainties present."
        else:
            confidence_assessment["confidence_justification"] = "Lower confidence due to analysis limitations or uncertainties."
        
        return confidence_assessment
    
    def _generate_ultimate_response(self, session: ProcessingSession, reasoning_result: Dict[str, Any], available_tools=None) -> str:
        """Generate the ultimate response using all available insights."""
        if not self.llm_manager:
            return self._generate_fallback_response(session, reasoning_result)
        
        try:
            #Prepare comprehensive context
            context_summary = ""
            if session.context_profile:
                context_summary = f"""
Context Profile:
- Domain: {session.context_profile.domain}
- Intent: {session.context_profile.intent.value if hasattr(session.context_profile.intent, 'value') else session.context_profile.intent}
- Urgency: {session.context_profile.urgency.value if hasattr(session.context_profile.urgency, 'value') else session.context_profile.urgency}
- Complexity: {session.context_profile.complexity_score:.2f}
- Knowledge Level: {session.context_profile.knowledge_level}
- Interaction Style: {session.context_profile.interaction_style}
"""
            
            #Prepare insights summary
            insights_summary = ""
            if session.contextual_insights:
                insights_summary = "\n".join([
                    f"- {insight.description}" for insight in session.contextual_insights[:3]
                ])
            
            #Prepare reasoning summary
            reasoning_summary = reasoning_result.get("synthesis", "")
            confidence_info = reasoning_result.get("confidence_assessment", {})
            
            #Determine response strategy
            response_strategy = ""
            if self.contextual_analyzer and session.context_profile:
                strategy = self.contextual_analyzer.adapt_response_strategy(
                    session.context_profile, session.contextual_insights
                )
                response_strategy = f"""
Response Strategy:
- Tone: {strategy.get('tone', 'professional')}
- Detail Level: {strategy.get('detail_level', 'medium')}
- Structure: {strategy.get('structure', 'standard')}
- Include Examples: {strategy.get('examples', False)}
- Technical Depth: {strategy.get('technical_depth', 'medium')}
"""
            
            #Create ultimate response prompt
            messages = [
                {
                    "role": "user",
                    "content": f"""Create the ultimate response to this query using all available analysis and insights:

Original Query: {session.query}

{context_summary}

Key Insights:
{insights_summary}

Reasoning Analysis:
{reasoning_summary}

Confidence Assessment: {confidence_info.get('overall_confidence', 0.5):.2f}
{confidence_info.get('confidence_justification', '')}

{response_strategy}

Create a response that:
1. Directly addresses the original query
2. Incorporates all relevant insights and analysis
3. Matches the appropriate tone and style
4. Provides actionable information
5. Acknowledges uncertainties appropriately
6. Is well-structured and clear
7. Includes practical next steps when relevant

Make this the best possible response given all available information."""
                }
            ]
            
            response = self.llm_manager.chat(messages)
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            #Enhance response with meta-cognitive insights if available
            if self.meta_cognitive_engine and session.reasoning_traces:
                meta_commentary = self.meta_cognitive_engine.generate_meta_commentary(session.reasoning_traces)
                if meta_commentary.get("meta_insights"):
                    meta_insights_text = "\n".join(meta_commentary["meta_insights"][:2])  #Limit to 2
                    content += f"\n\n**Meta-Analysis:** {meta_insights_text}"
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error generating ultimate response: {e}")
            return self._generate_fallback_response(session, reasoning_result)
    
    def _generate_fallback_response(self, session: ProcessingSession, reasoning_result: Dict[str, Any]) -> str:
        """Generate a fallback response when LLM is not available."""
        response_parts = [f"Analysis of: {session.query}"]
        
        if reasoning_result.get("analysis_steps"):
            response_parts.append("\nKey Analysis Points:")
            for i, step in enumerate(reasoning_result["analysis_steps"][:3], 1):
                response_parts.append(f"{i}. {step['sub_question']}")
                if step.get("analysis"):
                    response_parts.append(f"   {step['analysis'][:200]}...")
        
        if reasoning_result.get("synthesis"):
            response_parts.append(f"\nSynthesis: {reasoning_result['synthesis']}")
        
        if session.context_profile:
            response_parts.append(f"\nContext: {session.context_profile.domain} domain, complexity {session.context_profile.complexity_score:.2f}")
        
        return "\n".join(response_parts)
    
    def _assess_response_quality(self, session: ProcessingSession, response: str):
        """Assess the quality of the generated response."""
        quality_metrics = {
            "length": len(response),
            "structure": "good" if "\n" in response else "basic",
            "completeness": "good" if len(response) > 200 else "basic",
            "confidence": session.confidence_score
        }
        
        #Simple quality assessment
        if quality_metrics["length"] > 500 and quality_metrics["structure"] == "good" and quality_metrics["confidence"] > 0.7:
            session.response_quality = ResponseQuality.EXCELLENT
        elif quality_metrics["length"] > 200 and quality_metrics["confidence"] > 0.5:
            session.response_quality = ResponseQuality.GOOD
        else:
            session.response_quality = ResponseQuality.SATISFACTORY
        
        session.confidence_score = quality_metrics["confidence"]
    
    def _extract_learning_insights(self, session: ProcessingSession):
        """Extract learning insights from the processing session."""
        lessons = []
        improvements = []
        
        #Processing time insights
        if session.total_processing_time > 30:
            improvements.append("Consider optimizing processing time for similar queries")
        
        #Confidence insights
        if session.confidence_score < 0.5:
            improvements.append("Improve confidence through better analysis or additional information")
        
        #Context insights
        if session.context_profile and len(session.context_profile.uncertainty_areas) > 2:
            improvements.append("Address contextual uncertainties more effectively")
        
        #Tool usage insights
        if session.tools_used:
            lessons.append(f"Successfully used tools: {', '.join(session.tools_used)}")
        
        session.lessons_learned = lessons
        session.improvement_opportunities = improvements
        
        self.performance_stats["learning_adaptations"] += 1
    
    def _update_performance_stats(self, session: ProcessingSession):
        """Update performance statistics based on session results."""
        self.performance_stats["total_queries"] += 1
        
        if session.response_quality in [ResponseQuality.EXCELLENT, ResponseQuality.GOOD]:
            self.performance_stats["successful_responses"] += 1
        
        #Update averages
        total = self.performance_stats["total_queries"]
        self.performance_stats["average_processing_time"] = (
            (self.performance_stats["average_processing_time"] * (total - 1) + session.total_processing_time) / total
        )
        
        self.performance_stats["average_confidence"] = (
            (self.performance_stats["average_confidence"] * (total - 1) + session.confidence_score) / total
        )
    
    def _fallback_processing(self, query: str, available_tools=None) -> str:
        """Fallback processing when advanced components fail."""
        self.logger.info("Using fallback processing mode")
        
        if self.llm_manager:
            try:
                messages = [
                    {
                        "role": "user",
                        "content": f"Please provide a helpful response to this query: {query}"
                    }
                ]
                
                response = self.llm_manager.chat(messages)
                if isinstance(response, dict) and 'content' in response:
                    return response['content']
                elif hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
                    
            except Exception as e:
                self.logger.error(f"Fallback LLM processing failed: {e}")
        
        return f"I understand you're asking about: {query}\n\nI'm currently operating in limited mode, but I'm here to help as best I can."
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive capabilities information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "advanced_components": {
                "meta_cognitive_engine": self.meta_cognitive_engine is not None,
                "contextual_analyzer": self.contextual_analyzer is not None,
                "llm_integration": self.llm_manager is not None,
                "memory_integration": self.memory_manager is not None
            },
            "processing_modes": [mode.value for mode in ProcessingMode],
            "supported_features": [
                "meta_cognitive_awareness",
                "contextual_analysis",
                "advanced_reasoning",
                "adaptive_learning",
                "quality_assessment",
                "uncertainty_handling",
                "tool_integration",
                "performance_optimization"
            ],
            "performance_stats": self.performance_stats.copy()
        }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent session history."""
        recent_sessions = self.processing_history[-limit:]
        return [
            {
                "session_id": session.session_id,
                "query": session.query[:100] + "..." if len(session.query) > 100 else session.query,
                "processing_mode": session.processing_mode.value,
                "processing_time": session.total_processing_time,
                "response_quality": session.response_quality.value if session.response_quality else "unknown",
                "confidence_score": session.confidence_score,
                "tools_used": session.tools_used
            }
            for session in recent_sessions
        ]


def register(llm_manager=None, atlas_app=None, agent_manager=None, **kwargs):
    """
    Register the Ultimate AI Assistant.
    
    This is the main entry point for the most advanced AI assistant capabilities.
    """
    try:
        #Get additional components from kwargs
        memory_manager = kwargs.get('memory_manager')
        config_manager = kwargs.get('config_manager')
        
        #Initialize the ultimate assistant
        assistant = UltimateAIAssistant(llm_manager, memory_manager, config_manager)
        
        #Integration with Atlas helper mode
        if atlas_app and hasattr(atlas_app, 'register_helper_tool'):
            atlas_app.register_helper_tool('ultimate_thinking', assistant)
        
        #Integration with agent manager
        if agent_manager and hasattr(agent_manager, 'register_tool'):
            agent_manager.register_tool('ultimate_ai_assistant', assistant)
        
        logging.info("Ultimate AI Assistant registered successfully")
        return assistant
        
    except Exception as e:
        logging.error(f"Failed to register Ultimate AI Assistant: {e}")
        logging.error(traceback.format_exc())
        
        #Return a simple fallback
        class FallbackAssistant:
            def __init__(self):
                self.name = "Fallback Assistant"
                self.description = "Basic assistant functionality"
            
            def __call__(self, query: str, available_tools=None):
                return f"I understand you're asking: {query}\n\nI'm operating in basic mode due to initialization issues."
        
        return FallbackAssistant()


#Export the main class for direct usage
__all__ = ['UltimateAIAssistant', 'ProcessingMode', 'ResponseQuality', 'register']
