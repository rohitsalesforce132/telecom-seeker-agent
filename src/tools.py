"""Telecom Search Tools — 5 tools for multi-step search (OpenSeeker-v2 inspired)."""
import json
import os
from models import ToolType, ToolCall


class TelecomToolSet:
    """5 search tools for telecom domain. All work locally."""

    def __init__(self, graph, data_dir: str = None):
        self.graph = graph
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        self._runbooks = self._load_json("runbooks.json", [])
        self._specs = self._load_json("5g_specs.json", [])

    def _load_json(self, filename, default):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return default

    def execute(self, tool: ToolType, args: dict) -> str:
        handlers = {
            ToolType.KEYWORD_SEARCH: self.keyword_search,
            ToolType.GRAPH_TRAVERSE: self.graph_traverse,
            ToolType.SPEC_LOOKUP: self.spec_lookup,
            ToolType.RUNBOOK_SEARCH: self.runbook_search,
            ToolType.SERVICE_MAP: self.service_map,
        }
        handler = handlers.get(tool)
        if not handler:
            return f"Unknown tool: {tool}"
        return handler(args)

    def keyword_search(self, args: dict) -> str:
        query = args.get("query", "")
        results = self.graph.search(query)
        if not results:
            return f"No entities found matching '{query}'."
        lines = [f"Found {len(results)} entities:"]
        for r in results[:10]:
            desc = r.properties.get("description", r.name)
            lines.append(f"  • {r.name} ({r.entity_type.value}): {desc[:120]}")
        return "\n".join(lines)

    def graph_traverse(self, args: dict) -> str:
        entity_name = args.get("entity_name", "")
        relation_type = args.get("relation_type")
        max_depth = args.get("max_depth", 1)
        entity = self.graph.get_entity(entity_name)
        if not entity:
            return f"Entity '{entity_name}' not found in graph."
        neighbors = self.graph.get_neighbors(entity.id, relation_type)
        if not neighbors:
            return f"{entity.name} has no {'matching ' if relation_type else ''}relationships."
        lines = [f"Relationships from {entity.name}:"]
        for n in neighbors:
            rel = [r for r in entity.relationships if r["target"] == n.id]
            rel_name = rel[0]["relation"] if rel else "connected"
            lines.append(f"  → {n.name} ({rel_name}) — {n.properties.get('full_name', '')}")
        return "\n".join(lines)

    def spec_lookup(self, args: dict) -> str:
        technology = args.get("technology", "").lower()
        feature = args.get("feature", "").lower()
        results = []
        for spec in self._specs:
            searchable = f"{spec.get('id','')} {spec.get('title','')} {spec.get('content','')}".lower()
            if technology in searchable or feature in searchable:
                results.append(spec)
        # Also check graph entities
        if not results:
            entities = self.graph.search(feature or technology)
            for e in entities:
                if e.entity_type.value == "spec":
                    results.append({"id": e.id, "title": e.properties.get("full_name", e.name),
                                    "content": e.properties.get("description", "")})
        if not results:
            return f"No specs found for '{technology} {feature}'. Try: 5g, ran, amf, upf, n2, n3, pfcp."
        lines = [f"Found {len(results)} spec entries:"]
        for r in results[:5]:
            lines.append(f"  • {r.get('title', r.get('id', ''))}: {r.get('content', '')[:150]}")
        return "\n".join(lines)

    def runbook_search(self, args: dict) -> str:
        error_type = args.get("error_type", "").lower()
        service = args.get("service", "").lower()
        results = []
        for rb in self._runbooks:
            searchable = f"{rb.get('title','')} {rb.get('service','')} {rb.get('error_type','')} {rb.get('steps','')}".lower()
            if error_type in searchable or service in searchable:
                results.append(rb)
        if not results:
            entities = self.graph.search(service or error_type)
            incidents = [e for e in entities if e.entity_type.value == "incident"]
            for inc in incidents:
                rb_id = inc.properties.get("runbook", "")
                results.append({"title": f"Runbook for {inc.name}", "service": inc.name,
                                "steps": inc.properties.get("description", "See incident details.")})
        if not results:
            return f"No runbooks found for '{error_type}' '{service}'. Try: amf, upf, outage, latency."
        lines = [f"Found {len(results)} runbooks:"]
        for r in results[:5]:
            lines.append(f"  • {r.get('title', '')} ({r.get('service', '')})")
            if "steps" in r:
                steps = r["steps"] if isinstance(r["steps"], str) else "\n".join(r["steps"])
                lines.append(f"    Steps: {str(steps)[:200]}")
        return "\n".join(lines)

    def service_map(self, args: dict) -> str:
        service_name = args.get("service_name", "")
        entity = self.graph.get_entity(service_name)
        if not entity:
            return f"Service '{service_name}' not found. Try: amf, smf, upf, gnb, pcf."
        lines = [f"Service Map for {entity.name} ({entity.properties.get('full_name', '')})",
                 f"  Domain: {entity.properties.get('domain', 'unknown')}",
                 f"  Description: {entity.properties.get('description', '')[:200]}",
                 f"  Connected services:"]
        for rel in entity.relationships:
            target = self.graph.entities.get(rel["target"])
            if target:
                lines.append(f"    → {target.name} via {rel['relation']} ({target.properties.get('full_name', '')})")
        return "\n".join(lines)
