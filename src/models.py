from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional


class ToolType(Enum):
    KEYWORD_SEARCH = "keyword_search"
    GRAPH_TRAVERSE = "graph_traverse"
    SPEC_LOOKUP = "spec_lookup"
    RUNBOOK_SEARCH = "runbook_search"
    SERVICE_MAP = "service_map"


class QueryDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class EntityType(Enum):
    SERVICE = "service"
    INTERFACE = "interface"
    PROTOCOL = "protocol"
    KPI = "kpi"
    INCIDENT = "incident"
    RUNBOOK = "runbook"
    SPEC = "spec"


@dataclass
class GraphEntity:
    id: str
    name: str
    entity_type: EntityType
    properties: dict = field(default_factory=dict)
    relationships: list = field(default_factory=list)


@dataclass
class ToolCall:
    tool: ToolType
    arguments: dict
    result: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SearchStep:
    thought: str
    tool_call: ToolCall
    observation: str


@dataclass
class SearchTrajectory:
    query: str
    difficulty: QueryDifficulty = QueryDifficulty.EASY
    steps: list = field(default_factory=list)
    answer: str = ""
    success: bool = False
    total_tool_calls: int = 0


@dataclass
class TelecomQuery:
    id: str
    question: str
    expected_answer: str
    difficulty: QueryDifficulty
    required_hops: int
    domain: str
