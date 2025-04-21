// Function to get CSRF token from meta tag or input field
function getCsrfToken() {
    // Look for meta tag first (current method)
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (metaToken) return metaToken;
    
    // Then look for hidden input (quart-wtf method)
    const inputToken = document.querySelector('input[name="csrf_token"]')?.value;
    return inputToken || '';
}

// Function to handle adding videos to queue (improved for WTForms compatibility)
function initAddTrackButtons() {
    document.querySelectorAll('.add-track-btn').forEach(button => {
        button.addEventListener('click', function() {
            const btn = this;
            const originalText = btn.innerHTML;
            
            // Show loading state
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Adding...';
            btn.disabled = true;
            
            // Create a proper form submission matching the AddToQueueForm structure
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${btn.dataset.guildId}/queue/add`;
            form.style.display = 'none';
            
            // CSRF Token
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = getCsrfToken();
            form.appendChild(csrfInput);
            
            // Channel ID
            const channelInput = document.createElement('input');
            channelInput.type = 'hidden';
            channelInput.name = 'channel_id';
            channelInput.value = btn.dataset.channelId;
            form.appendChild(channelInput);
            
            // Video ID
            const videoIdInput = document.createElement('input');
            videoIdInput.type = 'hidden';
            videoIdInput.name = 'video_id';
            videoIdInput.value = btn.dataset.videoId;
            form.appendChild(videoIdInput);
            
            // Video Title
            const videoTitleInput = document.createElement('input');
            videoTitleInput.type = 'hidden';
            videoTitleInput.name = 'video_title';
            videoTitleInput.value = btn.dataset.videoTitle;
            form.appendChild(videoTitleInput);
            
            // Return to
            const returnToInput = document.createElement('input');
            returnToInput.type = 'hidden';
            returnToInput.name = 'return_to';
            returnToInput.value = 'dashboard';
            form.appendChild(returnToInput);
            
            // Add form to the document and submit
            document.body.appendChild(form);
            
            form.onsubmit = () => {
                // Add success notification
                showToast(`✅ Added "${btn.dataset.videoTitle}" to the queue.`);
                
                // Restore button state after a short delay
                setTimeout(() => {
                    btn.innerHTML = '<i class="fas fa-check me-1"></i> Added!';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }, 2000);
                }, 1000);
                
                // Remove the form from DOM
                setTimeout(() => form.remove(), 100);
            };
            
            form.submit();
        });
    });
}

// Function to properly handle playlist selection for WTForms
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
        
        // Add new hidden inputs for each checked video - using WTForms FieldList format
        videoCheckboxes.forEach((checkbox, index) => {
            if (checkbox.checked) {
                selectedCount++;
                
                const videoId = checkbox.getAttribute('data-video-id');
                const videoTitle = checkbox.getAttribute('data-video-title');
                
                // Create hidden input for video ID
                const idInput = document.createElement('input');
                idInput.type = 'hidden';
                idInput.name = `video_ids-${index}`;  // Match WTForms FieldList naming format
                idInput.value = videoId;
                selectedVideosContainer.appendChild(idInput);
                
                // Create hidden input for video title
                const titleInput = document.createElement('input');
                titleInput.type = 'hidden';
                titleInput.name = `video_titles-${index}`;  // Match WTForms FieldList naming format
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
    
    // Add form submission validation
    if (addMultipleForm) {
        addMultipleForm.addEventListener('submit', function(event) {
            // Check if any videos are selected
            const selectedVideos = document.querySelectorAll('input[name^="video_ids-"]');
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

// Initialize queue drag-and-drop with proper form submission
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
    
    // Use WTForms structure for the reorder form
    function updateQueueOrder(oldIndex, newIndex) {
        const container = document.querySelector('.container-fluid');
        const guildId = container ? container.dataset.guildId : null;
        const channelId = container ? container.dataset.channelId : null;
        
        if (!guildId || !channelId) return;
        
        // Create a form that matches ReorderQueueForm structure
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/server/${guildId}/queue/reorder`;
        form.style.display = 'none';
        
        // CSRF Token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = getCsrfToken();
        form.appendChild(csrfInput);
        
        // Channel ID
        const channelInput = document.createElement('input');
        channelInput.type = 'hidden';
        channelInput.name = 'channel_id';
        channelInput.value = channelId;
        form.appendChild(channelInput);
        
        // Old Index
        const oldIndexInput = document.createElement('input');
        oldIndexInput.type = 'hidden';
        oldIndexInput.name = 'old_index';
        oldIndexInput.value = oldIndex;
        form.appendChild(oldIndexInput);
        
        // New Index
        const newIndexInput = document.createElement('input');
        newIndexInput.type = 'hidden';
        newIndexInput.name = 'new_index';
        newIndexInput.value = newIndex;
        form.appendChild(newIndexInput);
        
        // Add form to the document and submit
        document.body.appendChild(form);
        form.submit();
        
        // Remove the form after submission
        setTimeout(() => form.remove(), 100);
    }
}

// Initialize all dashboard features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initQueueDragDrop();
    initPlaylistSelection();
    initAddTrackButtons();
    
    // Check for server dashboard page
    if (document.querySelector('.container-fluid[data-guild-id]')) {
        console.log('Server dashboard loaded, initializing all components');
    }
});

// Toast notification system
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