let currentIncidentOffset = 0;
let currentAlertOffset = 0;
const LIMIT = 6;
let isFetching = false;

document.addEventListener('DOMContentLoaded', () => {
    fetchNextIncidents();
    fetchNextAlerts();

    document.getElementById('refresh-btn').addEventListener('click', () => {
        if (!isFetching) {
            isFetching = true;
            document.getElementById('incident-body').innerHTML = '';
            document.getElementById('alert-list').innerHTML = '';
            fetchNextIncidents();
            fetchNextAlerts();
            setTimeout(() => {
                isFetching = false;
            }, 1000);
        }
    });
});

async function fetchNextIncidents() {
    try {
        const response = await fetch(`http://localhost:8000/incidents?limit=${LIMIT}&offset=${currentIncidentOffset}`);
        const data = await response.json();

        if (data.status === 'success' && data.incidents.length > 0) {
            data.incidents.forEach(displayIncident);
            currentIncidentOffset += data.incidents.length;
        } else {
            console.warn("No more incidents to fetch.");
        }
    } catch (error) {
        console.error("Error fetching incidents:", error);
    }
}

function displayIncident(incident) {
    const tbody = document.getElementById('incident-body');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${incident.id}</td>
        <td>${incident.cleaned_text}</td>
        <td>${incident.sentiment}</td>
        <td>${incident.threat_label}</td>
        <td>${incident.confidence_score.toFixed(2)}</td>
        <td>${new Date(incident.timestamp).toLocaleString()}</td>
    `;
    tbody.appendChild(row);
}

async function fetchNextAlerts() {
    try {
        const response = await fetch(`http://localhost:8000/alerts?limit=${LIMIT}&offset=${currentAlertOffset}`);
        const data = await response.json();

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(displayAlert);
            currentAlertOffset += data.length;
        } else {
            console.warn("No more alerts to fetch.");
        }
    } catch (error) {
        console.error("Error fetching alerts:", error);
    }
}

function displayAlert(alert) {
    const alertList = document.getElementById('alert-list');
    const li = document.createElement('li');
    li.textContent = `Alert ID ${alert.id}: ${alert.alert_type} - ${alert.cleaned_text} (${new Date(alert.timestamp).toLocaleString()})`;
    alertList.appendChild(li);
}
