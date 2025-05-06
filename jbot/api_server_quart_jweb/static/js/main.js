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

// Add this to static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
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
            
            // Create form dynamically
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/bot/join`;
            
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
            
            // Submit form
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
            
            // Create form dynamically
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/bot/leave`;
            
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
            
            // Submit form
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Handle Add Track buttons
    const addTrackBtns = document.querySelectorAll('.add-track-btn');
    addTrackBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const guildId = this.dataset.guildId;
            const channelId = this.dataset.channelId;
            const videoId = this.dataset.videoId;
            const videoTitle = this.dataset.videoTitle;
            
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
            
            // Add video ID
            const videoIdInput = document.createElement('input');
            videoIdInput.type = 'hidden';
            videoIdInput.name = 'video_id';
            videoIdInput.value = videoId;
            form.appendChild(videoIdInput);
            
            // Add video title
            const videoTitleInput = document.createElement('input');
            videoTitleInput.type = 'hidden';
            videoTitleInput.name = 'video_title';
            videoTitleInput.value = videoTitle;
            form.appendChild(videoTitleInput);
            
            // Submit form
            document.body.appendChild(form);
            form.submit();
        });
    });
    
    // Handle checkbox selection in playlist
    const videoCheckboxes = document.querySelectorAll('.video-checkbox');
    const addSelectedToQueueBtn = document.getElementById('addSelectedToQueueBtn');
    
    videoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Count selected checkboxes
            const selectedCount = document.querySelectorAll('.video-checkbox:checked').length;
            
            // Update add selected button state
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
            
            // Trigger change event on first checkbox to update UI
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
            
            // Create form
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/server/${guildId}/queue/add_multiple`;
            
            // Add CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Add other required fields
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
            
            // Add selected videos
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
            
            // Submit form
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
});

initializeDashboard();