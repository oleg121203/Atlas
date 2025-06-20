"""
Meta-Cognitive AI Engine for Atlas

This module implements advanced meta-cognitive capabilities based on real AI assistant experience,
including self-awareness, reasoning about reasoning, and adaptive cognitive strategies.

Key features:
- Meta-cognitive self-monitoring
- Epistemic reasoning (reasoning about knowledge)
- Adaptive cognitive strategy selection
- Self-correction mechanisms
- Uncertainty quantification
- Knowledge gap detection
- Contextual awareness modulation
"""

import logging
import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import math
from collections import defaultdict, deque


class CognitiveMode(Enum):
    """Different cognitive processing modes."""
    ANALYTICAL = "analytical"           #Deep logical analysis
    INTUITIVE = "intuitive"            #Pattern recognition and heuristics
    REFLECTIVE = "reflective"          #Self-examination and meta-analysis
    CREATIVE = "creative"              #Novel solution generation
    COLLABORATIVE = "collaborative"    #Multi-perspective integration
    SYSTEMATIC = "systematic"          #Methodical step-by-step processing


class EpistemicState(Enum):
    """Knowledge state awareness."""
    CERTAIN = "certain"                #High confidence in knowledge
    UNCERTAIN = "uncertain"            #Acknowledged uncertainty
    UNKNOWN = "unknown"                #Recognized knowledge gap
    CONFLICTED = "conflicted"          #Contradictory information
    PARTIAL = "partial"                #Incomplete understanding
    EVOLVING = "evolving"              #Understanding in flux


@dataclass
class CognitiveSnapshot:
    """Snapshot of current cognitive state."""
    timestamp: float
    mode: CognitiveMode
    epistemic_state: EpistemicState
    confidence_level: float
    attention_focus: List[str]
    active_strategies: List[str]
    processing_depth: int
    meta_awareness: Dict[str, Any]
    uncertainty_tracking: Dict[str, float]


@dataclass
class ReasoningTrace:
    """Detailed trace of reasoning process."""
    step_id: str
    reasoning_type: str
    input_state: Dict[str, Any]
    cognitive_operation: str
    output_state: Dict[str, Any]
    confidence_change: float
    epistemic_update: str
    meta_commentary: str
    processing_time: float


class MetaCognitiveEngine:
    """
    Advanced meta-cognitive engine that monitors and adapts thinking processes.
    
    This engine implements sophisticated self-awareness and reasoning about reasoning,
    drawing from real AI assistant experience in handling complex queries.
    """
    
    def __init__(self, llm_manager=None, memory_manager=None):
        """Initialize the meta-cognitive engine."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        
        #Core cognitive state
        self.current_mode = CognitiveMode.ANALYTICAL
        self.epistemic_state = EpistemicState.UNCERTAIN
        self.confidence_level = 0.5
        self.processing_depth = 1
        
        #Meta-cognitive tracking
        self.cognitive_history = deque(maxlen=50)
        self.reasoning_traces = []
        self.strategy_effectiveness = defaultdict(lambda: {"success": 0, "total": 0})
        self.uncertainty_map = {}
        self.knowledge_gaps = set()
        
        #Adaptive parameters
        self.attention_weights = defaultdict(float)
        self.strategy_preferences = {}
        self.confidence_calibration = {}
        
        #Performance metrics
        self.meta_stats = {
            "total_queries": 0,
            "successful_adaptations": 0,
            "knowledge_updates": 0,
            "uncertainty_resolutions": 0,
            "mode_switches": 0
        }
        
        self.logger.info("Meta-cognitive engine initialized with adaptive reasoning capabilities")
    
    def assess_query_complexity(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess the complexity and cognitive demands of a query.
        
        Returns detailed analysis including:
        - Cognitive load estimation
        - Required reasoning types
        - Knowledge domains involved
        - Uncertainty levels expected
        """
        context = context or {}
        
        complexity_analysis = {
            "cognitive_load": 1,
            "reasoning_types": [],
            "knowledge_domains": [],
            "uncertainty_factors": [],
            "meta_requirements": [],
            "recommended_mode": CognitiveMode.ANALYTICAL,
            "processing_strategy": "standard"
        }
        
        #Analyze query structure and content
        query_lower = query.lower()
        word_count = len(query.split())
        sentence_count = len([s for s in query.split('.') if s.strip()])
        
        #Complexity indicators
        complexity_indicators = {
            "multi_part": bool(re.search(r'\b(and|also|additionally|furthermore|moreover)\b', query_lower)),
            "conditional": bool(re.search(r'\b(if|when|unless|provided|assuming)\b', query_lower)),
            "comparative": bool(re.search(r'\b(compare|contrast|versus|better|worse|different)\b', query_lower)),
            "causal": bool(re.search(r'\b(why|because|cause|reason|due to|result)\b', query_lower)),
            "temporal": bool(re.search(r'\b(before|after|during|while|when|then)\b', query_lower)),
            "modal": bool(re.search(r'\b(could|should|might|may|would|can)\b', query_lower)),
            "meta": bool(re.search(r'\b(think|analyze|consider|evaluate|assess)\b', query_lower))
        }
        
        #Calculate cognitive load
        base_load = min(5, max(1, word_count / 10))
        complexity_multiplier = 1 + sum(complexity_indicators.values()) * 0.3
        complexity_analysis["cognitive_load"] = min(5, base_load * complexity_multiplier)
        
        #Determine reasoning types needed
        if complexity_indicators["causal"]:
            complexity_analysis["reasoning_types"].append("causal")
        if complexity_indicators["comparative"]:
            complexity_analysis["reasoning_types"].append("comparative")
        if complexity_indicators["conditional"]:
            complexity_analysis["reasoning_types"].append("conditional")
        if complexity_indicators["meta"]:
            complexity_analysis["reasoning_types"].append("meta-cognitive")
        
        #Identify knowledge domains
        domain_keywords = {
            "technical": ["code", "programming", "system", "algorithm", "api", "database"],
            "analytical": ["analyze", "evaluate", "assess", "examine", "investigate"],
            "creative": ["create", "design", "improve", "innovate", "generate"],
            "strategic": ["plan", "strategy", "approach", "method", "framework"],
            "troubleshooting": ["fix", "debug", "solve", "error", "problem", "issue"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                complexity_analysis["knowledge_domains"].append(domain)
        
        #Recommend cognitive mode
        if complexity_indicators["meta"] or "meta-cognitive" in complexity_analysis["reasoning_types"]:
            complexity_analysis["recommended_mode"] = CognitiveMode.REFLECTIVE
        elif complexity_indicators["comparative"] and len(complexity_analysis["knowledge_domains"]) > 1:
            complexity_analysis["recommended_mode"] = CognitiveMode.COLLABORATIVE
        elif "creative" in complexity_analysis["knowledge_domains"]:
            complexity_analysis["recommended_mode"] = CognitiveMode.CREATIVE
        elif complexity_analysis["cognitive_load"] > 3:
            complexity_analysis["recommended_mode"] = CognitiveMode.SYSTEMATIC
        
        #Identify uncertainty factors
        uncertainty_keywords = ["might", "possibly", "unclear", "unknown", "uncertain", "maybe"]
        if any(kw in query_lower for kw in uncertainty_keywords):
            complexity_analysis["uncertainty_factors"].append("explicit_uncertainty")
        
        if not complexity_analysis["knowledge_domains"]:
            complexity_analysis["uncertainty_factors"].append("domain_ambiguity")
        
        #Meta-requirements assessment
        if complexity_analysis["cognitive_load"] > 3:
            complexity_analysis["meta_requirements"].append("iterative_refinement")
        if len(complexity_analysis["reasoning_types"]) > 2:
            complexity_analysis["meta_requirements"].append("strategy_coordination")
        if complexity_indicators["meta"]:
            complexity_analysis["meta_requirements"].append("self_reflection")
        
        return complexity_analysis
    
    def select_cognitive_strategy(self, query_analysis: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Select optimal cognitive strategy based on query analysis and current state.
        
        Uses meta-cognitive awareness to choose the best approach for the given situation.
        """
        context = context or {}
        
        strategy_selection = {
            "primary_mode": query_analysis.get("recommended_mode", CognitiveMode.ANALYTICAL),
            "processing_depth": min(5, max(1, int(query_analysis.get("cognitive_load", 1)))),
            "attention_focus": [],
            "reasoning_sequence": [],
            "uncertainty_handling": "standard",
            "adaptation_triggers": [],
            "success_criteria": {}
        }
        
        #Attention focus based on knowledge domains
        domains = query_analysis.get("knowledge_domains", [])
        for domain in domains:
            weight = self.attention_weights.get(domain, 1.0)
            strategy_selection["attention_focus"].append({
                "domain": domain,
                "weight": weight,
                "priority": min(5, max(1, int(weight * 3)))
            })
        
        #Reasoning sequence based on complexity
        reasoning_types = query_analysis.get("reasoning_types", [])
        if "meta-cognitive" in reasoning_types:
            strategy_selection["reasoning_sequence"].extend([
                "self_assessment",
                "knowledge_gap_identification",
                "strategy_selection_justification"
            ])
        
        if "causal" in reasoning_types:
            strategy_selection["reasoning_sequence"].extend([
                "causal_chain_analysis",
                "mechanism_identification"
            ])
        
        if "comparative" in reasoning_types:
            strategy_selection["reasoning_sequence"].extend([
                "feature_extraction",
                "similarity_analysis",
                "difference_highlighting"
            ])
        
        #Uncertainty handling strategy
        uncertainty_factors = query_analysis.get("uncertainty_factors", [])
        if uncertainty_factors:
            if "explicit_uncertainty" in uncertainty_factors:
                strategy_selection["uncertainty_handling"] = "explicit_tracking"
            elif "domain_ambiguity" in uncertainty_factors:
                strategy_selection["uncertainty_handling"] = "domain_exploration"
            else:
                strategy_selection["uncertainty_handling"] = "confidence_qualification"
        
        #Adaptation triggers
        if query_analysis.get("cognitive_load", 1) > 3:
            strategy_selection["adaptation_triggers"].append("complexity_overload")
        
        if len(reasoning_types) > 2:
            strategy_selection["adaptation_triggers"].append("strategy_coordination_needed")
        
        #Success criteria
        strategy_selection["success_criteria"] = {
            "minimum_confidence": 0.7,
            "knowledge_gap_tolerance": 0.3,
            "reasoning_coherence": 0.8,
            "uncertainty_acknowledgment": True
        }
        
        return strategy_selection
    
    def monitor_cognitive_process(self, step_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor ongoing cognitive process for adaptation needs.
        
        Provides real-time assessment of cognitive performance and adaptation recommendations.
        """
        monitoring_result = {
            "cognitive_health": "good",
            "confidence_trend": "stable",
            "attention_distribution": {},
            "processing_efficiency": 1.0,
            "adaptation_needed": False,
            "recommended_adjustments": [],
            "meta_insights": []
        }
        
        #Assess cognitive load
        current_load = step_info.get("processing_load", self.processing_depth)
        if current_load > 4:
            monitoring_result["cognitive_health"] = "overloaded"
            monitoring_result["recommended_adjustments"].append("reduce_processing_depth")
        elif current_load < 2:
            monitoring_result["cognitive_health"] = "underutilized"
            monitoring_result["recommended_adjustments"].append("increase_processing_depth")
        
        #Track confidence evolution
        current_confidence = step_info.get("confidence", self.confidence_level)
        if hasattr(self, '_last_confidence'):
            confidence_change = current_confidence - self._last_confidence
            if confidence_change < -0.2:
                monitoring_result["confidence_trend"] = "declining"
                monitoring_result["recommended_adjustments"].append("uncertainty_resolution")
            elif confidence_change > 0.2:
                monitoring_result["confidence_trend"] = "improving"
        self._last_confidence = current_confidence
        
        #Analyze attention distribution
        attention_focus = step_info.get("attention_focus", [])
        for focus_item in attention_focus:
            domain = focus_item.get("domain", "unknown")
            weight = focus_item.get("weight", 1.0)
            monitoring_result["attention_distribution"][domain] = weight
        
        #Check for adaptation triggers
        if step_info.get("processing_time", 0) > 30:  #seconds
            monitoring_result["adaptation_needed"] = True
            monitoring_result["recommended_adjustments"].append("processing_optimization")
        
        if step_info.get("uncertainty_level", 0) > 0.7:
            monitoring_result["adaptation_needed"] = True
            monitoring_result["recommended_adjustments"].append("knowledge_gap_addressing")
        
        #Generate meta-insights
        if monitoring_result["cognitive_health"] == "overloaded":
            monitoring_result["meta_insights"].append(
                "Cognitive overload detected - consider breaking down the problem into smaller components"
            )
        
        if monitoring_result["confidence_trend"] == "declining":
            monitoring_result["meta_insights"].append(
                "Confidence declining - may need to gather more information or clarify assumptions"
            )
        
        return monitoring_result
    
    def adapt_cognitive_strategy(self, monitoring_result: Dict[str, Any], current_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt cognitive strategy based on monitoring feedback.
        
        Implements real-time strategy adjustment for optimal performance.
        """
        adapted_strategy = current_strategy.copy()
        adaptations_made = []
        
        #Process recommended adjustments
        adjustments = monitoring_result.get("recommended_adjustments", [])
        
        for adjustment in adjustments:
            if adjustment == "reduce_processing_depth":
                adapted_strategy["processing_depth"] = max(1, adapted_strategy["processing_depth"] - 1)
                adaptations_made.append("Reduced processing depth to manage cognitive load")
            
            elif adjustment == "increase_processing_depth":
                adapted_strategy["processing_depth"] = min(5, adapted_strategy["processing_depth"] + 1)
                adaptations_made.append("Increased processing depth for more thorough analysis")
            
            elif adjustment == "uncertainty_resolution":
                adapted_strategy["uncertainty_handling"] = "explicit_tracking"
                adapted_strategy["reasoning_sequence"].insert(0, "uncertainty_assessment")
                adaptations_made.append("Enhanced uncertainty tracking and resolution")
            
            elif adjustment == "processing_optimization":
                #Switch to more efficient mode if possible
                if adapted_strategy["primary_mode"] == CognitiveMode.SYSTEMATIC:
                    adapted_strategy["primary_mode"] = CognitiveMode.ANALYTICAL
                    adaptations_made.append("Switched to more efficient analytical mode")
            
            elif adjustment == "knowledge_gap_addressing":
                adapted_strategy["reasoning_sequence"].insert(0, "knowledge_gap_identification")
                adaptations_made.append("Added explicit knowledge gap identification")
        
        #Update strategy effectiveness tracking
        if adaptations_made:
            self.meta_stats["successful_adaptations"] += 1
            
        adapted_strategy["adaptations_made"] = adaptations_made
        return adapted_strategy
    
    def generate_meta_commentary(self, reasoning_trace: List[ReasoningTrace]) -> Dict[str, Any]:
        """
        Generate meta-cognitive commentary on the reasoning process.
        
        Provides insights into the quality and characteristics of the reasoning.
        """
        commentary = {
            "reasoning_quality": "good",
            "coherence_score": 0.8,
            "uncertainty_handling": "appropriate",
            "knowledge_integration": "effective",
            "strategic_effectiveness": {},
            "improvement_opportunities": [],
            "meta_insights": [],
            "epistemic_assessment": {}
        }
        
        if not reasoning_trace:
            return commentary
        
        #Analyze reasoning coherence
        confidence_values = [trace.confidence_change for trace in reasoning_trace]
        if confidence_values:
            confidence_variance = sum((c - sum(confidence_values)/len(confidence_values))**2 for c in confidence_values) / len(confidence_values)
            commentary["coherence_score"] = max(0, 1 - confidence_variance)
        
        #Assess uncertainty handling
        uncertainty_mentions = sum(1 for trace in reasoning_trace if "uncertain" in trace.epistemic_update.lower())
        total_steps = len(reasoning_trace)
        if uncertainty_mentions / total_steps > 0.3:
            commentary["uncertainty_handling"] = "thorough"
        elif uncertainty_mentions / total_steps < 0.1:
            commentary["uncertainty_handling"] = "insufficient"
        
        #Evaluate strategic effectiveness
        strategies_used = set(trace.reasoning_type for trace in reasoning_trace)
        for strategy in strategies_used:
            strategy_traces = [t for t in reasoning_trace if t.reasoning_type == strategy]
            avg_confidence_change = sum(t.confidence_change for t in strategy_traces) / len(strategy_traces)
            commentary["strategic_effectiveness"][strategy] = {
                "usage_count": len(strategy_traces),
                "avg_confidence_impact": avg_confidence_change,
                "effectiveness": "high" if avg_confidence_change > 0.1 else "moderate" if avg_confidence_change > 0 else "low"
            }
        
        #Identify improvement opportunities
        if commentary["coherence_score"] < 0.6:
            commentary["improvement_opportunities"].append("Improve reasoning coherence and consistency")
        
        if commentary["uncertainty_handling"] == "insufficient":
            commentary["improvement_opportunities"].append("Better acknowledge and track uncertainty")
        
        low_effectiveness_strategies = [
            strategy for strategy, data in commentary["strategic_effectiveness"].items()
            if data["effectiveness"] == "low"
        ]
        if low_effectiveness_strategies:
            commentary["improvement_opportunities"].append(f"Reconsider use of strategies: {', '.join(low_effectiveness_strategies)}")
        
        #Generate meta-insights
        commentary["meta_insights"].append(f"Reasoning process involved {total_steps} steps across {len(strategies_used)} strategies")
        
        if commentary["coherence_score"] > 0.8:
            commentary["meta_insights"].append("High coherence indicates well-structured reasoning")
        
        if uncertainty_mentions > 0:
            commentary["meta_insights"].append(f"Appropriately acknowledged uncertainty in {uncertainty_mentions} steps")
        
        #Epistemic assessment
        final_trace = reasoning_trace[-1] if reasoning_trace else None
        if final_trace:
            commentary["epistemic_assessment"] = {
                "final_confidence": final_trace.output_state.get("confidence", 0.5),
                "knowledge_state": final_trace.epistemic_update,
                "reasoning_completeness": "complete" if final_trace.confidence_change >= 0 else "incomplete"
            }
        
        return commentary
    
    def create_cognitive_snapshot(self) -> CognitiveSnapshot:
        """Create a snapshot of current cognitive state."""
        return CognitiveSnapshot(
            timestamp=time.time(),
            mode=self.current_mode,
            epistemic_state=self.epistemic_state,
            confidence_level=self.confidence_level,
            attention_focus=list(self.attention_weights.keys()),
            active_strategies=list(self.strategy_preferences.keys()),
            processing_depth=self.processing_depth,
            meta_awareness={
                "total_queries": self.meta_stats["total_queries"],
                "knowledge_gaps": len(self.knowledge_gaps),
                "uncertainty_areas": len(self.uncertainty_map)
            },
            uncertainty_tracking=self.uncertainty_map.copy()
        )
    
    def update_cognitive_state(self, new_information: Dict[str, Any]):
        """Update cognitive state based on new information."""
        #Update confidence level
        if "confidence_update" in new_information:
            self.confidence_level = max(0, min(1, new_information["confidence_update"]))
        
        #Update epistemic state
        if "epistemic_update" in new_information:
            epistemic_info = new_information["epistemic_update"]
            if "uncertain" in epistemic_info.lower():
                self.epistemic_state = EpistemicState.UNCERTAIN
            elif "unknown" in epistemic_info.lower():
                self.epistemic_state = EpistemicState.UNKNOWN
            elif "certain" in epistemic_info.lower():
                self.epistemic_state = EpistemicState.CERTAIN
        
        #Update knowledge gaps
        if "knowledge_gaps" in new_information:
            self.knowledge_gaps.update(new_information["knowledge_gaps"])
        
        #Update uncertainty map
        if "uncertainty_updates" in new_information:
            self.uncertainty_map.update(new_information["uncertainty_updates"])
        
        #Store cognitive snapshot
        snapshot = self.create_cognitive_snapshot()
        self.cognitive_history.append(snapshot)
        
        self.meta_stats["knowledge_updates"] += 1
    
    def get_meta_cognitive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of meta-cognitive engine."""
        return {
            "current_state": {
                "mode": self.current_mode.value,
                "epistemic_state": self.epistemic_state.value,
                "confidence_level": self.confidence_level,
                "processing_depth": self.processing_depth
            },
            "performance_metrics": self.meta_stats.copy(),
            "knowledge_status": {
                "known_domains": list(self.attention_weights.keys()),
                "knowledge_gaps": len(self.knowledge_gaps),
                "uncertainty_areas": len(self.uncertainty_map)
            },
            "adaptive_capabilities": {
                "strategy_effectiveness_tracking": len(self.strategy_effectiveness),
                "cognitive_history_length": len(self.cognitive_history),
                "adaptation_success_rate": (
                    self.meta_stats["successful_adaptations"] / max(1, self.meta_stats["total_queries"])
                )
            }
        }
