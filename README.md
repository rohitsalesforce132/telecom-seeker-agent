# Telecom Seeker Agent

A **standalone ReAct-style deep search agent for telecom domain**. Multi-step reasoning over a 5G knowledge graph with 35+ entities, 5 search tools, and strict difficulty filtering for SFT data synthesis.

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
│  │  Difficulty Filter   │   │
│  │  D = {(q,τ) | T(τ) >= T_min}     │   │
│  │  Only keep HARD trajectories       │   │
│  └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

## Key Design Decisions

| Decision | What We Did | Why |
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

## Key Features

- Multi-step ReAct reasoning over telecom knowledge graph
- 5 specialized search tools for diverse strategies
- Strict difficulty filtering for high-quality training data
- SFT data export in chat messages format
- Runs locally, no API keys needed

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
  demo_training.py      # Data synthesis demo
skills/
  network_troubleshooter.md
  5g_architecture_expert.md
  incident_resolver.md
```

## License

MIT

*Proving that data quality and difficulty filtering beats brute-force scale.*
