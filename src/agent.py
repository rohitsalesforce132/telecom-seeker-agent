"""Telecom Seeker Agent — ReAct-style deep search agent for telecom domain.
Multi-step reasoning with tools + difficulty filtering.
"""
from models import ToolType, ToolCall, SearchStep, SearchTrajectory, TelecomQuery, QueryDifficulty
from knowledge_graph import TelecomKnowledgeGraph
from tools import TelecomToolSet


class TelecomSeekerAgent:
    """ReAct-style telecom search agent.
    
    Key insight: high-difficulty trajectories produce better agents..
    This agent demonstrates multi-step search across a telecom knowledge graph.
    """

    def __init__(self, config):
        self.config = config
        self.graph = TelecomKnowledgeGraph(config.data_dir)
        self.tools = TelecomToolSet(self.graph, config.data_dir)
        self.max_steps = config.max_steps
        self.min_steps_for_learning = config.min_steps_for_learning

    def search(self, query: str) -> SearchTrajectory:
        """Execute a multi-step ReAct search for a telecom query."""
        trajectory = SearchTrajectory(query=query)

        for step_num in range(self.max_steps):
            # THINK
            thought = self._think(query, trajectory.steps)
            # ACT
            tool_type, args = self._select_tool(thought, query, trajectory.steps)
            result = self.tools.execute(tool_type, args)
            # OBSERVE
            tool_call = ToolCall(tool=tool_type, arguments=args, result=result)
            step = SearchStep(thought=thought, tool_call=tool_call, observation=result)
            trajectory.steps.append(step)
            trajectory.total_tool_calls += 1
            # Can we answer?
            if self._can_answer(query, trajectory.steps):
                trajectory.answer = self._synthesize_answer(query, trajectory.steps)
                trajectory.success = True
                break

        trajectory.difficulty = self._classify_difficulty(trajectory.total_tool_calls)
        if not trajectory.answer:
            trajectory.answer = self._synthesize_answer(query, trajectory.steps)
            trajectory.success = len(trajectory.steps) > 0
        return trajectory

    def _think(self, query: str, previous_steps: list) -> str:
        if not previous_steps:
            return f"I need to search for information about: {query}"
        last_obs = previous_steps[-1].observation[:100]
        return f"From previous finding ({last_obs}...), I need to explore further to fully answer the query."

    def _select_tool(self, thought: str, query: str, steps: list) -> tuple:
        used_tools = {s.tool_call.tool for s in steps}
        query_lower = query.lower()
        # Prioritize unused tools
        if any(kw in query_lower for kw in ["spec", "3gpp", "standard", "ts 23"]):
            if ToolType.SPEC_LOOKUP not in used_tools:
                return ToolType.SPEC_LOOKUP, {"technology": "5g", "feature": query}
        if any(kw in query_lower for kw in ["error", "alarm", "incident", "outage", "fail", "down"]):
            if ToolType.RUNBOOK_SEARCH not in used_tools:
                return ToolType.RUNBOOK_SEARCH, {"error_type": "general", "service": query}
        if any(kw in query_lower for kw in ["connect", "interface", "between", "link", "path", "trace"]):
            if ToolType.GRAPH_TRAVERSE not in used_tools:
                entity = self.graph.get_entity(query_lower.split()[0]) or self.graph.search(query)[0] if self.graph.search(query) else None
                name = entity.name if entity else query.split()[0]
                return ToolType.GRAPH_TRAVERSE, {"entity_name": name, "relation_type": None}
        if any(kw in query_lower for kw in ["what is", "describe", "explain", "tell me about"]):
            if ToolType.SERVICE_MAP not in used_tools:
                words = [w for w in query_lower.split() if len(w) > 2 and w not in ("what", "is", "the", "how", "does", "tell", "me", "about")]
                return ToolType.SERVICE_MAP, {"service_name": " ".join(words[:2])}
        # Fallback: try unused tools
        for t in ToolType:
            if t not in used_tools:
                if t == ToolType.KEYWORD_SEARCH:
                    return t, {"query": query}
                elif t == ToolType.GRAPH_TRAVERSE:
                    entity = self.graph.search(query)
                    name = entity[0].name if entity else query.split()[0]
                    return t, {"entity_name": name, "relation_type": None}
                elif t == ToolType.SERVICE_MAP:
                    entity = self.graph.search(query)
                    name = entity[0].name if entity else query.split()[0]
                    return t, {"service_name": name}
        return ToolType.KEYWORD_SEARCH, {"query": query}

    def _can_answer(self, query: str, steps: list) -> bool:
        if len(steps) >= 2:
            return True
        return len(steps) >= 1 and len(steps[0].observation) > 100

    def _synthesize_answer(self, query: str, steps: list) -> str:
        if not steps:
            return f"Could not find information for: {query}"
        parts = [f"Based on {len(steps)} search steps:"]
        for i, step in enumerate(steps):
            obs_short = step.observation[:200]
            parts.append(f"{i+1}. [{step.tool_call.tool.value}] {obs_short}")
        parts.append(f"\nSummary: {steps[-1].observation[:300]}")
        return "\n".join(parts)

    def _classify_difficulty(self, steps: int) -> QueryDifficulty:
        if steps <= 2: return QueryDifficulty.EASY
        if steps <= 5: return QueryDifficulty.MEDIUM
        if steps <= 10: return QueryDifficulty.HARD
        return QueryDifficulty.EXPERT

    def synthesize_training_data(self, queries: list, min_steps: int = None) -> list:
        """Strict low-step filtering: only keep hard trajectories."""
        
        Only keep trajectories with T(tau) >= T_min tool calls.
        
        Only keeps trajectories that required >= min_steps tool calls.
        """
        min_steps = min_steps or self.min_steps_for_learning
        raw_trajectories = []
        for q in queries:
            traj = self.search(q.question if isinstance(q, TelecomQuery) else q)
            raw_trajectories.append(traj)
        
        # STRICT FILTER: only keep hard trajectories
        filtered = [t for t in raw_trajectories if t.total_tool_calls >= min_steps]
        return filtered

    def export_sft_data(self, trajectories: list) -> list:
        """Export trajectories as SFT training data (chat messages format)."""
        sft_data = []
        for traj in trajectories:
            messages = [
                {"role": "system", "content": "You are a telecom network expert. Use available tools to search and reason about 5G networks, services, and troubleshooting."},
                {"role": "user", "content": traj.query},
            ]
            reasoning = ""
            for step in traj.steps:
                reasoning += f"Thought: {step.thought}\n"
                reasoning += f"Action: {step.tool_call.tool.value}({step.tool_call.arguments})\n"
                reasoning += f"Observation: {step.observation[:200]}\n\n"
            reasoning += f"Answer: {traj.answer}"
            messages.append({"role": "assistant", "content": reasoning})
            sft_data.append({"messages": messages})
        return sft_data

    def get_stats(self) -> dict:
        return {
            "graph_stats": self.graph.stats(),
            "config": {"max_steps": self.max_steps, "min_steps_for_learning": self.min_steps_for_learning},
        }
