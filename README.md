# Telecom Seeker Agent

A **standalone ReAct-style deep search agent for telecom domain**, inspired by [OpenSeeker-v2](https://arxiv.org/abs/2605.04036). Multi-step reasoning over a 5G knowledge graph with 35+ entities, 5 search tools, and OpenSeeker-v2's strict difficulty filtering for SFT data synthesis.

## What It Does

```
Query: "Trace the signal path from UE to internet"
  Step 1: [service_map] → Found UPF (User Plane Function)...
  Step 2: [graph_traverse] → UPF connects to gNB via N3...
  Step 3: [keyword_search] → Found DN (Data Network)...
  Step 4: [spec_lookup] → 3GPP TS 23.501 defines the path...

  Answer: UE → (Uu) → gNB → (N3) → UPF → (N6) → DN
  Difficulty: HARD (4 tool calls)
```

## Architecture

```
┌──────────────────────────────────────────┐
│           Telecom Seeker Agent            │
│                                          │
│  ┌────────────┐    ┌──────────────────┐  │
│  │   ReAct     │    │  Knowledge Graph  │  │
│  │   Loop      │    │  35+ 5G entities  │  │
│  │ Think→Act→  │    │  AMF,SMF,UPF,gNB  │  │
│  │ Observe     │    │  O-RAN,CAMARA,TMF │  │
│  └─────┬──────┘    └────────┬─────────┘  │
│        │                    │             │
│  ┌─────▼──────────────────▼──────────┐   │
│  │           5 Search Tools           │   │
│  │                                    │   │
│  │  1. keyword_search                 │   │
│  │  2. graph_traverse                 │   │
│  │  3. spec_lookup (3GPP/CAMARA/TMF)  │   │
│  │  4. runbook_search                 │   │
│  │  5. service_map                    │   │
│  └────────────────────────────────────┘   │
│                                          │
│  ┌────────────────────────────────────┐   │
│  │  OpenSeeker-v2 Difficulty Filter   │   │
│  │  D = {(q,τ) | T(τ) >= T_min}     │   │
│  │  Only keep HARD trajectories       │   │
│  └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

## OpenSeeker-v2's 3 Modifications Applied to Telecom

| Modification | What We Did | Why |
|---|---|---|
| **Scale graph size** | 35+ entities with rich relationships | More multi-hop paths = harder queries |
| **Expand tool set** | 5 distinct search tools | Agent learns diverse strategies |
| **Strict low-step filtering** | Only keep trajectories with ≥ 4 tool calls | Easy examples teach nothing |

## Quick Start

```bash
# Clone
git clone https://github.com/rohitsalesforce132/telecom-seeker-agent
cd telecom-seeker-agent

# Run tests
python3 tests/test_all.py

# Basic demo
python3 examples/demo_basic.py

# Multi-hop reasoning
python3 examples/demo_multihop.py

# Training data synthesis with difficulty filtering
python3 examples/demo_training.py
```

No API keys needed. Everything runs locally.

## Knowledge Graph Coverage (35+ Entities)

### 5G Core (9)
AMF, SMF, UPF, UDM, AUSF, NRF, PCF, NEF, NSSF

### RAN (6)
gNB, O-CU, O-DU, O-RU, RIC, SMO

### Interfaces (4)
N1, N2, N3, N4

### Transport (2)
Backhaul, Fronthaul

### OSS/BSS (3)
TMF622, TMF640, TMF641

### CAMARA (4)
DeviceStatus, QoD, SIMSwap, NumberVerification

### Incidents (3)
AMF Outage, UPF High Latency, Slice Allocation Failure

### Specs (2)
TS 23.501, TS 23.502

## Interview Talking Points

> "I built a telecom deep search agent inspired by OpenSeeker-v2 from Shanghai Jiao Tong University. The key insight: 10.6K high-difficulty training trajectories with simple SFT beats industrial pipelines using CPT+SFT+RL. I applied this to telecom by building a 35-entity 5G knowledge graph, 5 search tools, and strict difficulty filtering that only keeps trajectories requiring 4+ tool calls. Easy examples teach the model nothing."

> "The three modifications from OpenSeeker-v2 map directly to telecom: scale the knowledge graph for richer multi-hop queries, expand the tool set for diverse search strategies, and filter out any query solvable in fewer than 4 steps. This produces concentrated, high-quality training data."

## File Structure

```
src/
  agent.py              # TelecomSeekerAgent — ReAct loop + difficulty filtering
  knowledge_graph.py    # 35+ entity 5G knowledge graph
  tools.py              # 5 search tools
  config.py             # Configuration
  models.py             # Data models
data/
  runbooks.json         # 5 telecom runbooks
  5g_specs.json         # 9 spec entries (3GPP + CAMARA)
  sample_queries.json   # 15 sample queries (easy → expert)
tests/
  test_all.py           # Full test suite
examples/
  demo_basic.py         # Basic search demo
  demo_multihop.py      # Multi-hop reasoning demo
  demo_training.py      # OpenSeeker-v2 data synthesis demo
skills/
  network_troubleshooter.md
  5g_architecture_expert.md
  incident_resolver.md
```

## License

MIT

*Inspired by [OpenSeeker-v2](https://arxiv.org/abs/2605.04036) — proving that data quality beats pipeline complexity.*
