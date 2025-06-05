// Enhanced main.js with all functionality and no external dependencies

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
            
            // Re-initialize drag and drop and other functionality after refresh
            initializeDragAndDrop();
            initializeQueueButtons();
        } else {
            console.error('Failed to refresh queue:', response.statusText);
        }
    } catch (error) {
        console.error('Error refreshing queue:', error);
    }
}

// Initialize drag and drop functionality for queue reordering
function initializeDragAndDrop() {
    const queueItems = document.querySelectorAll('.queue-item');
    
    queueItems.forEach((item, index) => {
        item.setAttribute('draggable', 'true');
        item.dataset.index = index;
        
        // Drag start
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', index);
            item.classList.add('dragging');
            console.log('Drag started for item:', index);
        });
        
        // Drag end
        item.addEventListener('dragend', (e) => {
            item.classList.remove('dragging');
            // Remove all dragover classes
            queueItems.forEach(qi => qi.classList.remove('dragover'));
        });
        
        // Drag over
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            item.classList.add('dragover');
        });
        
        // Drag leave
        item.addEventListener('dragleave', (e) => {
            item.classList.remove('dragover');
        });
        
        // Drop
        item.addEventListener('drop', async (e) => {
            e.preventDefault();
            item.classList.remove('dragover');
            
            const draggedIndex = parseInt(e.dataTransfer.getData('text/plain'));
            const targetIndex = parseInt(item.dataset.index);
            
            if (draggedIndex !== targetIndex) {
                console.log(`Moving item from ${draggedIndex} to ${targetIndex}`);
                await reorderQueueItem(draggedIndex, targetIndex);
            }
        });
    });
}

// Function to reorder queue items
async function reorderQueueItem(oldIndex, newIndex) {
    const guildId = document.querySelector('.container-fluid').dataset.guildId;
    const channelId = document.querySelector('.container-fluid').dataset.channelId;
    
    if (!guildId || !channelId) {
        showToast("Missing guild or channel information");
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);
        formData.append('channel_id', channelId);
        formData.append('old_index', oldIndex);
        formData.append('new_index', newIndex);
        
        const response = await fetch(`/server/${guildId}/queue/reorder`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // Refresh the queue to show new order
            await refreshQueue(guildId, channelId);
            showToast("Queue reordered successfully");
        } else {
            showToast("Failed to reorder queue");
        }
    } catch (error) {
        console.error('Error reordering queue:', error);
        showToast("Error reordering queue");
    }
}

// Function to move item to top of queue
async function moveToTop(currentIndex) {
    if (currentIndex === 0) {
        showToast("Track is already at the top");
        return;
    }
    
    const guildId = document.querySelector('.container-fluid').dataset.guildId;
    const channelId = document.querySelector('.container-fluid').dataset.channelId;
    
    if (!guildId || !channelId) {
        showToast("Missing guild or channel information");
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);
        formData.append('channel_id', channelId);
        formData.append('old_index', currentIndex);
        formData.append('new_index', 0);
        
        const response = await fetch(`/server/${guildId}/queue/reorder`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            await refreshQueue(guildId, channelId);
            showToast("Track moved to top");
        } else {
            showToast("Failed to move track");
        }
    } catch (error) {
        console.error('Error moving track to top:', error);
        showToast("Error moving track");
    }
}

// Function to remove item from queue (placeholder for now)
async function removeFromQueue(index) {
    showToast("Remove functionality coming soon - you can clear the entire queue for now");
}

// Initialize queue button functionality
function initializeQueueButtons() {
    // Move to top buttons
    const moveToTopBtns = document.querySelectorAll('.move-to-top-btn');
    moveToTopBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const index = parseInt(this.dataset.index);
            if (!isNaN(index)) {
                moveToTop(index);
            }
        });
    });
    
    // Remove from queue buttons
    const removeFromQueueBtns = document.querySelectorAll('.remove-from-queue-btn');
    removeFromQueueBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const index = parseInt(this.dataset.index);
            if (!isNaN(index)) {
                removeFromQueue(index);
            }
        });
    });
}

// Function to preserve search context when adding to queue
function addToQueueWithContext(videoId, videoTitle) {
    const guildId = document.querySelector('.container-fluid').dataset.guildId;
    const channelId = document.querySelector('.container-fluid').dataset.channelId;
    
    // Get current search context
    const searchQuery = document.getElementById('searchQuery')?.value || '';
    const playlistId = document.querySelector('input[name="playlist_id"]')?.value || '';
    const pageToken = document.querySelector('input[name="page_token"]')?.value || '';
    
    // Create form dynamically
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/server/${guildId}/queue/add`;
    
    // Add CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add channel ID
    const channelInput = document.createElement('input');
    channelInput.type = 'hidden';
    channelInput.name = 'channel_id';
    channelInput.value = channelId;
    form.appendChild(channelInput);
    
    // Add video ID and title
    const videoIdInput = document.createElement('input');
    videoIdInput.type = 'hidden';
    videoIdInput.name = 'video_id';
    videoIdInput.value = videoId;
    form.appendChild(videoIdInput);
    
    const videoTitleInput = document.createElement('input');
    videoTitleInput.type = 'hidden';
    videoTitleInput.name = 'video_title';
    videoTitleInput.value = videoTitle;
    form.appendChild(videoTitleInput);
    
    // Preserve search context
    if (searchQuery) {
        const queryInput = document.createElement('input');
        queryInput.type = 'hidden';
        queryInput.name = 'query';
        queryInput.value = searchQuery;
        form.appendChild(queryInput);
    }
    
    if (playlistId) {
        const playlistInput = document.createElement('input');
        playlistInput.type = 'hidden';
        playlistInput.name = 'playlist_id';
        playlistInput.value = playlistId;
        form.appendChild(playlistInput);
    }
    
    if (pageToken) {
        const pageInput = document.createElement('input');
        pageInput.type = 'hidden';
        pageInput.name = 'page_token';
        pageInput.value = pageToken;
        form.appendChild(pageInput);
    }
    
    // Submit form
    document.body.appendChild(form);
    form.submit();
}

// Initialize dashboard functionality
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Initialize drag and drop for queue
    initializeDragAndDrop();
    
    // Initialize queue buttons
    initializeQueueButtons();
    
    // Handle bot join button click
    const botJoinBtn = document.getElementById('botJoinBtn');
    if (botJoinBtn) {
        botJoinBtn.addEventListener('click', function() {
            const guildId = document.querySelector('.container-fluid').dataset.guildId;
            const channelId = document.querySelector('.container-fluid').dataset.channelId;
            
            if (!channelId) {
                showToast("Please join a voice channel in Discord first");
                return;
            }
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/bot/join`;
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            const channelInput = document.createElement('input');
            channelInput.type = 'hidden';
            channelInput.name = 'channel_id';
            channelInput.value = channelId;
            form.appendChild(channelInput);
            
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Handle bot leave button click
    const botLeaveBtn = document.getElementById('botLeaveBtn');
    if (botLeaveBtn) {
        botLeaveBtn.addEventListener('click', function() {
            const guildId = document.querySelector('.container-fluid').dataset.guildId;
            const channelId = document.querySelector('.container-fluid').dataset.channelId;
            
            if (!channelId) {
                showToast("No voice channel selected");
                return;
            }
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/bot/leave`;
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            const channelInput = document.createElement('input');
            channelInput.type = 'hidden';
            channelInput.name = 'channel_id';
            channelInput.value = channelId;
            form.appendChild(channelInput);
            
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Handle Add Track buttons with context preservation
    const addTrackBtns = document.querySelectorAll('.add-track-btn');
    addTrackBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            const videoId = this.dataset.videoId;
            const videoTitle = this.dataset.videoTitle;
            
            // Use the context-preserving function
            addToQueueWithContext(videoId, videoTitle);
        });
    });
    
    // Handle checkbox selection in playlist
    const videoCheckboxes = document.querySelectorAll('.video-checkbox');
    const addSelectedToQueueBtn = document.getElementById('addSelectedToQueueBtn');
    
    videoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedCount = document.querySelectorAll('.video-checkbox:checked').length;
            
            if (addSelectedToQueueBtn) {
                if (selectedCount > 0) {
                    addSelectedToQueueBtn.disabled = false;
                    addSelectedToQueueBtn.textContent = `Add ${selectedCount} Selected to Queue`;
                } else {
                    addSelectedToQueueBtn.disabled = true;
                    addSelectedToQueueBtn.textContent = 'Add Selected to Queue';
                }
            }
        });
    });
    
    // Handle Select All button
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('.video-checkbox');
            const anyUnchecked = Array.from(checkboxes).some(cb => !cb.checked);
            
            checkboxes.forEach(cb => {
                cb.checked = anyUnchecked;
            });
            
            if (checkboxes.length > 0) {
                checkboxes[0].dispatchEvent(new Event('change'));
            }
        });
    }
    
    // Handle Add Selected to Queue button
    if (addSelectedToQueueBtn) {
        addSelectedToQueueBtn.addEventListener('click', function() {
            const guildId = document.querySelector('.container-fluid').dataset.guildId;
            const channelId = document.querySelector('.container-fluid').dataset.channelId;
            const playlistId = document.querySelector('input[name="playlist_id"]').value;
            const pageToken = document.querySelector('input[name="page_token"]').value;
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/queue/add_multiple`;
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            const channelInput = document.createElement('input');
            channelInput.type = 'hidden';
            channelInput.name = 'channel_id';
            channelInput.value = channelId;
            form.appendChild(channelInput);
            
            const playlistIdInput = document.createElement('input');
            playlistIdInput.type = 'hidden';
            playlistIdInput.name = 'playlist_id';
            playlistIdInput.value = playlistId;
            form.appendChild(playlistIdInput);
            
            const pageTokenInput = document.createElement('input');
            pageTokenInput.type = 'hidden';
            pageTokenInput.name = 'page_token';
            pageTokenInput.value = pageToken;
            form.appendChild(pageTokenInput);
            
            const selectedCheckboxes = document.querySelectorAll('.video-checkbox:checked');
            selectedCheckboxes.forEach((cb, index) => {
                const videoIdInput = document.createElement('input');
                videoIdInput.type = 'hidden';
                videoIdInput.name = `video_ids-${index}`;
                videoIdInput.value = cb.dataset.videoId;
                form.appendChild(videoIdInput);
                
                const videoTitleInput = document.createElement('input');
                videoTitleInput.type = 'hidden';
                videoTitleInput.name = `video_titles-${index}`;
                videoTitleInput.value = cb.dataset.videoTitle;
                form.appendChild(videoTitleInput);
            });
            
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Auto-refresh queue every 10 seconds when a channel is selected
    const channelId = document.querySelector('.container-fluid')?.dataset.channelId;
    const guildId = document.querySelector('.container-fluid')?.dataset.guildId;
    
    if (channelId && guildId) {
        setInterval(() => {
            refreshQueue(guildId, channelId);
        }, 10000);
    }
    
    console.log('Dashboard initialization complete');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    initializeDashboard();
});

// Also call initialize function for cases where script loads after DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}

// Make functions globally available
window.moveToTop = moveToTop;
window.removeFromQueue = removeFromQueue;
window.refreshQueue = refreshQueue;
window.showToast = showToast;
window.initializeDashboard = initializeDashboard;