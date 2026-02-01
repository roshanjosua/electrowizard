from backend.graph_model import build_city_graph

def compute_severity(simulation_events):
    G = build_city_graph()

    severity_results = []

    for event in simulation_events:
        node = event["node"]
        time = event["time"]

        node_data = G.nodes[node]
        criticality = node_data.get("criticality", 5)
        population = node_data.get("population", 0)
        chain_length = len(event.get("cause_chain", []))

        # Severity score formula (simple, explainable)
        score = (
            criticality * 10
            + max(0, (8 - time)) * 5     # earlier failure = higher impact
            + (population / 1000)
            + chain_length * 5
        )

        # Severity category
        if score >= 100:
            level = "Critical"
        elif score >= 70:
            level = "High"
        elif score >= 40:
            level = "Medium"
        else:
            level = "Low"

        severity_results.append({
            "node": node,
            "time_failed": time,
            "severity_score": round(score, 2),
            "severity_level": level,
            "cause_chain": event.get("cause_chain", [])
        })

    return severity_results
