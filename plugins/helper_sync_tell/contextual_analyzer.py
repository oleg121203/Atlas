"""
Advanced Contextual Analysis Engine

This module implements sophisticated contextual understanding and adaptation
based on real AI assistant experience in handling diverse user needs.

Key features:
- Multi-dimensional context modeling
- Dynamic context adaptation
- Cross-domain knowledge integration
- User intent inference
- Contextual memory and learning
- Situation-aware response optimization
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import time


class ContextDimension(Enum):
    """Different dimensions of context analysis."""
    DOMAIN = "domain"                   # Technical/business domain
    INTENT = "intent"                   # User's underlying goal
    URGENCY = "urgency"                 # Time sensitivity
    COMPLEXITY = "complexity"           # Problem complexity level
    INTERACTION_STYLE = "interaction_style"  # Preferred communication style
    KNOWLEDGE_LEVEL = "knowledge_level"      # User's expertise level
    EMOTIONAL_TONE = "emotional_tone"        # Emotional context
    CULTURAL = "cultural"               # Cultural considerations


class IntentCategory(Enum):
    """Categories of user intent."""
    INFORMATION_SEEKING = "information_seeking"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE_ASSISTANCE = "creative_assistance"
    LEARNING = "learning"
    DECISION_SUPPORT = "decision_support"
    TASK_COMPLETION = "task_completion"
    EXPLORATION = "exploration"
    VALIDATION = "validation"


class UrgencyLevel(Enum):
    """Levels of urgency."""
    CRITICAL = "critical"      # Immediate attention needed
    HIGH = "high"             # Prompt response required
    MEDIUM = "medium"         # Standard response time
    LOW = "low"               # Can be handled leisurely
    BACKGROUND = "background" # Non-time-sensitive


@dataclass
class ContextProfile:
    """Comprehensive context profile for a query or interaction."""
    domain: str = "general"
    intent: IntentCategory = IntentCategory.INFORMATION_SEEKING
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    complexity_score: float = 0.5
    knowledge_level: str = "intermediate"
    interaction_style: str = "professional"
    emotional_tone: str = "neutral"
    cultural_factors: List[str] = field(default_factory=list)
    
    # Contextual metadata
    previous_interactions: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence scores
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    uncertainty_areas: List[str] = field(default_factory=list)


@dataclass
class ContextualInsight:
    """Insight derived from contextual analysis."""
    insight_type: str
    description: str
    confidence: float
    actionable_recommendations: List[str]
    evidence: List[str]


class AdvancedContextualAnalyzer:
    """
    Sophisticated contextual analysis engine that understands and adapts to
    multi-dimensional context for optimal response generation.
    """
    
    def __init__(self, llm_manager=None, memory_manager=None):
        """Initialize the contextual analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        
        # Context learning and adaptation
        self.domain_patterns = self._initialize_domain_patterns()
        self.intent_classifiers = self._initialize_intent_classifiers()
        self.style_indicators = self._initialize_style_indicators()
        self.complexity_markers = self._initialize_complexity_markers()
        
        # Contextual memory
        self.context_history = []
        self.learned_patterns = defaultdict(list)
        self.user_preferences = {}
        self.domain_expertise = {}
        
        # Performance tracking
        self.analysis_stats = {
            "total_analyses": 0,
            "successful_adaptations": 0,
            "pattern_recognitions": 0,
            "context_predictions": 0
        }
        
        self.logger.info("Advanced contextual analyzer initialized")
    
    def _initialize_domain_patterns(self) -> Dict[str, List[str]]:
        """Initialize domain recognition patterns."""
        return {
            "software_development": [
                "code", "programming", "debug", "api", "framework", "library",
                "algorithm", "function", "variable", "class", "method", "bug",
                "repository", "git", "deploy", "database", "frontend", "backend"
            ],
            "data_science": [
                "data", "model", "analysis", "statistics", "machine learning",
                "neural network", "dataset", "visualization", "pandas", "numpy",
                "prediction", "classification", "regression", "clustering"
            ],
            "business_strategy": [
                "strategy", "market", "business", "revenue", "profit", "customer",
                "growth", "competition", "analysis", "planning", "goals", "kpi"
            ],
            "technical_support": [
                "error", "issue", "problem", "fix", "troubleshoot", "support",
                "help", "broken", "not working", "installation", "configuration"
            ],
            "creative_design": [
                "design", "creative", "visual", "aesthetic", "layout", "color",
                "typography", "user experience", "interface", "branding"
            ],
            "academic_research": [
                "research", "study", "analysis", "methodology", "hypothesis",
                "literature", "publication", "peer review", "citation", "theory"
            ]
        }
    
    def _initialize_intent_classifiers(self) -> Dict[IntentCategory, List[str]]:
        """Initialize intent classification patterns."""
        return {
            IntentCategory.INFORMATION_SEEKING: [
                "what is", "how does", "explain", "define", "describe", "tell me about",
                "information", "details", "overview", "summary"
            ],
            IntentCategory.PROBLEM_SOLVING: [
                "fix", "solve", "resolve", "troubleshoot", "debug", "error",
                "issue", "problem", "not working", "broken"
            ],
            IntentCategory.CREATIVE_ASSISTANCE: [
                "create", "generate", "design", "make", "build", "develop",
                "improve", "enhance", "innovate", "brainstorm"
            ],
            IntentCategory.LEARNING: [
                "learn", "understand", "study", "tutorial", "guide", "teach",
                "explain how", "step by step", "example"
            ],
            IntentCategory.DECISION_SUPPORT: [
                "should I", "which is better", "compare", "recommend", "choose",
                "decide", "evaluate", "pros and cons", "best option"
            ],
            IntentCategory.TASK_COMPLETION: [
                "complete", "finish", "implement", "execute", "perform", "do",
                "accomplish", "achieve", "carry out"
            ],
            IntentCategory.EXPLORATION: [
                "explore", "investigate", "discover", "find out", "research",
                "look into", "examine", "analyze"
            ],
            IntentCategory.VALIDATION: [
                "check", "verify", "confirm", "validate", "correct", "review",
                "is this right", "does this work", "feedback"
            ]
        }
    
    def _initialize_style_indicators(self) -> Dict[str, List[str]]:
        """Initialize interaction style indicators."""
        return {
            "formal": [
                "please", "could you", "would you", "thank you", "appreciate",
                "respectfully", "professionally", "formally"
            ],
            "casual": [
                "hey", "hi", "cool", "awesome", "great", "thanks", "btw",
                "basically", "stuff", "thing"
            ],
            "technical": [
                "specifically", "precisely", "exactly", "implementation",
                "architecture", "specification", "documentation"
            ],
            "urgent": [
                "urgent", "asap", "immediately", "quickly", "fast", "now",
                "emergency", "critical", "deadline"
            ],
            "exploratory": [
                "maybe", "perhaps", "possibly", "might", "could be",
                "wondering", "curious", "exploring"
            ]
        }
    
    def _initialize_complexity_markers(self) -> Dict[str, float]:
        """Initialize complexity assessment markers."""
        return {
            # High complexity indicators
            "multi-step": 0.8,
            "integration": 0.7,
            "architecture": 0.8,
            "optimization": 0.7,
            "advanced": 0.8,
            "complex": 0.9,
            "sophisticated": 0.8,
            
            # Medium complexity indicators
            "analysis": 0.5,
            "implementation": 0.6,
            "configuration": 0.5,
            "customization": 0.6,
            
            # Low complexity indicators
            "simple": 0.2,
            "basic": 0.3,
            "easy": 0.2,
            "quick": 0.3,
            "straightforward": 0.2
        }
    
    def analyze_context(self, query: str, additional_context: Dict[str, Any] = None) -> ContextProfile:
        """
        Perform comprehensive contextual analysis of a query.
        
        Returns detailed context profile with multi-dimensional analysis.
        """
        additional_context = additional_context or {}
        
        # Initialize context profile
        profile = ContextProfile()
        
        # Analyze domain
        profile.domain = self._analyze_domain(query, additional_context)
        
        # Classify intent
        profile.intent = self._classify_intent(query, additional_context)
        
        # Assess urgency
        profile.urgency = self._assess_urgency(query, additional_context)
        
        # Calculate complexity
        profile.complexity_score = self._calculate_complexity(query, additional_context)
        
        # Infer knowledge level
        profile.knowledge_level = self._infer_knowledge_level(query, additional_context)
        
        # Determine interaction style
        profile.interaction_style = self._determine_interaction_style(query, additional_context)
        
        # Analyze emotional tone
        profile.emotional_tone = self._analyze_emotional_tone(query, additional_context)
        
        # Extract constraints and preferences
        profile.constraints = self._extract_constraints(query, additional_context)
        profile.preferences = self._extract_preferences(query, additional_context)
        
        # Identify related topics
        profile.related_topics = self._identify_related_topics(query, additional_context)
        
        # Calculate confidence scores
        profile.confidence_scores = self._calculate_confidence_scores(profile, query)
        
        # Identify uncertainty areas
        profile.uncertainty_areas = self._identify_uncertainty_areas(profile, query)
        
        # Update statistics
        self.analysis_stats["total_analyses"] += 1
        
        return profile
    
    def _analyze_domain(self, query: str, context: Dict[str, Any]) -> str:
        """Analyze and determine the primary domain of the query."""
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                # Weight by keyword frequency and relevance
                domain_scores[domain] = score / len(keywords)
        
        # Consider context hints
        if "domain_hint" in context:
            suggested_domain = context["domain_hint"]
            if suggested_domain in domain_scores:
                domain_scores[suggested_domain] *= 1.5
            else:
                domain_scores[suggested_domain] = 0.3
        
        # Return highest scoring domain or default
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        return "general"
    
    def _classify_intent(self, query: str, context: Dict[str, Any]) -> IntentCategory:
        """Classify the user's intent behind the query."""
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_classifiers.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Consider question patterns
        if query.strip().endswith('?'):
            if any(word in query_lower for word in ['what', 'how', 'why', 'when', 'where']):
                intent_scores[IntentCategory.INFORMATION_SEEKING] = intent_scores.get(IntentCategory.INFORMATION_SEEKING, 0) + 2
        
        # Consider imperative patterns
        imperative_patterns = ['create', 'make', 'build', 'implement', 'fix', 'solve']
        if any(pattern in query_lower for pattern in imperative_patterns):
            intent_scores[IntentCategory.TASK_COMPLETION] = intent_scores.get(IntentCategory.TASK_COMPLETION, 0) + 1
        
        # Return highest scoring intent or default
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        return IntentCategory.INFORMATION_SEEKING
    
    def _assess_urgency(self, query: str, context: Dict[str, Any]) -> UrgencyLevel:
        """Assess the urgency level of the query."""
        query_lower = query.lower()
        
        # Critical urgency indicators
        if any(word in query_lower for word in ['urgent', 'emergency', 'critical', 'asap', 'immediately']):
            return UrgencyLevel.CRITICAL
        
        # High urgency indicators
        if any(word in query_lower for word in ['quickly', 'fast', 'soon', 'deadline', 'time-sensitive']):
            return UrgencyLevel.HIGH
        
        # Low urgency indicators
        if any(word in query_lower for word in ['when convenient', 'no rush', 'sometime', 'eventually']):
            return UrgencyLevel.LOW
        
        # Background indicators
        if any(word in query_lower for word in ['background', 'research', 'explore', 'curious']):
            return UrgencyLevel.BACKGROUND
        
        # Consider context hints
        if "urgency_hint" in context:
            urgency_mapping = {
                "critical": UrgencyLevel.CRITICAL,
                "high": UrgencyLevel.HIGH,
                "medium": UrgencyLevel.MEDIUM,
                "low": UrgencyLevel.LOW,
                "background": UrgencyLevel.BACKGROUND
            }
            return urgency_mapping.get(context["urgency_hint"], UrgencyLevel.MEDIUM)
        
        return UrgencyLevel.MEDIUM
    
    def _calculate_complexity(self, query: str, context: Dict[str, Any]) -> float:
        """Calculate complexity score based on various indicators."""
        query_lower = query.lower()
        complexity_score = 0.5  # Base complexity
        
        # Word count influence
        word_count = len(query.split())
        complexity_score += min(0.3, word_count / 100)  # Cap at 0.3
        
        # Complexity markers
        for marker, weight in self.complexity_markers.items():
            if marker in query_lower:
                complexity_score += (weight - 0.5) * 0.3  # Normalize influence
        
        # Multi-part questions
        if '?' in query and query.count('?') > 1:
            complexity_score += 0.2
        
        # Conditional statements
        if any(word in query_lower for word in ['if', 'when', 'unless', 'provided', 'assuming']):
            complexity_score += 0.15
        
        # Technical terminology density
        tech_terms = sum(1 for word in query_lower.split() 
                        if len(word) > 8 or word.endswith(('ing', 'tion', 'ism', 'ity')))
        if tech_terms > 3:
            complexity_score += min(0.2, tech_terms / 20)
        
        # Context hints
        if "complexity_hint" in context:
            hinted_complexity = context["complexity_hint"]
            if isinstance(hinted_complexity, (int, float)):
                complexity_score = (complexity_score + hinted_complexity) / 2
        
        return max(0.0, min(1.0, complexity_score))
    
    def _infer_knowledge_level(self, query: str, context: Dict[str, Any]) -> str:
        """Infer the user's knowledge level in the domain."""
        query_lower = query.lower()
        
        # Beginner indicators
        beginner_phrases = [
            "i'm new to", "beginner", "just started", "don't know much",
            "explain like", "simple terms", "basic", "introduction"
        ]
        if any(phrase in query_lower for phrase in beginner_phrases):
            return "beginner"
        
        # Advanced indicators
        advanced_phrases = [
            "advanced", "expert", "professional", "optimization", "architecture",
            "implementation details", "under the hood", "internals"
        ]
        if any(phrase in query_lower for phrase in advanced_phrases):
            return "advanced"
        
        # Expert indicators
        expert_phrases = [
            "research", "publication", "thesis", "dissertation", "cutting edge",
            "state of the art", "novel approach"
        ]
        if any(phrase in query_lower for phrase in expert_phrases):
            return "expert"
        
        # Context hints
        if "knowledge_level_hint" in context:
            return context["knowledge_level_hint"]
        
        return "intermediate"
    
    def _determine_interaction_style(self, query: str, context: Dict[str, Any]) -> str:
        """Determine preferred interaction style."""
        query_lower = query.lower()
        style_scores = {}
        
        for style, indicators in self.style_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query_lower)
            if score > 0:
                style_scores[style] = score
        
        if style_scores:
            return max(style_scores.items(), key=lambda x: x[1])[0]
        
        return "professional"
    
    def _analyze_emotional_tone(self, query: str, context: Dict[str, Any]) -> str:
        """Analyze emotional tone of the query."""
        query_lower = query.lower()
        
        # Frustrated/stressed indicators
        if any(word in query_lower for word in ['frustrated', 'stuck', 'confused', 'difficult', 'struggling']):
            return "frustrated"
        
        # Excited/enthusiastic indicators
        if any(word in query_lower for word in ['excited', 'amazing', 'awesome', 'love', 'fantastic']):
            return "enthusiastic"
        
        # Concerned/worried indicators
        if any(word in query_lower for word in ['worried', 'concerned', 'afraid', 'nervous', 'unsure']):
            return "concerned"
        
        # Professional/neutral indicators
        if any(word in query_lower for word in ['please', 'kindly', 'appreciate', 'thank you']):
            return "professional"
        
        return "neutral"
    
    def _extract_constraints(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Extract explicit constraints from the query."""
        constraints = []
        query_lower = query.lower()
        
        # Time constraints
        if any(word in query_lower for word in ['by', 'before', 'within', 'deadline']):
            constraints.append("time_constraint")
        
        # Budget constraints
        if any(word in query_lower for word in ['budget', 'cost', 'price', 'free', 'cheap']):
            constraints.append("budget_constraint")
        
        # Technology constraints
        if any(word in query_lower for word in ['using', 'with', 'must use', 'required']):
            constraints.append("technology_constraint")
        
        # Platform constraints
        if any(word in query_lower for word in ['linux', 'windows', 'macos', 'mobile', 'web']):
            constraints.append("platform_constraint")
        
        # Size/scale constraints
        if any(word in query_lower for word in ['small', 'large', 'simple', 'complex', 'minimal']):
            constraints.append("scale_constraint")
        
        return constraints
    
    def _extract_preferences(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user preferences from the query."""
        preferences = {}
        query_lower = query.lower()
        
        # Communication preferences
        if "detailed" in query_lower or "comprehensive" in query_lower:
            preferences["detail_level"] = "high"
        elif "brief" in query_lower or "summary" in query_lower:
            preferences["detail_level"] = "low"
        
        # Example preferences
        if "example" in query_lower or "sample" in query_lower:
            preferences["include_examples"] = True
        
        # Step-by-step preferences
        if "step by step" in query_lower or "guide" in query_lower:
            preferences["format"] = "step_by_step"
        
        # Visual preferences
        if "diagram" in query_lower or "visual" in query_lower or "chart" in query_lower:
            preferences["include_visuals"] = True
        
        return preferences
    
    def _identify_related_topics(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Identify topics related to the main query."""
        related_topics = []
        query_lower = query.lower()
        
        # Extract potential topics using simple heuristics
        words = query_lower.split()
        potential_topics = [word for word in words if len(word) > 4 and word.isalpha()]
        
        # Filter and score topics
        for topic in potential_topics:
            if topic in self.learned_patterns:
                related_topics.append(topic)
        
        # Add context-suggested topics
        if "related_topics" in context:
            related_topics.extend(context["related_topics"])
        
        return list(set(related_topics))  # Remove duplicates
    
    def _calculate_confidence_scores(self, profile: ContextProfile, query: str) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of the analysis."""
        confidence_scores = {}
        
        # Domain confidence
        domain_keywords = self.domain_patterns.get(profile.domain, [])
        domain_matches = sum(1 for keyword in domain_keywords if keyword in query.lower())
        confidence_scores["domain"] = min(1.0, domain_matches / max(1, len(domain_keywords) * 0.3))
        
        # Intent confidence
        intent_patterns = self.intent_classifiers.get(profile.intent, [])
        intent_matches = sum(1 for pattern in intent_patterns if pattern in query.lower())
        confidence_scores["intent"] = min(1.0, intent_matches / max(1, len(intent_patterns) * 0.2))
        
        # Complexity confidence
        complexity_indicators = sum(1 for marker in self.complexity_markers if marker in query.lower())
        confidence_scores["complexity"] = min(1.0, complexity_indicators / 3)
        
        # Overall confidence
        confidence_scores["overall"] = sum(confidence_scores.values()) / len(confidence_scores)
        
        return confidence_scores
    
    def _identify_uncertainty_areas(self, profile: ContextProfile, query: str) -> List[str]:
        """Identify areas of uncertainty in the contextual analysis."""
        uncertainty_areas = []
        
        # Low confidence areas
        for aspect, confidence in profile.confidence_scores.items():
            if confidence < 0.5:
                uncertainty_areas.append(f"low_confidence_{aspect}")
        
        # Ambiguous language
        if any(word in query.lower() for word in ['maybe', 'perhaps', 'might', 'possibly']):
            uncertainty_areas.append("ambiguous_language")
        
        # Multiple possible interpretations
        if len(query.split('or')) > 1:
            uncertainty_areas.append("multiple_interpretations")
        
        # Vague requirements
        if any(word in query.lower() for word in ['something', 'anything', 'somehow', 'some way']):
            uncertainty_areas.append("vague_requirements")
        
        return uncertainty_areas
    
    def generate_contextual_insights(self, profile: ContextProfile) -> List[ContextualInsight]:
        """Generate actionable insights based on contextual analysis."""
        insights = []
        
        # Complexity-based insights
        if profile.complexity_score > 0.7:
            insights.append(ContextualInsight(
                insight_type="complexity",
                description="High complexity query detected - consider breaking into smaller parts",
                confidence=0.8,
                actionable_recommendations=[
                    "Break down into sub-questions",
                    "Provide structured response",
                    "Include implementation steps"
                ],
                evidence=[f"Complexity score: {profile.complexity_score:.2f}"]
            ))
        
        # Urgency-based insights
        if profile.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
            insights.append(ContextualInsight(
                insight_type="urgency",
                description="Time-sensitive request requiring prompt response",
                confidence=0.9,
                actionable_recommendations=[
                    "Prioritize immediate, actionable solutions",
                    "Provide quick wins first",
                    "Defer detailed explanations if needed"
                ],
                evidence=[f"Urgency level: {profile.urgency.value}"]
            ))
        
        # Knowledge level insights
        if profile.knowledge_level == "beginner":
            insights.append(ContextualInsight(
                insight_type="knowledge_level",
                description="Beginner-level user requiring accessible explanations",
                confidence=0.7,
                actionable_recommendations=[
                    "Use simple, clear language",
                    "Provide background context",
                    "Include step-by-step guidance",
                    "Avoid jargon"
                ],
                evidence=[f"Knowledge level: {profile.knowledge_level}"]
            ))
        
        # Style adaptation insights
        if profile.interaction_style == "technical":
            insights.append(ContextualInsight(
                insight_type="interaction_style",
                description="Technical communication style preferred",
                confidence=0.8,
                actionable_recommendations=[
                    "Use precise technical terminology",
                    "Provide implementation details",
                    "Include code examples",
                    "Reference documentation"
                ],
                evidence=[f"Interaction style: {profile.interaction_style}"]
            ))
        
        return insights
    
    def adapt_response_strategy(self, profile: ContextProfile, insights: List[ContextualInsight]) -> Dict[str, Any]:
        """Adapt response strategy based on contextual analysis."""
        strategy = {
            "tone": "professional",
            "detail_level": "medium",
            "structure": "standard",
            "examples": False,
            "technical_depth": "medium",
            "urgency_handling": "standard"
        }
        
        # Adapt based on profile
        if profile.knowledge_level == "beginner":
            strategy["detail_level"] = "high"
            strategy["examples"] = True
            strategy["technical_depth"] = "low"
        elif profile.knowledge_level == "expert":
            strategy["detail_level"] = "low"
            strategy["technical_depth"] = "high"
        
        if profile.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
            strategy["structure"] = "action_first"
            strategy["urgency_handling"] = "prioritized"
        
        if profile.complexity_score > 0.7:
            strategy["structure"] = "hierarchical"
            strategy["detail_level"] = "high"
        
        if profile.interaction_style == "casual":
            strategy["tone"] = "friendly"
        elif profile.interaction_style == "formal":
            strategy["tone"] = "formal"
        
        # Apply insights
        for insight in insights:
            if insight.insight_type == "complexity":
                strategy["structure"] = "step_by_step"
            elif insight.insight_type == "urgency":
                strategy["urgency_handling"] = "immediate"
        
        return strategy
    
    def get_contextual_status(self) -> Dict[str, Any]:
        """Get comprehensive status of contextual analyzer."""
        return {
            "analysis_statistics": self.analysis_stats.copy(),
            "learned_patterns": {
                domain: len(patterns) for domain, patterns in self.learned_patterns.items()
            },
            "domain_coverage": list(self.domain_patterns.keys()),
            "intent_categories": [intent.value for intent in IntentCategory],
            "context_history_length": len(self.context_history),
            "adaptation_capabilities": {
                "domain_recognition": True,
                "intent_classification": True,
                "urgency_assessment": True,
                "complexity_calculation": True,
                "style_adaptation": True
            }
        }
