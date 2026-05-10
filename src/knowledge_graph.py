"""Telecom Knowledge Graph — 5G Core, RAN, Transport, OSS/BSS entities."""
import json
import os
from typing import Optional
from models import GraphEntity, EntityType


class TelecomKnowledgeGraph:
    """Knowledge graph for telecom domain with 50+ entities."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        self.entities: dict[str, GraphEntity] = {}
        self._build_default_graph()

    def _build_default_graph(self):
        """Build the default 5G telecom knowledge graph."""
        raw = self._get_default_entities()
        for e in raw:
            entity = GraphEntity(
                id=e["id"],
                name=e["name"],
                entity_type=EntityType(e["type"]),
                properties=e.get("properties", {}),
                relationships=e.get("relationships", []),
            )
            self.entities[entity.id] = entity

    def get_entity(self, name_or_id: str) -> Optional[GraphEntity]:
        name_lower = name_or_id.lower().replace("-", "").replace("_", "").replace(" ", "")
        for e in self.entities.values():
            eid = e.id.lower().replace("-", "").replace("_", "")
            ename = e.name.lower().replace("-", "").replace("_", "").replace(" ", "")
            if name_lower in (eid, ename) or name_lower in eid or name_lower in ename:
                return e
        return None

    def get_neighbors(self, entity_id: str, relation_type: str = None) -> list[GraphEntity]:
        entity = self.entities.get(entity_id)
        if not entity:
            return []
        neighbors = []
        for rel in entity.relationships:
            if relation_type and rel.get("relation") != relation_type:
                continue
            target = self.entities.get(rel["target"])
            if target:
                neighbors.append(target)
        return neighbors

    def traverse(self, start_id: str, max_depth: int = 2) -> list[GraphEntity]:
        visited = set()
        result = []
        queue = [(start_id, 0)]
        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            entity = self.entities.get(current_id)
            if entity:
                result.append(entity)
                for rel in entity.relationships:
                    if rel["target"] not in visited:
                        queue.append((rel["target"], depth + 1))
        return result

    def shortest_path(self, start_id: str, end_id: str) -> list[GraphEntity]:
        if start_id == end_id:
            e = self.entities.get(start_id)
            return [e] if e else []
        visited = {start_id}
        queue = [(start_id, [start_id])]
        while queue:
            current, path = queue.pop(0)
            entity = self.entities.get(current)
            if not entity:
                continue
            for rel in entity.relationships:
                target = rel["target"]
                if target == end_id:
                    return [self.entities[tid] for tid in path + [target] if tid in self.entities]
                if target not in visited:
                    visited.add(target)
                    queue.append((target, path + [target]))
        return []

    def search(self, keyword: str) -> list[GraphEntity]:
        keyword_lower = keyword.lower()
        results = []
        for e in self.entities.values():
            searchable = f"{e.id} {e.name} {e.properties.get('full_name', '')} {e.properties.get('description', '')} {' '.join(e.properties.get('aliases', []))}".lower()
            if keyword_lower in searchable:
                results.append(e)
        return results

    def expand_subgraph(self, seed_id: str, max_depth: int = 3) -> list[GraphEntity]:
        """OpenSeeker-v2's graph scaling: expand from seed with increasing depth."""
        return self.traverse(seed_id, max_depth=max_depth)

    def get_random_entities(self, n: int) -> list[GraphEntity]:
        import random
        return random.sample(list(self.entities.values()), min(n, len(self.entities)))

    def _get_default_entities(self) -> list[dict]:
        return [
            # === 5G CORE NETWORK ===
            {"id": "amf", "name": "AMF", "type": "service",
             "properties": {"full_name": "Access and Mobility Management Function", "domain": "5g_core",
                            "description": "Manages UE registration, mobility, and connection. First point of contact for UE attaching to 5G network.",
                            "aliases": ["access mobility function", "mobility management"]},
             "relationships": [{"target": "gnb", "relation": "N2"}, {"target": "smf", "relation": "N11"},
                               {"target": "udm", "relation": "N8"}, {"target": "ausf", "relation": "N12"},
                               {"target": "nrf", "relation": "discovery"}, {"target": "nssf", "relation": "N22"},
                               {"target": "pcf", "relation": "N15"}]},
            {"id": "smf", "name": "SMF", "type": "service",
             "properties": {"full_name": "Session Management Function", "domain": "5g_core",
                            "description": "Manages PDU sessions, IP address allocation, UPF selection. Controls user plane via N4.",
                            "aliases": ["session management", "pdu session"]},
             "relationships": [{"target": "amf", "relation": "N11"}, {"target": "upf", "relation": "N4"},
                               {"target": "udm", "relation": "N10"}, {"target": "nrf", "relation": "discovery"},
                               {"target": "pcf", "relation": "N7"}, {"target": "nssf", "relation": "N23"}]},
            {"id": "upf", "name": "UPF", "type": "service",
             "properties": {"full_name": "User Plane Function", "domain": "5g_core",
                            "description": "Routes user data packets between RAN and data network. Handles packet inspection, QoS enforcement.",
                            "aliases": ["user plane", "data plane", "packet forwarding"]},
             "relationships": [{"target": "gnb", "relation": "N3"}, {"target": "smf", "relation": "N4"},
                               {"target": "dn", "relation": "N6"}, {"target": "nrf", "relation": "discovery"}]},
            {"id": "udm", "name": "UDM", "type": "service",
             "properties": {"full_name": "Unified Data Management", "domain": "5g_core",
                            "description": "Stores subscriber data, generates authentication vectors. 5G equivalent of HSS.",
                            "aliases": ["unified data", "subscriber data", "hss"]},
             "relationships": [{"target": "amf", "relation": "N8"}, {"target": "smf", "relation": "N10"},
                               {"target": "ausf", "relation": "N13"}, {"target": "nrf", "relation": "discovery"}]},
            {"id": "ausf", "name": "AUSF", "type": "service",
             "properties": {"full_name": "Authentication Server Function", "domain": "5g_core",
                            "description": "Authenticates UEs using 5G-AKA or EAP-AKA. Works with UDM for credential verification.",
                            "aliases": ["authentication server", "5g aka"]},
             "relationships": [{"target": "amf", "relation": "N12"}, {"target": "udm", "relation": "N13"},
                               {"target": "nrf", "relation": "discovery"}]},
            {"id": "nrf", "name": "NRF", "type": "service",
             "properties": {"full_name": "Network Repository Function", "domain": "5g_core",
                            "description": "Service discovery for all 5G core functions. Maintains registry of available NF instances.",
                            "aliases": ["service discovery", "registry"]},
             "relationships": [{"target": "amf", "relation": "discovery"}, {"target": "smf", "relation": "discovery"},
                               {"target": "upf", "relation": "discovery"}, {"target": "pcf", "relation": "discovery"},
                               {"target": "udm", "relation": "discovery"}, {"target": "ausf", "relation": "discovery"}]},
            {"id": "pcf", "name": "PCF", "type": "service",
             "properties": {"full_name": "Policy Control Function", "domain": "5g_core",
                            "description": "Manages QoS policies, charging policies, and service-specific policies for sessions.",
                            "aliases": ["policy control", "qos policy"]},
             "relationships": [{"target": "smf", "relation": "N7"}, {"target": "amf", "relation": "N15"},
                               {"target": "nrf", "relation": "discovery"}]},
            {"id": "nef", "name": "NEF", "type": "service",
             "properties": {"full_name": "Network Exposure Function", "domain": "5g_core",
                            "description": "Exposes 5G network capabilities to external applications via APIs. Maps to CAMARA APIs.",
                            "aliases": ["network exposure", "api gateway", "camara"]},
             "relationships": [{"target": "nrf", "relation": "discovery"}, {"target": "pcf", "relation": "policy"},
                               {"target": "udm", "relation": "data"}]},
            {"id": "nssf", "name": "NSSF", "type": "service",
             "properties": {"full_name": "Network Slice Selection Function", "domain": "5g_core",
                            "description": "Selects appropriate network slice for UE based on subscription and requested service.",
                            "aliases": ["slice selection", "network slicing"]},
             "relationships": [{"target": "amf", "relation": "N22"}, {"target": "nrf", "relation": "discovery"}]},
            # === RAN ===
            {"id": "gnb", "name": "gNB", "type": "service",
             "properties": {"full_name": "next-generation Node B", "domain": "ran",
                            "description": "5G radio base station. Split into CU (Centralized Unit), DU (Distributed Unit), RU (Radio Unit) in O-RAN.",
                            "aliases": ["base station", "enodeb", "o-cu", "o-du"]},
             "relationships": [{"target": "amf", "relation": "N2"}, {"target": "upf", "relation": "N3"},
                               {"target": "ue", "relation": "Uu"}, {"target": "ric", "relation": "A1"},
                               {"target": "cu", "relation": "F1"}, {"target": "du", "relation": "F1"}]},
            {"id": "cu", "name": "O-CU", "type": "service",
             "properties": {"full_name": "O-RAN Centralized Unit", "domain": "ran",
                            "description": "Handles RRC, SDAP, PDCP layers in O-RAN architecture.",
                            "aliases": ["centralized unit", "oran cu"]},
             "relationships": [{"target": "gnb", "relation": "F1"}, {"target": "du", "relation": "F1"},
                               {"target": "ric", "relation": "E2"}]},
            {"id": "du", "name": "O-DU", "type": "service",
             "properties": {"full_name": "O-RAN Distributed Unit", "domain": "ran",
                            "description": "Handles RLC, MAC, upper-PHY layers in O-RAN.",
                            "aliases": ["distributed unit", "oran du"]},
             "relationships": [{"target": "cu", "relation": "F1"}, {"target": "ru", "relation": "O-RAN FH"},
                               {"target": "gnb", "relation": "F1"}]},
            {"id": "ru", "name": "O-RU", "type": "service",
             "properties": {"full_name": "O-RAN Radio Unit", "domain": "ran",
                            "description": "Handles lower-PHY and RF processing. Antenna interface.",
                            "aliases": ["radio unit", "oran ru", "antenna"]},
             "relationships": [{"target": "du", "relation": "O-RAN FH"}]},
            {"id": "ric", "name": "RIC", "type": "service",
             "properties": {"full_name": "RAN Intelligent Controller", "domain": "ran",
                            "description": "AI/ML-driven RAN optimization. Near-RT RIC (10ms-1s) and Non-RT RIC (>1s). Enables rApps and xApps.",
                            "aliases": ["ran intelligent controller", "near-rt ric", "non-rt ric", "rapp", "xapp"]},
             "relationships": [{"target": "gnb", "relation": "A1"}, {"target": "cu", "relation": "E2"},
                               {"target": "smo", "relation": "O1"}]},
            {"id": "ue", "name": "UE", "type": "service",
             "properties": {"full_name": "User Equipment", "domain": "ran",
                            "description": "End-user device (phone, IoT, CPE). Connects to gNB via Uu interface.",
                            "aliases": ["user equipment", "phone", "device", "mobile"]},
             "relationships": [{"target": "gnb", "relation": "Uu"}]},
            {"id": "smo", "name": "SMO", "type": "service",
             "properties": {"full_name": "Service Management and Orchestration", "domain": "ran",
                            "description": "O-RAN management platform. Orchestrates O-CU, O-DU, O-RU lifecycle.",
                            "aliases": ["orchestration", "o1", "ran management"]},
             "relationships": [{"target": "ric", "relation": "O1"}, {"target": "cu", "relation": "O1"},
                               {"target": "du", "relation": "O1"}, {"target": "ru", "relation": "O1"}]},
            # === INTERFACES ===
            {"id": "n1", "name": "N1", "type": "interface",
             "properties": {"full_name": "UE-AMF NAS Signaling", "domain": "interface",
                            "description": "NAS signaling between UE and AMF. Registration, authentication, session management."},
             "relationships": [{"target": "ue", "relation": "endpoint"}, {"target": "amf", "relation": "endpoint"}]},
            {"id": "n2", "name": "N2", "type": "interface",
             "properties": {"full_name": "gNB-AMF NGAP", "domain": "interface",
                            "description": "NGAP signaling between gNB and AMF. Carries NAS messages, handover commands."},
             "relationships": [{"target": "gnb", "relation": "endpoint"}, {"target": "amf", "relation": "endpoint"}]},
            {"id": "n3", "name": "N3", "type": "interface",
             "properties": {"full_name": "gNB-UPF GTP-U", "domain": "interface",
                            "description": "User plane tunnel between gNB and UPF using GTP-U protocol."},
             "relationships": [{"target": "gnb", "relation": "endpoint"}, {"target": "upf", "relation": "endpoint"}]},
            {"id": "n4", "name": "N4", "type": "interface",
             "properties": {"full_name": "SMF-UPF PFCP", "domain": "interface",
                            "description": "PFCP session management between SMF and UPF. Rules for packet forwarding, QoS."},
             "relationships": [{"target": "smf", "relation": "endpoint"}, {"target": "upf", "relation": "endpoint"}]},
            # === TRANSPORT ===
            {"id": "backhaul", "name": "Backhaul", "type": "service",
             "properties": {"full_name": "Backhaul Network", "domain": "transport",
                            "description": "Links gNB to 5G Core. Typically fiber or microwave. Carries N2/N3 traffic."},
             "relationships": [{"target": "gnb", "relation": "connects"}, {"target": "amf", "relation": "carries"},
                               {"target": "upf", "relation": "carries"}]},
            {"id": "fronthaul", "name": "Fronthaul", "type": "service",
             "properties": {"full_name": "Fronthaul Network", "domain": "transport",
                            "description": "O-RAN fronthaul between O-DU and O-RU. Carries IQ samples via eCPRI."},
             "relationships": [{"target": "du", "relation": "connects"}, {"target": "ru", "relation": "connects"}]},
            # === DATA NETWORK ===
            {"id": "dn", "name": "DN", "type": "service",
             "properties": {"full_name": "Data Network", "domain": "external",
                            "description": "External data network (internet, enterprise intranet). UPF connects via N6."},
             "relationships": [{"target": "upf", "relation": "N6"}]},
            # === OSS/BSS ===
            {"id": "tmf622", "name": "TMF622", "type": "service",
             "properties": {"full_name": "Product Ordering API", "domain": "oss",
                            "description": "TM Forum API for managing product orders. Create, update, track orders."},
             "relationships": [{"target": "tmf640", "relation": "fulfillment"}, {"target": "tmf641", "relation": "qualification"}]},
            {"id": "tmf640", "name": "TMF640", "type": "service",
             "properties": {"full_name": "Service Activation API", "domain": "oss",
                            "description": "TM Forum API for activating services. Configuration, activation, completion."},
             "relationships": [{"target": "tmf622", "relation": "ordering"}, {"target": "nssf", "relation": "slice"}]},
            {"id": "tmf641", "name": "TMF641", "type": "service",
             "properties": {"full_name": "Service Qualification API", "domain": "oss",
                            "description": "TM Forum API for checking service availability at address/location."},
             "relationships": [{"target": "tmf622", "relation": "ordering"}, {"target": "gnb", "relation": "coverage"}]},
            # === CAMARA ===
            {"id": "camara-device", "name": "DeviceStatus", "type": "service",
             "properties": {"full_name": "CAMARA Device Status API", "domain": "camara",
                            "description": "Check if device is reachable, roaming status, battery level."},
             "relationships": [{"target": "nef", "relation": "exposes"}, {"target": "ue", "relation": "monitors"}]},
            {"id": "camara-qod", "name": "QoD", "type": "service",
             "properties": {"full_name": "CAMARA Quality-on-Demand API", "domain": "camara",
                            "description": "Request QoS profiles (latency, throughput) for specific device sessions."},
             "relationships": [{"target": "nef", "relation": "exposes"}, {"target": "pcf", "relation": "policy"},
                               {"target": "upf", "relation": "enforces"}]},
            {"id": "camara-simswap", "name": "SIMSwap", "type": "service",
             "properties": {"full_name": "CAMARA SIM Swap API", "domain": "camara",
                            "description": "Check if SIM was recently swapped. Used for fraud detection."},
             "relationships": [{"target": "nef", "relation": "exposes"}, {"target": "udm", "relation": "subscriber"}]},
            {"id": "camara-numverify", "name": "NumberVerification", "type": "service",
             "properties": {"full_name": "CAMARA Number Verification API", "domain": "camara",
                            "description": "Verify phone number matches the one on device. Authentication use case."},
             "relationships": [{"target": "nef", "relation": "exposes"}, {"target": "udm", "relation": "subscriber"}]},
            # === INCIDENTS/RUNBOOKS ===
            {"id": "inc-amf-down", "name": "AMF Outage", "type": "incident",
             "properties": {"full_name": "AMF Service Outage", "domain": "incident", "severity": "P1",
                            "description": "AMF becomes unreachable. All new UE registrations fail. Existing sessions may drop.",
                            "runbook": "RB-001"},
             "relationships": [{"target": "amf", "relation": "affects"}, {"target": "ue", "relation": "impacts"},
                               {"target": "gnb", "relation": "impacts"}]},
            {"id": "inc-upf-latency", "name": "UPF High Latency", "type": "incident",
             "properties": {"full_name": "UPF Packet Processing Delay", "domain": "incident", "severity": "P2",
                            "description": "UPF experiencing high latency. User traffic delayed. Possible buffer overflow or CPU spike.",
                            "runbook": "RB-002"},
             "relationships": [{"target": "upf", "relation": "affects"}, {"target": "smf", "relation": "escalate"},
                               {"target": "dn", "relation": "impacts"}]},
            {"id": "inc-slice-fail", "name": "Slice Allocation Failure", "type": "incident",
             "properties": {"full_name": "Network Slice Allocation Failure", "domain": "incident", "severity": "P2",
                            "description": "NSSF fails to allocate requested slice. UE gets default slice or rejected.",
                            "runbook": "RB-003"},
             "relationships": [{"target": "nssf", "relation": "affects"}, {"target": "amf", "relation": "escalate"},
                               {"target": "pcf", "relation": "policy"}]},
            # === SPECS ===
            {"id": "spec-23502", "name": "TS 23.502", "type": "spec",
             "properties": {"full_name": "3GPP TS 23.502", "domain": "spec",
                            "description": "5G System Procedures. Registration, PDU session, handover, network slicing procedures."},
             "relationships": [{"target": "amf", "relation": "defines"}, {"target": "smf", "relation": "defines"}]},
            {"id": "spec-23501", "name": "TS 23.501", "type": "spec",
             "properties": {"full_name": "3GPP TS 23.501", "domain": "spec",
                            "description": "5G System Architecture. Defines all NFs, interfaces, and their interactions."},
             "relationships": [{"target": "amf", "relation": "defines"}, {"target": "smf", "relation": "defines"},
                               {"target": "upf", "relation": "defines"}]},
        ]

    def stats(self) -> dict:
        return {
            "total_entities": len(self.entities),
            "by_type": {t.value: sum(1 for e in self.entities.values() if e.entity_type == t) for t in EntityType},
        }


from typing import Optional
