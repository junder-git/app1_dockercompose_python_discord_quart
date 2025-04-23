// Function to show toast notifications
function showToast(msg) {
    const toast = document.createElement("div");
    toast.textContent = msg;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.left = "50%";
    toast.style.transform = "translateX(-50%)";
    toast.style.background = "#333";
    toast.style.color = "#fff";
    toast.style.padding = "10px 20px";
    toast.style.borderRadius = "5px";
    toast.style.zIndex = 1000;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Function to refresh the queue display
async function refreshQueue(guildId, channelId) {
    try {
        const response = await fetch(`/server/${guildId}/queue?channel_id=${channelId}`);
        if (response.ok) {
            const queueHtml = await response.text();
            document.getElementById('queue-container').innerHTML = queueHtml;
        } else {
            console.error('Failed to refresh queue:', response.statusText);
        }
    } catch (error) {
        console.error('Error refreshing queue:', error);
    }
}

// Initialize all dashboard features
function initializeDashboard() {
    document.addEventListener('DOMContentLoaded', function () {
        console.log('Dashboard initialized.');
    });
}

initializeDashboard();