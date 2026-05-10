"""Training data synthesis demo — difficulty filtering."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from agent import TelecomSeekerAgent
from models import TelecomQuery, QueryDifficulty

agent = TelecomSeekerAgent(Config(min_steps_for_learning=4))

print("=" * 60)
print("Data Synthesis + Difficulty Filtering")
print("=" * 60)

queries = [
    TelecomQuery(id="q1", question="What is AMF?", expected_answer="AMF", difficulty=QueryDifficulty.EASY, required_hops=1, domain="5g_core"),
    TelecomQuery(id="q2", question="What is NRF?", expected_answer="NRF", difficulty=QueryDifficulty.EASY, required_hops=1, domain="5g_core"),
    TelecomQuery(id="q3", question="How does SMF connect to UPF?", expected_answer="N4 PFCP", difficulty=QueryDifficulty.MEDIUM, required_hops=3, domain="5g_core"),
    TelecomQuery(id="q4", question="Trace signal path from UE to internet via gNB and UPF", expected_answer="UE-Uu-gNB-N3-UPF-N6-DN", difficulty=QueryDifficulty.HARD, required_hops=6, domain="5g_core"),
    TelecomQuery(id="q5", question="If AMF goes down which services are affected and what runbook applies", expected_answer="RB-001", difficulty=QueryDifficulty.HARD, required_hops=5, domain="incident"),
    TelecomQuery(id="q6", question="What protocol does N4 use?", expected_answer="PFCP", difficulty=QueryDifficulty.EASY, required_hops=2, domain="5g_core"),
    TelecomQuery(id="q7", question="How does CAMARA QoD API work with PCF and UPF", expected_answer="QoS enforcement", difficulty=QueryDifficulty.HARD, required_hops=5, domain="camara"),
]

# Step 1: Generate raw trajectories
print(f"\n1. Running {len(queries)} queries through agent...")
raw = [agent.search(q.question) for q in queries]

# Step 2: Show difficulty distribution
easy = sum(1 for t in raw if t.total_tool_calls < 4)
hard = len(raw) - easy
print(f"   Raw trajectories: {len(raw)}")
print(f"   Easy (< 4 steps): {easy}")
print(f"   Hard (>= 4 steps): {hard}")

# Step 3: Apply strict low-step filtering
filtered = agent.synthesize_training_data(queries, min_steps=4)
print(f"\n2. Strict Filtering (min_steps=4):")
print(f"   Kept: {len(filtered)} / {len(raw)} trajectories ({100*len(filtered)//len(raw)}%)")

# Step 4: Export as SFT data
sft_data = agent.export_sft_data(filtered)
print(f"\n3. Exported {len(sft_data)} SFT training examples")

# Step 5: Show difficulty distribution
for t in filtered:
    print(f"   • '{t.query[:50]}...' → {t.total_tool_calls} steps, {t.difficulty.value}")

# Step 6: Save
output_path = os.path.join(os.path.dirname(__file__), '..', 'sft_training_data.json')
with open(output_path, 'w') as f:
    json.dump(sft_data, f, indent=2)
print(f"\n4. Saved to {output_path}")

# Key insight:
print(f"\n{'=' * 60}")
print("KEY INSIGHT:")
print(f"  Easy examples teach the agent NOTHING.")
print(f"  Only keep HARD trajectories (>= 4 tool calls).")
print(f"  {len(filtered)} high-quality examples > {len(raw)} mixed-quality examples.")
print(f"  10.6K hard trajectories beat industrial CPT+SFT+RL pipelines.")
print("=" * 60)
