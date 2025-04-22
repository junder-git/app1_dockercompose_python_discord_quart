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

// Initialize drag-and-drop functionality for the queue
function initQueueDragAndDrop() {
    const queueList = document.getElementById('queue-list');
    if (!queueList) return;

    let draggedItem = null;

    queueList.addEventListener('dragstart', (e) => {
        draggedItem = e.target;
        e.target.style.opacity = '0.5';
    });

    queueList.addEventListener('dragend', (e) => {
        e.target.style.opacity = '';
        draggedItem = null;
    });

    queueList.addEventListener('dragover', (e) => {
        e.preventDefault();
        const afterElement = getDragAfterElement(queueList, e.clientY);
        if (afterElement == null) {
            queueList.appendChild(draggedItem);
        } else {
            queueList.insertBefore(draggedItem, afterElement);
        }
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.queue-item:not(.dragging)')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
}

// Handle bot join button click
document.getElementById('botJoinBtn').addEventListener('click', async function () {
    const channelId = document.querySelector('[data-channel-id]').dataset.channelId;
    const guildId = document.querySelector('[data-guild-id]').dataset.guildId;

    if (!channelId) {
        showToast('❌ No voice channel selected.');
        return;
    }

    try {
        const response = await fetch(`/server/${guildId}/bot/join`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel_id: channelId }),
        });

        if (response.ok) {
            showToast('✅ Bot joined the voice channel.');
        } else {
            const error = await response.json();
            showToast(`❌ Failed to join: ${error.error}`);
        }
    } catch (error) {
        console.error('Error joining voice channel:', error);
        showToast('❌ An error occurred.');
    }
});

// Handle bot leave button click
document.getElementById('botLeaveBtn').addEventListener('click', async function () {
    const guildId = document.querySelector('[data-guild-id]').dataset.guildId;

    try {
        const response = await fetch(`/server/${guildId}/bot/leave`, { method: 'POST' });

        if (response.ok) {
            showToast('✅ Bot left the voice channel and cleared the queue.');
            await refreshQueue(guildId, null); // Clear the queue view
        } else {
            const error = await response.json();
            showToast(`❌ Failed to leave: ${error.error}`);
        }
    } catch (error) {
        console.error('Error leaving voice channel:', error);
        showToast('❌ An error occurred.');
    }
});

// Handle adding tracks to the queue
function initAddTrackButtons() {
    document.querySelectorAll('.add-track-btn').forEach(button => {
        button.addEventListener('click', async function () {
            const btn = this;
            const originalText = btn.innerHTML;

            // Show loading state
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Adding...';
            btn.disabled = true;

            // Prepare form data
            const formData = new FormData();
            formData.append('channel_id', btn.dataset.channelId);
            formData.append('video_id', btn.dataset.videoId);
            formData.append('video_title', btn.dataset.videoTitle);

            try {
                // Send AJAX request
                const response = await fetch(`/server/${btn.dataset.guildId}/queue/add`, {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    showToast(`✅ Added "${btn.dataset.videoTitle}" to the queue.`);
                    await refreshQueue(btn.dataset.guildId, btn.dataset.channelId);
                } else {
                    showToast('❌ Failed to add to the queue.');
                }
            } catch (error) {
                console.error('Error adding to queue:', error);
                showToast('❌ An error occurred.');
            } finally {
                // Restore button state
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    });
}

// Initialize all dashboard features
document.addEventListener('DOMContentLoaded', function () {
    initQueueDragAndDrop();
    initAddTrackButtons();
    console.log('Dashboard initialized.');
});