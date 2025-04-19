// Function to get CSRF token from meta tag or input field
function getCsrfToken() {
    // Look for meta tag first (current method)
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (metaToken) return metaToken;
    
    // Then look for hidden input (quart-wtf method)
    const inputToken = document.querySelector('input[name="csrf_token"]')?.value;
    return inputToken || '';
}

// Function to submit forms with CSRF protection
function submitFormWithCsrf(action, additionalData = {}) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;
    form.style.display = 'none';
    
    // Always add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = getCsrfToken();
    form.appendChild(csrfInput);
    
    // Add additional data
    Object.entries(additionalData).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
    });
    
    document.body.appendChild(form);
    form.submit();
}

// Playlist video selection function
function initPlaylistSelection() {
    console.log("Initializing playlist selection...");
    const videoCheckboxes = document.querySelectorAll('.video-checkbox');
    if (videoCheckboxes.length === 0) {
        console.log("No video checkboxes found. Exiting initialization.");
        return;
    }
    
    const selectAllBtn = document.getElementById('selectAllBtn');
    const addSelectedBtn = document.getElementById('addSelectedToQueueBtn');
    const selectedVideosContainer = document.getElementById('selectedVideosContainer');
    const addMultipleForm = document.getElementById('addMultipleForm');
    
    let allSelected = false;
    
    // Function to update the selected videos form
    function updateSelectedVideos() {
        if (!selectedVideosContainer) {
            console.error("selectedVideosContainer not found");
            return;
        }
        
        selectedVideosContainer.innerHTML = '';
        
        // Count selected videos
        let selectedCount = 0;
        
        // Add new hidden inputs for each checked video
        videoCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selectedCount++;
                
                const videoId = checkbox.getAttribute('data-video-id');
                const videoTitle = checkbox.getAttribute('data-video-title');
                
                // Create hidden input for video ID
                const idInput = document.createElement('input');
                idInput.type = 'hidden';
                idInput.name = 'video_ids';
                idInput.value = videoId;
                selectedVideosContainer.appendChild(idInput);
                
                // Create hidden input for video title
                const titleInput = document.createElement('input');
                titleInput.type = 'hidden';
                titleInput.name = 'video_titles';
                titleInput.value = videoTitle;
                selectedVideosContainer.appendChild(titleInput);
            }
        });
        
        // Enable/disable add selected button
        if (addSelectedBtn) {
            addSelectedBtn.disabled = selectedCount === 0;
            
            // Update button text
            if (selectedCount > 0) {
                addSelectedBtn.innerHTML = `<i class="fas fa-plus me-1"></i> Add ${selectedCount} Selected`;
            } else {
                addSelectedBtn.innerHTML = `<i class="fas fa-plus me-1"></i> Add Selected to Queue`;
            }
        }
    }
    
    // Add event listeners to checkboxes
    videoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedVideos();
        });
    });
    
    // Select/deselect all videos
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            allSelected = !allSelected;
            
            videoCheckboxes.forEach(checkbox => {
                checkbox.checked = allSelected;
            });
            
            // Update button text
            if (allSelected) {
                selectAllBtn.innerHTML = `<i class="fas fa-square me-1"></i> Deselect All`;
            } else {
                selectAllBtn.innerHTML = `<i class="fas fa-check-square me-1"></i> Select All`;
            }
            
            updateSelectedVideos();
        });
    }
    
    // Add form submission handling to ensure data is sent
    if (addMultipleForm) {
        addMultipleForm.addEventListener('submit', function(event) {
            // Check if any videos are selected
            const selectedVideos = document.querySelectorAll('input[name="video_ids"]');
            if (selectedVideos.length === 0) {
                event.preventDefault();
                alert('Please select at least one video to add to the queue.');
                return false;
            }
            
            // Add CSRF token if not already present
            if (!addMultipleForm.querySelector('input[name="csrf_token"]')) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = getCsrfToken();
                addMultipleForm.appendChild(csrfInput);
            }
            
            // Allow the form to submit
            return true;
        });
    }
    
    // Initialize
    updateSelectedVideos();
}

// Queue drag and drop functionality
function initQueueDragDrop() {
    const queueList = document.getElementById('queue-list');
    if (!queueList) return;
    
    let draggedItem = null;
    let dragStartIndex = 0;
    
    const queueItems = queueList.querySelectorAll('.queue-item');
    queueItems.forEach((item, index) => {
        item.addEventListener('dragstart', function(e) {
            draggedItem = item;
            dragStartIndex = index;
            
            setTimeout(() => {
                item.classList.add('dragging');
            }, 0);
            
            e.dataTransfer.setData('text/plain', item.dataset.id);
            e.dataTransfer.effectAllowed = 'move';
        });
        
        item.addEventListener('dragend', function() {
            item.classList.remove('dragging');
            draggedItem = null;
        });
        
        item.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            this.classList.add('dragover');
        });
        
        item.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        item.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const dropIndex = Array.from(queueItems).indexOf(this);
            
            if (draggedItem && dragStartIndex !== dropIndex) {
                if (dropIndex < dragStartIndex) {
                    queueList.insertBefore(draggedItem, this);
                } else {
                    queueList.insertBefore(draggedItem, this.nextSibling);
                }
                
                updateQueueOrder(dragStartIndex, dropIndex);
            }
        });
    });
    
    function updateQueueOrder(oldIndex, newIndex) {
        const container = document.querySelector('.container-fluid');
        const guildId = container ? container.dataset.guildId : null;
        const channelId = container ? container.dataset.channelId : null;
        
        if (!guildId || !channelId) return;
        
        submitFormWithCsrf(`/server/${guildId}/queue/reorder`, {
            channel_id: channelId,
            old_index: oldIndex,
            new_index: newIndex
        });
    }
}

// Queue manager with AJAX support
function initQueueManager() {
    const guildId = document.querySelector('[data-guild-id]')?.dataset.guildId;
    const channelId = document.querySelector('[data-channel-id]')?.dataset.channelId;
    
    if (!guildId || !channelId) return;

    function refreshQueueData() {
        fetch(`/server/${guildId}/queue/ajax?channel_id=${channelId}`, {
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                updateQueueDisplay(data);
            })
            .catch(error => console.error('Error refreshing queue:', error));
    }
    
    function updateQueueDisplay(data) {
        const currentTrackDiv = document.getElementById('current-track');
        const queueListDiv = document.getElementById('queue-list');
        const queueEmptyDiv = document.getElementById('queue-empty');
        const botControlsDiv = document.getElementById('bot-controls');
        
        document.querySelectorAll('.bot-status-indicator').forEach(indicator => {
            indicator.classList.add('d-none');
        });
        
        if (data.is_connected) {
            const statusElement = document.getElementById(
                data.is_playing ? 'status-playing' : 
                (data.is_paused ? 'status-paused' : 'status-connected')
            );
            if (statusElement) {
                statusElement.classList.remove('d-none');
            }
        } else {
            const disconnectedStatus = document.getElementById('status-disconnected');
            if (disconnectedStatus) {
                disconnectedStatus.classList.remove('d-none');
            }
        }
        
        if (data.current_track && currentTrackDiv) {
            currentTrackDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="me-2">
                        <i class="fas fa-play-circle text-success"></i>
                    </div>
                    <div>
                        <h6 class="mb-0">Now Playing:</h6>
                        <p class="mb-0">${data.current_track.title}</p>
                    </div>
                </div>
            `;
            currentTrackDiv.classList.remove('d-none');
            
            if (botControlsDiv) {
                botControlsDiv.classList.remove('d-none');
                
                const pauseButton = document.getElementById('pause-button');
                const resumeButton = document.getElementById('resume-button');
                
                if (pauseButton && resumeButton) {
                    if (data.is_paused) {
                        pauseButton.classList.add('d-none');
                        resumeButton.classList.remove('d-none');
                    } else {
                        pauseButton.classList.remove('d-none');
                        resumeButton.classList.add('d-none');
                    }
                }
            }
        } else if (currentTrackDiv) {
            currentTrackDiv.classList.add('d-none');
            
            if (botControlsDiv && !data.is_connected) {
                botControlsDiv.classList.add('d-none');
            }
        }
        
        if (queueListDiv && data.queue) {
            if (data.queue.length > 0) {
                let queueHtml = '';
                data.queue.forEach((item, index) => {
                    queueHtml += `
                        <div class="list-group-item bg-dark text-light border-secondary queue-item" 
                             data-id="${item.id}" draggable="true">
                            <div class="d-flex w-100 justify-content-between align-items-start">
                                <div>
                                    <div class="drag-handle me-2 d-inline-block">
                                        <i class="fas fa-grip-vertical text-muted"></i>
                                    </div>
                                    <h6 class="mb-1 d-inline-block">${item.title}</h6>
                                </div>
                                <span class="badge bg-secondary">${index + 1}</span>
                            </div>
                        </div>
                    `;
                });
                
                queueListDiv.innerHTML = queueHtml;
                queueListDiv.classList.remove('d-none');
                
                if (queueEmptyDiv) {
                    queueEmptyDiv.classList.add('d-none');
                }
                
                initQueueDragDrop();
            } else {
                queueListDiv.innerHTML = '';
                if (queueEmptyDiv) {
                    queueEmptyDiv.classList.remove('d-none');
                }
            }
        }

        const lastRefreshed = document.getElementById('last-refreshed');
        if (lastRefreshed) {
            const now = new Date();
            lastRefreshed.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        }
    }

    document.querySelectorAll('.playback-control, .join-button, #leave-button').forEach(button => {
        button.addEventListener('click', function() {
            setTimeout(refreshQueueData, 500);
        });
    });

    refreshQueueData();
}

// Dynamic link conversion for POST requests
function convertPostLinks() {
    document.querySelectorAll('a[data-method="post"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const additionalData = {};
            Object.keys(this.dataset).forEach(key => {
                if (key !== 'method') {
                    additionalData[key] = this.dataset[key];
                }
            });
            
            const url = this.getAttribute('href');
            submitFormWithCsrf(url, additionalData);
        });
    });
}

// Initialize all dashboard features
document.addEventListener('DOMContentLoaded', function() {
    initQueueDragDrop();
    initPlaylistSelection();
    initQueueManager();
    convertPostLinks();
    
    // Keyboard shortcut for search field
    const searchField = document.getElementById('searchQuery');
    if (searchField) {
        document.addEventListener('keydown', function(e) {
            // Ctrl+/ or Cmd+/ to focus search field
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                searchField.focus();
            }
        });
    }

    // Find all add track buttons
    document.querySelectorAll('.add-track-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const btn = this;
            const originalText = btn.innerHTML;
            
            // Show loading state
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Adding...';
            btn.disabled = true;
            
            try {
                const response = await fetch(`/server/${btn.dataset.guildId}/queue/add_multiple`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: new URLSearchParams({
                        'channel_id': btn.dataset.channelId,
                        'video_ids': btn.dataset.videoId,
                        'video_titles': btn.dataset.videoTitle,
                        'return_to': 'dashboard'
                    })
                });
                
                if (response.ok) {
                    // Show success state
                    btn.innerHTML = '<i class="fas fa-check me-1"></i> Added!';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }, 2000);
                    
                    showToast(`✅ Added "${btn.dataset.videoTitle}" to the queue.`);
                    
                    // Optionally refresh the queue display if you have that function
                    if (typeof refreshQueueData === 'function') {
                        refreshQueueData();
                    }
                } else {
                    // Show error state
                    btn.innerHTML = '<i class="fas fa-times me-1"></i> Error!';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }, 2000);
                    
                    const errorText = await response.text();
                    console.error('Queue error:', errorText);
                    showToast("❌ Failed to add song.");
                }
            } catch (error) {
                // Handle network errors
                btn.innerHTML = '<i class="fas fa-times me-1"></i> Error!';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }, 2000);
                
                console.error('Network error:', error);
                showToast("❌ Network issue.");
            }
        });
    });
    
    // Your existing showToast function
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
});