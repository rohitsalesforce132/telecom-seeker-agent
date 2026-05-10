"""Basic demo — solve a telecom query with the agent."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from agent import TelecomSeekerAgent

agent = TelecomSeekerAgent(Config())

print("=" * 60)
print("Telecom Seeker Agent — Basic Demo")
print("=" * 60)

queries = [
    "What is AMF?",
    "What interfaces connect AMF to gNB?",
    "How does SMF connect to UPF?",
    "What is O-RAN RIC?",
]

for q in queries:
    print(f"\n{'─' * 60}")
    print(f"Query: {q}")
    print(f"{'─' * 60}")
    result = agent.search(q)
    for i, step in enumerate(result.steps):
        print(f"  Step {i+1}: [{step.tool_call.tool.value}]")
        print(f"    Thought: {step.thought[:100]}")
        print(f"    Observation: {step.observation[:150]}")
    print(f"\n  Answer: {result.answer[:300]}")
    print(f"  Steps: {result.total_tool_calls} | Difficulty: {result.difficulty.value}")

print(f"\n{'=' * 60}")
print(f"Graph stats: {agent.get_stats()['graph_stats']}")
print("=" * 60)
