from backend.graph_model import build_city_graph

def trace_dependency_path(G, start, end):
    """
    Find one dependency path from start → end
    """
    try:
        return list(G.nodes(nx.shortest_path(G, start, end)))
    except:
        return []

def simulate_outage(start_node, max_hours=8):
    import networkx as nx

    G = build_city_graph()

    timeline = []
    node_state = {}
    failure_cause = {}   # <-- NEW

    # Initialize node states
    for node, data in G.nodes(data=True):
        node_state[node] = {
            "status": "active",
            "backup_left": data.get("backup_hours", 0)
        }

    # Initial failure
    node_state[start_node]["status"] = "failed"
    failure_cause[start_node] = []
    timeline.append({
        "time": 0,
        "node": start_node,
        "event": "Power source failed",
        "cause_chain": []
    })

    # Hour-by-hour simulation
    for hour in range(1, max_hours + 1):
        for node in G.nodes():

            if node_state[node]["status"] == "failed":
                continue

            failed_parents = [
                parent for parent in G.predecessors(node)
                if node_state[parent]["status"] == "failed"
            ]

            if failed_parents:
                if node_state[node]["backup_left"] > 0:
                    node_state[node]["backup_left"] -= 1
                    node_state[node]["status"] = "backup"
                else:
                    node_state[node]["status"] = "failed"

                    # Pick primary cause (highest weight edge)
                    primary_parent = failed_parents[0]

                    # Build explainable chain
                    chain = failure_cause.get(primary_parent, []) + [primary_parent, node]
                    failure_cause[node] = chain

                    timeline.append({
                        "time": hour,
                        "node": node,
                        "event": "Backup exhausted",
                        "cause_chain": chain
                    })

        if all(state["status"] == "failed" for state in node_state.values()):
            break

    return timeline
