const WMS_API = "http://localhost:8081";
const CELL_API = "http://localhost:8080";

async function sendPickRequest() {
    const pickId = Number(document.getElementById("pickId").value);
    const quantity = Number(document.getElementById("quantity").value);

    const requestBody = {
        pickId: pickId,
        quantity: quantity
    };

    try {
        const response = await fetch(`${WMS_API}/sendPick`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        document.getElementById("lastResponse").textContent =
            JSON.stringify(data, null, 2);

        await updateDashboard();

    } catch (error) {
        document.getElementById("lastResponse").textContent =
            "Error sending pick request: " + error;
    }
}

async function updateDashboard() {
    await updateCellState();
    await updateLastRequest();
    await updateLastConfirmation();
}

async function updateCellState() {
    try {
        const response = await fetch(`${CELL_API}/state`);
        const state = await response.json();

        document.getElementById("doorState").textContent =
            state.doorClosed ? "Closed" : "Open";

        document.getElementById("emergencyState").textContent =
            state.emergencyPressed ? "Pressed" : "Not pressed";

        updateStackLight(state.stackLight);

    } catch (error) {
        document.getElementById("doorState").textContent = "API not available";
        document.getElementById("emergencyState").textContent = "API not available";
        updateStackLight(null);
    }
}

async function updateLastRequest() {
    try {
        const response = await fetch(`${WMS_API}/lastRequest`);
        const data = await response.json();

        document.getElementById("lastRequest").textContent =
            data ? JSON.stringify(data, null, 2) : "No request yet";

    } catch (error) {
        document.getElementById("lastRequest").textContent =
            "Could not load last request";
    }
}

async function updateLastConfirmation() {
    try {
        const response = await fetch(`${WMS_API}/lastConfirmation`);
        const data = await response.json();

        document.getElementById("lastResponse").textContent =
            data ? JSON.stringify(data, null, 2) : "No response yet";

    } catch (error) {
        document.getElementById("lastResponse").textContent =
            "Could not load last response";
    }
}

function updateStackLight(stackLightValue) {
    const shape = document.getElementById("stackLightShape");
    const text = document.getElementById("stackLightText");

    shape.className = "stack-light";

    if (stackLightValue === 0) {
        shape.classList.add("green");
        text.textContent = "Operational / Green";
    } else if (stackLightValue === 1) {
        shape.classList.add("yellow");
        text.textContent = "Paused / Yellow";
    } else if (stackLightValue === -1) {
        shape.classList.add("red");
        text.textContent = "Emergency / Red";
    } else {
        shape.classList.add("unknown");
        text.textContent = "Unknown";
    }
}

setInterval(updateDashboard, 1000);
updateDashboard();