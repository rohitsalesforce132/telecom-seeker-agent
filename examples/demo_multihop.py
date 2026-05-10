"""Multi-hop reasoning demo — show deep search across telecom graph."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from agent import TelecomSeekerAgent

agent = TelecomSeekerAgent(Config(max_steps=10))

print("=" * 60)
print("Telecom Seeker — Multi-Hop Deep Search Demo")
print("=" * 60)

queries = [
    "Trace the full signal path from UE to internet",
    "If AMF goes down which services are affected and what runbook applies",
]

for q in queries:
    print(f"\n{'─' * 60}")
    print(f"Query: {q}")
    print(f"{'─' * 60}")
    result = agent.search(q)
    print(f"Difficulty: {result.difficulty.value} | Steps: {result.total_tool_calls}")
    for i, step in enumerate(result.steps):
        print(f"\n  [{i+1}] {step.tool_call.tool.value}")
        print(f"      Thought: {step.thought}")
        print(f"      → {step.observation[:200]}")
    print(f"\n  📋 ANSWER:")
    print(f"  {result.answer[:500]}")

print("\n" + "=" * 60)
