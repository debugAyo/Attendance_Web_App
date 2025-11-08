// Offline Attendance Handler
class OfflineAttendance {
    constructor() {
        this.storageKey = 'offline_attendance_queue';
        this.membersKey = 'cached_members';
        this.servicesKey = 'cached_services';
        this.init();
    }

    init() {
        this.updateOnlineStatus();
        this.displayPendingCount();
        
        // Update status every 5 seconds
        setInterval(() => {
            this.updateOnlineStatus();
        }, 5000);

        // Auto-sync when coming back online
        window.addEventListener('online', () => {
            this.updateOnlineStatus();
            this.autoSync();
        });

        window.addEventListener('offline', () => {
            this.updateOnlineStatus();
        });
    }

    updateOnlineStatus() {
        const statusBadge = document.getElementById('connection-status');
        const syncButton = document.getElementById('sync-button');
        
        if (navigator.onLine) {
            statusBadge.className = 'badge bg-success';
            statusBadge.innerHTML = '<i class="fa fa-wifi"></i> Online';
            if (syncButton) syncButton.disabled = false;
        } else {
            statusBadge.className = 'badge bg-warning';
            statusBadge.innerHTML = '<i class="fa fa-wifi"></i> Offline Mode';
            if (syncButton) syncButton.disabled = true;
        }
    }

    // Cache members data for offline use
    cacheMembers(members) {
        localStorage.setItem(this.membersKey, JSON.stringify(members));
    }

    // Cache services data
    cacheServices(services) {
        localStorage.setItem(this.servicesKey, JSON.stringify(services));
    }

    // Get cached members
    getCachedMembers() {
        const data = localStorage.getItem(this.membersKey);
        return data ? JSON.parse(data) : [];
    }

    // Get cached services
    getCachedServices() {
        const data = localStorage.getItem(this.servicesKey);
        return data ? JSON.parse(data) : [];
    }

    // Search members by name or phone
    searchMembers(query) {
        const members = this.getCachedMembers();
        const lowerQuery = query.toLowerCase();
        
        return members.filter(member => 
            member.name.toLowerCase().includes(lowerQuery) ||
            member.phone.includes(query)
        );
    }

    // Mark attendance offline
    markAttendance(memberData) {
        const queue = this.getQueue();
        
        const attendance = {
            id: Date.now(),
            member_id: memberData.id,
            member_name: memberData.name,
            member_phone: memberData.phone,
            service_id: memberData.service_id,
            service_name: memberData.service_name,
            timestamp: new Date().toISOString(),
            synced: false
        };

        queue.push(attendance);
        this.saveQueue(queue);
        this.displayPendingCount();
        
        return attendance;
    }

    // Get pending queue
    getQueue() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : [];
    }

    // Save queue
    saveQueue(queue) {
        localStorage.setItem(this.storageKey, JSON.stringify(queue));
    }

    // Display pending count
    displayPendingCount() {
        const queue = this.getQueue();
        const pendingCount = queue.filter(item => !item.synced).length;
        const badge = document.getElementById('pending-count');
        
        if (badge) {
            badge.textContent = pendingCount;
            badge.className = pendingCount > 0 ? 'badge bg-danger ms-2' : 'badge bg-secondary ms-2';
        }

        // Update sync button text
        const syncButton = document.getElementById('sync-button');
        if (syncButton && pendingCount > 0) {
            syncButton.innerHTML = `<i class="fa fa-sync"></i> Sync Now (${pendingCount})`;
        } else if (syncButton) {
            syncButton.innerHTML = '<i class="fa fa-check"></i> All Synced';
        }
    }

    // Display pending list
    displayPendingList() {
        const queue = this.getQueue();
        const pending = queue.filter(item => !item.synced);
        const container = document.getElementById('pending-list');
        
        if (!container) return;

        if (pending.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No pending attendance to sync</p>';
            return;
        }

        let html = '<div class="list-group">';
        pending.forEach(item => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${item.member_name}</strong>
                            <br>
                            <small class="text-muted">${item.member_phone} • ${item.service_name}</small>
                            <br>
                            <small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small>
                        </div>
                        <span class="badge bg-warning">Pending</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    // Sync all pending attendance to server
    async syncAll() {
        if (!navigator.onLine) {
            this.showAlert('Cannot sync while offline. Please check your connection.', 'warning');
            return;
        }

        const queue = this.getQueue();
        const pending = queue.filter(item => !item.synced);

        if (pending.length === 0) {
            this.showAlert('No pending attendance to sync', 'info');
            return;
        }

        const syncButton = document.getElementById('sync-button');
        if (syncButton) {
            syncButton.disabled = true;
            syncButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Syncing...';
        }

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch('/admin/sync-offline-attendance/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ attendance: pending })
            });

            const result = await response.json();

            if (result.success) {
                // Mark all as synced
                queue.forEach(item => {
                    if (!item.synced) item.synced = true;
                });
                this.saveQueue(queue);
                this.displayPendingCount();
                this.displayPendingList();
                
                this.showAlert(`Successfully synced ${result.synced_count} attendance records!`, 'success');
            } else {
                this.showAlert('Sync failed: ' + (result.error || 'Unknown error'), 'danger');
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.showAlert('Sync failed. Please try again.', 'danger');
        } finally {
            if (syncButton) {
                syncButton.disabled = false;
                this.displayPendingCount();
            }
        }
    }

    // Auto-sync when connection is restored
    async autoSync() {
        const queue = this.getQueue();
        const pending = queue.filter(item => !item.synced);
        
        if (pending.length > 0) {
            this.showAlert('Connection restored! Auto-syncing attendance...', 'info');
            await this.syncAll();
        }
    }

    // Show alert message
    showAlert(message, type = 'info') {
        const container = document.getElementById('alert-container');
        if (!container) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alert);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    // Clear synced records older than 7 days
    clearOldRecords() {
        const queue = this.getQueue();
        const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        
        const filtered = queue.filter(item => {
            if (item.synced && item.id < weekAgo) {
                return false; // Remove old synced items
            }
            return true;
        });

        this.saveQueue(filtered);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.offlineAttendance = new OfflineAttendance();
});
