#!/usr/bin/env python3
"""
Context Relevance Scorer - Part of PRISM
Implements human-like context relevance scoring based on task requirements, not size limits.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import re
from datetime import datetime, timedelta

class RiskLevel(Enum):
    """Risk levels for missing context"""
    CRITICAL = "critical"     # System failure, security breach
    HIGH = "high"            # Bugs, performance issues  
    MEDIUM = "medium"        # Suboptimal solutions
    LOW = "low"              # Minor inefficiencies
    NONE = "none"            # No risk

class TaskType(Enum):
    """Different task types requiring different context strategies"""
    DEBUGGING = "debugging"
    FEATURE_DEVELOPMENT = "feature_development"
    REFACTORING = "refactoring"
    SECURITY_REVIEW = "security_review"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    INFRASTRUCTURE = "infrastructure"
    GENERAL = "general"

@dataclass
class ContextItem:
    """Represents a piece of context with metadata"""
    name: str
    content: Dict
    category: str
    size_kb: float
    last_modified: datetime
    dependencies: List[str]
    risk_if_missing: RiskLevel
    
@dataclass
class AgentState:
    """Current state of the agent during task execution"""
    task_type: TaskType
    progress: float  # 0.0 to 1.0
    context_loaded: Set[str]
    errors_encountered: List[str]
    expansion_count: int
    cognitive_load: float  # 0.0 to 1.0

class ContextRelevanceScorer:
    """
    Scores context relevance based on task requirements, not arbitrary size limits.
    Implements human-like progressive context gathering.
    """
    
    # Critical context that must always be included regardless of score
    CRITICAL_CONTEXT = {
        TaskType.DEBUGGING: [
            "ERROR_HANDLING", "STACK_TRACES", "RECENT_CHANGES", "SYSTEM_STATE"
        ],
        TaskType.SECURITY_REVIEW: [
            "AUTH_MECHANISMS", "DATA_FLOW", "EXTERNAL_INTERFACES", "DEPENDENCIES"
        ],
        TaskType.REFACTORING: [
            "TEST_COVERAGE", "DEPENDENCY_GRAPH", "PERFORMANCE_BASELINES"
        ],
        TaskType.FEATURE_DEVELOPMENT: [
            "REQUIREMENTS", "API_CONTRACTS", "ARCHITECTURE_CONSTRAINTS"
        ],
    }
    
    # Task-specific relevance patterns
    RELEVANCE_PATTERNS = {
        TaskType.DEBUGGING: {
            "high": ["error", "exception", "stack", "trace", "debug", "log"],
            "medium": ["test", "recent", "change", "commit"],
            "low": ["style", "documentation", "comment"]
        },
        TaskType.FEATURE_DEVELOPMENT: {
            "high": ["requirement", "api", "interface", "contract", "spec"],
            "medium": ["pattern", "convention", "example", "similar"],
            "low": ["deprecated", "legacy", "archived"]
        },
        TaskType.SECURITY_REVIEW: {
            "high": ["auth", "security", "vulnerability", "encryption", "access"],
            "medium": ["validation", "sanitization", "logging", "audit"],
            "low": ["style", "formatting", "comment"]
        },
    }
    
    def __init__(self):
        self.scoring_history = []
        self.task_patterns = {}
        
    def score_context(self, 
                     context_item: ContextItem, 
                     task_description: str,
                     agent_state: AgentState) -> Tuple[float, Dict[str, float]]:
        """
        Score a context item's relevance for the current task.
        Returns tuple of (total_score, component_scores)
        """
        scores = {}
        
        # 1. Task Alignment Score (0-40 points)
        scores['task_alignment'] = self._task_alignment_score(
            context_item, task_description, agent_state.task_type
        )
        
        # 2. Dependency Distance Score (0-30 points)
        scores['dependency'] = self._dependency_distance_score(
            context_item, agent_state.context_loaded
        )
        
        # 3. Risk Mitigation Score (0-20 points)
        scores['risk'] = self._risk_mitigation_score(
            context_item, agent_state
        )
        
        # 4. Recency Score (0-10 points)
        scores['recency'] = self._recency_score(context_item)
        
        # 5. Progressive Disclosure Bonus (0-10 points)
        scores['progressive'] = self._progressive_disclosure_score(
            context_item, agent_state
        )
        
        # 6. Cognitive Load Penalty (-20 to 0 points)
        scores['cognitive_penalty'] = self._cognitive_load_penalty(
            agent_state, context_item.size_kb
        )
        
        # Calculate total
        total_score = sum(scores.values())
        
        # Record for learning
        self.scoring_history.append({
            'context': context_item.name,
            'task_type': agent_state.task_type,
            'score': total_score,
            'components': scores
        })
        
        return total_score, scores
    
    def _task_alignment_score(self, item: ContextItem, task: str, task_type: TaskType) -> float:
        """Score how well the context aligns with the task (0-40)"""
        score = 0.0
        task_lower = task.lower()
        item_name_lower = item.name.lower()
        
        # Direct mention in task description (15 points)
        if item_name_lower in task_lower:
            score += 15
        
        # Category match (10 points)
        if task_type in self.RELEVANCE_PATTERNS:
            patterns = self.RELEVANCE_PATTERNS[task_type]
            
            # Check high relevance patterns (10 points)
            if any(pattern in item_name_lower for pattern in patterns.get('high', [])):
                score += 10
            # Medium relevance (5 points)
            elif any(pattern in item_name_lower for pattern in patterns.get('medium', [])):
                score += 5
            # Low relevance (0 points)
            elif any(pattern in item_name_lower for pattern in patterns.get('low', [])):
                score += 0
        
        # Task-specific critical context (15 points)
        if task_type in self.CRITICAL_CONTEXT:
            if item.name in self.CRITICAL_CONTEXT[task_type]:
                score += 15
        
        return min(score, 40)  # Cap at 40
    
    def _dependency_distance_score(self, item: ContextItem, loaded_context: Set[str]) -> float:
        """Score based on dependency distance from already loaded context (0-30)"""
        if not loaded_context:
            return 15  # Neutral score for first context
        
        # Direct dependency of loaded context (30 points)
        for loaded in loaded_context:
            if loaded in item.dependencies:
                return 30
        
        # Secondary dependency (20 points)
        secondary_deps = set()
        for loaded in loaded_context:
            # Would need to look up dependencies of loaded items
            pass
        
        # Unrelated (0 points)
        return 0
    
    def _risk_mitigation_score(self, item: ContextItem, state: AgentState) -> float:
        """Score based on risk mitigation value (0-20)"""
        risk_scores = {
            RiskLevel.CRITICAL: 20,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 10,
            RiskLevel.LOW: 5,
            RiskLevel.NONE: 0
        }
        
        base_score = risk_scores.get(item.risk_if_missing, 0)
        
        # Increase score if errors encountered
        if state.errors_encountered:
            base_score *= 1.5
            
        return min(base_score, 20)
    
    def _recency_score(self, item: ContextItem) -> float:
        """Score based on how recently the context was modified (0-10)"""
        age = datetime.now() - item.last_modified
        
        if age < timedelta(hours=1):
            return 10
        elif age < timedelta(days=1):
            return 8
        elif age < timedelta(days=7):
            return 5
        elif age < timedelta(days=30):
            return 2
        else:
            return 0
    
    def _progressive_disclosure_score(self, item: ContextItem, state: AgentState) -> float:
        """Score based on task progress and expansion needs (0-10)"""
        # Early in task: prefer overview context
        if state.progress < 0.3:
            if 'overview' in item.name.lower() or 'manifest' in item.name.lower():
                return 10
            return 0
        
        # Mid-task: prefer implementation details
        elif state.progress < 0.7:
            if 'implementation' in item.name.lower() or 'detail' in item.name.lower():
                return 10
            return 5
        
        # Late task: prefer validation/testing context
        else:
            if 'test' in item.name.lower() or 'validation' in item.name.lower():
                return 10
            return 3
    
    def _cognitive_load_penalty(self, state: AgentState, size_kb: float) -> float:
        """Penalty for adding context when cognitive load is high (-20 to 0)"""
        if state.cognitive_load < 0.5:
            return 0  # No penalty
        
        # Scale penalty based on cognitive load and size
        load_factor = (state.cognitive_load - 0.5) * 2  # 0 to 1
        size_factor = min(size_kb / 50, 1)  # Normalize to 0-1 (50KB as max)
        
        penalty = -20 * load_factor * size_factor
        return penalty
    
    def should_include_context(self, 
                              item: ContextItem,
                              task: str,
                              state: AgentState,
                              threshold: float = 50) -> Tuple[bool, str]:
        """
        Determine if context should be included.
        Returns (should_include, reason)
        """
        # Always include critical context
        if state.task_type in self.CRITICAL_CONTEXT:
            if item.name in self.CRITICAL_CONTEXT[state.task_type]:
                return True, "Critical context for task type"
        
        # Always include if critical risk
        if item.risk_if_missing == RiskLevel.CRITICAL:
            return True, "Critical risk if missing"
        
        # Score-based inclusion
        score, components = self.score_context(item, task, state)
        
        if score >= threshold:
            return True, f"Score {score:.1f} exceeds threshold"
        
        # Progressive loading: lower threshold as task progresses with errors
        if state.errors_encountered:
            adjusted_threshold = threshold * 0.7
            if score >= adjusted_threshold:
                return True, f"Score {score:.1f} exceeds error-adjusted threshold"
        
        return False, f"Score {score:.1f} below threshold"
    
    def get_optimal_context_set(self,
                               available_items: List[ContextItem],
                               task: str,
                               state: AgentState,
                               max_cognitive_load: float = 0.8) -> List[ContextItem]:
        """
        Select optimal set of context items for the task.
        Balances relevance with cognitive load.
        """
        # Score all items
        scored_items = []
        for item in available_items:
            score, components = self.score_context(item, task, state)
            scored_items.append((score, item, components))
        
        # Sort by score descending
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Select items while managing cognitive load
        selected = []
        current_load = state.cognitive_load
        
        for score, item, components in scored_items:
            # Always include critical items
            if item.risk_if_missing == RiskLevel.CRITICAL:
                selected.append(item)
                current_load += item.size_kb / 200  # Rough cognitive impact
                continue
            
            # Check if we can add without overloading
            projected_load = current_load + (item.size_kb / 200)
            if projected_load <= max_cognitive_load:
                should_include, reason = self.should_include_context(item, task, state)
                if should_include:
                    selected.append(item)
                    current_load = projected_load
            else:
                # Stop adding non-critical items if load too high
                break
        
        return selected
    
    def learn_from_task_completion(self,
                                  task_type: TaskType,
                                  used_context: Set[str],
                                  loaded_context: Set[str],
                                  success: bool):
        """
        Learn from task completion to improve future scoring.
        """
        utilization = len(used_context) / len(loaded_context) if loaded_context else 0
        
        # Record pattern
        if task_type not in self.task_patterns:
            self.task_patterns[task_type] = {
                'successful_sets': [],
                'failed_sets': [],
                'utilization_rates': []
            }
        
        pattern = self.task_patterns[task_type]
        
        if success:
            pattern['successful_sets'].append(used_context)
        else:
            pattern['failed_sets'].append(loaded_context - used_context)
        
        pattern['utilization_rates'].append(utilization)
        
        # Adjust future scoring based on patterns
        self._update_scoring_weights(task_type, utilization, success)
    
    def _update_scoring_weights(self, task_type: TaskType, utilization: float, success: bool):
        """Update internal scoring weights based on task outcomes"""
        # This would adjust the scoring algorithm based on learned patterns
        # For now, just track the data
        pass


def main():
    """Test the relevance scorer"""
    scorer = ContextRelevanceScorer()
    
    # Create test context items
    test_items = [
        ContextItem(
            name="ERROR_HANDLING",
            content={},
            category="critical",
            size_kb=5,
            last_modified=datetime.now(),
            dependencies=[],
            risk_if_missing=RiskLevel.CRITICAL
        ),
        ContextItem(
            name="UI_COMPONENTS",
            content={},
            category="frontend",
            size_kb=20,
            last_modified=datetime.now() - timedelta(days=5),
            dependencies=["DESIGN_SYSTEM"],
            risk_if_missing=RiskLevel.LOW
        ),
        ContextItem(
            name="DATABASE_SCHEMA",
            content={},
            category="backend",
            size_kb=15,
            last_modified=datetime.now() - timedelta(hours=2),
            dependencies=["API_CONTRACTS"],
            risk_if_missing=RiskLevel.HIGH
        ),
    ]
    
    # Test different scenarios
    test_scenarios = [
        ("Fix database connection error", TaskType.DEBUGGING, 0.2),
        ("Add new user dashboard component", TaskType.FEATURE_DEVELOPMENT, 0.5),
        ("Review authentication flow for vulnerabilities", TaskType.SECURITY_REVIEW, 0.3),
    ]
    
    for task, task_type, progress in test_scenarios:
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print(f"Type: {task_type.value}")
        print(f"Progress: {progress*100:.0f}%")
        print(f"{'='*60}")
        
        state = AgentState(
            task_type=task_type,
            progress=progress,
            context_loaded=set(),
            errors_encountered=[],
            expansion_count=0,
            cognitive_load=0.3
        )
        
        optimal_set = scorer.get_optimal_context_set(test_items, task, state)
        
        for item in optimal_set:
            score, components = scorer.score_context(item, task, state)
            print(f"\n{item.name}:")
            print(f"  Total Score: {score:.1f}")
            print(f"  Components: {components}")
            should_include, reason = scorer.should_include_context(item, task, state)
            print(f"  Include: {should_include} ({reason})")


if __name__ == "__main__":
    main()