"""Tests for Telecom Seeker Agent."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import ToolType, QueryDifficulty, TelecomQuery
from config import Config
from knowledge_graph import TelecomKnowledgeGraph
from tools import TelecomToolSet
from agent import TelecomSeekerAgent


def test_knowledge_graph():
    graph = TelecomKnowledgeGraph()
    assert len(graph.entities) >= 30, f"Expected 30+ entities, got {len(graph.entities)}"
    amf = graph.get_entity("AMF")
    assert amf is not None, "AMF not found"
    assert amf.properties["domain"] == "5g_core"
    neighbors = graph.get_neighbors("amf")
    assert len(neighbors) > 0, "AMF has no neighbors"
    assert any(n.id == "smf" for n in neighbors), "SMF not a neighbor of AMF"
    path = graph.shortest_path("ue", "dn")
    assert len(path) > 0, "No path from UE to DN"
    results = graph.search("mobility")
    assert len(results) > 0, "Search for 'mobility' returned nothing"
    print(f"  Knowledge graph: {len(graph.entities)} entities OK")


def test_tools():
    graph = TelecomKnowledgeGraph()
    tools = TelecomToolSet(graph)
    # keyword search
    r = tools.keyword_search({"query": "AMF"})
    assert "AMF" in r, f"Keyword search for AMF failed: {r}"
    # graph traverse
    r = tools.graph_traverse({"entity_name": "amf", "relation_type": None})
    assert "SMF" in r or "N11" in r, f"Graph traverse from AMF failed: {r}"
    # service map
    r = tools.service_map({"service_name": "upf"})
    assert "N3" in r or "N4" in r or "N6" in r, f"Service map for UPF failed: {r}"
    # runbook search
    r = tools.runbook_search({"error_type": "outage", "service": "amf"})
    assert "RB-001" in r or "AMF" in r, f"Runbook search failed: {r}"
    # spec lookup
    r = tools.spec_lookup({"technology": "5g", "feature": "procedures"})
    assert "23.502" in r or "Procedures" in r, f"Spec lookup failed: {r}"
    print("  All 5 tools OK")


def test_agent_basic():
    config = Config()
    agent = TelecomSeekerAgent(config)
    result = agent.search("What is AMF?")
    assert result.success, f"Search failed: {result.answer}"
    assert result.total_tool_calls >= 1, "Agent made no tool calls"
    assert result.answer, "No answer produced"
    print(f"  Basic search: {result.total_tool_calls} steps, difficulty={result.difficulty.value}")


def test_agent_multihop():
    config = Config(max_steps=10)
    agent = TelecomSeekerAgent(config)
    result = agent.search("Trace the signal path from UE to internet")
    assert result.success, f"Multi-hop search failed: {result.answer}"
    assert result.total_tool_calls >= 2, f"Expected 2+ steps for multi-hop, got {result.total_tool_calls}"
    print(f"  Multi-hop: {result.total_tool_calls} steps, difficulty={result.difficulty.value}")


def test_difficulty_filtering():
    """Strict low-step filtering: only keep hard trajectories."""
    config = Config(min_steps_for_learning=4)
    agent = TelecomSeekerAgent(config)
    queries = [
        TelecomQuery(id=f"q{i}", question=q["question"], expected_answer=q["expected_answer"],
                      difficulty=QueryDifficulty(q["difficulty"]), required_hops=q["required_hops"], domain=q["domain"])
        for i, q in enumerate([
            {"question": "What is AMF?", "expected_answer": "AMF", "difficulty": "easy", "required_hops": 1, "domain": "5g_core"},
            {"question": "Trace signal path from UE to internet via gNB UPF", "expected_answer": "path", "difficulty": "hard", "required_hops": 6, "domain": "5g_core"},
            {"question": "What is NRF?", "expected_answer": "NRF", "difficulty": "easy", "required_hops": 1, "domain": "5g_core"},
            {"question": "If AMF goes down which services are affected and what runbook applies", "expected_answer": "RB-001", "difficulty": "hard", "required_hops": 5, "domain": "incident"},
        ])
    ]
    filtered = agent.synthesize_training_data(queries, min_steps=3)
    print(f"  Difficulty filtering: {len(queries)} queries → {len(filtered)} hard trajectories kept")


def test_sft_export():
    config = Config()
    agent = TelecomSeekerAgent(config)
    traj = agent.search("How does SMF connect to UPF?")
    sft_data = agent.export_sft_data([traj])
    assert len(sft_data) == 1
    assert sft_data[0]["messages"][0]["role"] == "system"
    assert sft_data[0]["messages"][1]["role"] == "user"
    assert sft_data[0]["messages"][2]["role"] == "assistant"
    print(f"  SFT export: {len(sft_data)} trajectories in chat format")


if __name__ == "__main__":
    print("Running Telecom Seeker Agent tests...")
    test_knowledge_graph()
    test_tools()
    test_agent_basic()
    test_agent_multihop()
    test_difficulty_filtering()
    test_sft_export()
    print("\n=== ALL TESTS PASSED ===")
