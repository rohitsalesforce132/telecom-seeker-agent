# Telecom Seeker Agent

## Architecture
ReAct-style search agent for telecom domain. Multi-step reasoning over a 5G knowledge graph.

## Key Classes
- `TelecomSeekerAgent` (agent.py) — Main agent with ReAct loop + difficulty filtering
- `TelecomKnowledgeGraph` (knowledge_graph.py) — 35+ 5G entities with relationships
- `TelecomToolSet` (tools.py) — 5 search tools

## Data Flow
1. Query → Agent.search()
2. Loop: Think → Select Tool → Execute → Observe (up to max_steps)
3. Synthesize answer from all observations
4. Classify difficulty by step count
5. For training: filter trajectories with < min_steps

## Conventions
- All data in data/ as JSON
- Skills as Markdown in skills/
- No API keys needed (local mode)
- No company names in code or data
