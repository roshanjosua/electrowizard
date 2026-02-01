from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from graph_model import build_city_graph
from simulation import simulate_outage
from severity import compute_severity
from priority import compute_restoration_priority

import os

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)

# Serve frontend
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "OK"})

# Main analysis endpoint
@app.route("/analyze", methods=["GET"])
def analyze_outage():
    start_node = request.args.get("start_node", "Sub_A")
    hours = int(request.args.get("hours", 8))

    # Build graph
    G = build_city_graph()

    # Simulation
    simulation_events = simulate_outage(start_node, max_hours=hours)

    # Severity & priority
    severity_results = compute_severity(simulation_events)
    priority_results = compute_restoration_priority(severity_results)

    # Extract node locations for map
    node_locations = {
        node: {
            "lat": data["latitude"],
            "lng": data["longitude"]
        }
        for node, data in G.nodes(data=True)
    }

    return jsonify({
        "start_node": start_node,
        "duration_hours": hours,
        "simulation": simulation_events,
        "severity": severity_results,
        "priority": priority_results,
        "locations": node_locations
    })

