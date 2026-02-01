let severityChart = null;
let map = null;
let mapMarkers = [];

// Initialize map once
window.onload = () => {
    map = L.map("map").setView([12.9716, 77.5946], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
    }).addTo(map);
};

async function runAnalysis() {
    const startNode = document.getElementById("startNode").value;
    const hours = document.getElementById("hours").value;

    const response = await fetch(
        `/analyze?start_node=${startNode}&hours=${hours}`
    );

    const data = await response.json();

    renderPriority(data.priority);
    renderTimeline(data.simulation);
    renderSeverityChart(data.severity);
    renderMap(data.simulation, data.locations);
}

function renderPriority(priority) {
    const tbody = document.querySelector("#priorityTable tbody");
    tbody.innerHTML = "";

    priority.forEach((item, index) => {
        const row = document.createElement("tr");
        const cls = item.severity_level.toLowerCase();

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.node}</td>
            <td class="${cls}">${item.severity_level}</td>
            <td>${item.priority_score}</td>
            <td>${item.cause_chain.join(" → ") || "Root cause"}</td>
        `;

        tbody.appendChild(row);
    });
}

function renderTimeline(simulation) {
    const tbody = document.querySelector("#timelineTable tbody");
    tbody.innerHTML = "";

    simulation.forEach(event => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${event.time}</td>
            <td>${event.node}</td>
            <td>${event.event}</td>
            <td>${event.cause_chain.join(" → ") || "Initial failure"}</td>
        `;

        tbody.appendChild(row);
    });
}

function renderSeverityChart(severity) {
    const ctx = document.getElementById("severityChart").getContext("2d");

    const labels = severity.map(s => s.node);
    const scores = severity.map(s => s.severity_score);

    if (severityChart) severityChart.destroy();

    severityChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Severity Score",
                data: scores,
                maxBarThickness: 40
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderMap(simulation, locations) {
    mapMarkers.forEach(m => map.removeLayer(m));
    mapMarkers = [];

    simulation.forEach(event => {
        const loc = locations[event.node];
        if (!loc) return;

        let color = "green";
        if (event.event === "Backup exhausted") color = "red";
        if (event.event === "Power source failed") color = "black";

        const marker = L.circleMarker([loc.lat, loc.lng], {
            radius: 8,
            color: color,
            fillOpacity: 0.8
        }).addTo(map);

        marker.bindPopup(`
            <b>${event.node}</b><br/>
            Event: ${event.event}<br/>
            Time: ${event.time}h<br/>
            Cause: ${event.cause_chain.join(" → ") || "Initial failure"}
        `);

        mapMarkers.push(marker);
    });
}
