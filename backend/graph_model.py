import pandas as pd
import networkx as nx
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def build_city_graph():
    nodes_path = os.path.join(DATA_DIR, "infrastructure_nodes.csv")
    edges_path = os.path.join(DATA_DIR, "infrastructure_edges.csv")

    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    G = nx.DiGraph()

    # Add nodes
    for _, row in nodes_df.iterrows():
        G.add_node(
            row["node_id"],
            type=row["node_type"],
            backup_hours=int(row["backup_hours"]),
            criticality=int(row["criticality"]),
            population=0 if pd.isna(row["population"]) else int(row["population"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            status="active"
        )

    # Add edges
    for _, row in edges_df.iterrows():
        G.add_edge(
            row["source"],
            row["target"],
            weight=float(row["weight"]),
            reason=row["reason"]
        )

    return G
