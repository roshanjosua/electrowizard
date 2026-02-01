from backend.graph_model import build_city_graph

def compute_restoration_priority(severity_results):
    G = build_city_graph()

    priority_list = []

    for item in severity_results:
        node = item["node"]
        severity_score = item["severity_score"]
        time_failed = item["time_failed"]

        node_data = G.nodes[node]
        criticality = node_data.get("criticality", 5)

        # Count downstream impact
        downstream_nodes = len(list(G.successors(node)))

        # Priority score (explainable)
        priority_score = (
            severity_score
            + criticality * 15
            + downstream_nodes * 10
            - time_failed * 2
        )

        priority_list.append({
            "node": node,
            "priority_score": round(priority_score, 2),
            "severity_level": item["severity_level"],
            "time_failed": time_failed,
            "downstream_impact": downstream_nodes,
            "cause_chain": item["cause_chain"]
        })

    # Sort highest priority first
    priority_list.sort(key=lambda x: x["priority_score"], reverse=True)

    return priority_list
