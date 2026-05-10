# Incident Resolver

## When to Use
Network incidents, outages, degradation events, alarm investigation.

## Instructions
1. Identify the failing service from the alarm
2. Check runbook for known procedures
3. Map blast radius using graph traversal
4. Identify affected downstream services
5. Recommend specific runbook steps

## Severity Levels
- P1: System down (AMF outage, full outage)
- P2: Service degraded (UPF latency, slice failure)
- P3: Warning (approaching thresholds)
- P4: Informational
