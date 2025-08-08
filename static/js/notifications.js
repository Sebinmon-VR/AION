// Notification System JavaScript
class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.checkInterval = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.startPeriodicCheck();
        this.bindEvents();
    }

    createContainer() {
        // Create notification container
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        this.container.id = 'notification-container';
        document.body.appendChild(this.container);
    }

    async fetchNotifications() {
        try {
            console.log('Fetching notifications...');
            const response = await fetch('/api/notifications');
            console.log('Response status:', response.status);
            if (response.ok) {
                const data = await response.json();
                console.log('Notifications data:', data);
                return data.notifications || [];
            } else {
                console.error('Failed to fetch notifications, status:', response.status);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
        return [];
    }

    async markAsRead(notificationId) {
        try {
            await fetch(`/api/notifications/${notificationId}/mark_read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    createNotificationElement(notification) {
        const notificationEl = document.createElement('div');
        notificationEl.className = `notification-popup ${notification.priority === 'high' ? 'high-priority' : ''}`;
        notificationEl.setAttribute('data-notification-id', notification.id);

        const timeAgo = this.formatTimeAgo(notification.timestamp);
        const candidateName = notification.candidate_name || 'Unknown';
        const position = notification.position || 'Unknown Position';

        notificationEl.innerHTML = `
            <div class="notification-header">
                <h4 class="notification-title">
                    ${notification.type === 'candidate_shortlisted' ? '🎯' : '⭐'} 
                    ${notification.type === 'candidate_shortlisted' ? 'Candidate Shortlisted' : 'Candidate Selected'}
                </h4>
                <button class="notification-close" onclick="notificationSystem.dismissNotification(${notification.id})">&times;</button>
            </div>
            <div class="notification-message">
                ${notification.message}
            </div>
            <div class="notification-actions">
                <a href="/candidate/${notification.candidate_id}" class="notification-action-btn primary">
                    View Candidate
                </a>
                <button class="notification-action-btn" onclick="notificationSystem.dismissNotification(${notification.id})">
                    Dismiss
                </button>
            </div>
            <div class="notification-meta">
                <span><strong>${candidateName}</strong> - ${position}</span>
                <span>${timeAgo}</span>
            </div>
        `;

        return notificationEl;
    }

    showNotification(notification) {
        // Check if notification already exists
        const existingNotification = document.querySelector(`[data-notification-id="${notification.id}"]`);
        if (existingNotification) {
            return;
        }

        const notificationEl = this.createNotificationElement(notification);
        this.container.appendChild(notificationEl);

        // Play notification sound (optional)
        this.playNotificationSound();

        // Auto-dismiss after 15 seconds for non-critical notifications
        if (notification.priority !== 'high') {
            setTimeout(() => {
                this.dismissNotification(notification.id);
            }, 15000);
        }

        // Add to internal notifications array
        this.notifications.push(notification);
    }

    async dismissNotification(notificationId) {
        const notificationEl = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationEl) {
            notificationEl.classList.add('fade-out');
            setTimeout(() => {
                if (notificationEl.parentNode) {
                    notificationEl.parentNode.removeChild(notificationEl);
                }
            }, 500);

            // Mark as read in backend
            await this.markAsRead(notificationId);

            // Remove from internal array
            this.notifications = this.notifications.filter(n => n.id !== notificationId);
        }
    }

    async checkForNewNotifications() {
        console.log('Checking for new notifications...');
        const newNotifications = await this.fetchNotifications();
        console.log('Fetched notifications:', newNotifications);
        
        for (const notification of newNotifications) {
            // Only show if we haven't seen this notification before
            const exists = this.notifications.some(n => n.id === notification.id);
            console.log(`Notification ${notification.id} exists:`, exists);
            if (!exists) {
                console.log('Showing new notification:', notification);
                this.showNotification(notification);
            }
        }
    }

    startPeriodicCheck() {
        // Check for new notifications every 10 seconds
        this.checkInterval = setInterval(() => {
            this.checkForNewNotifications();
        }, 10000);

        // Initial check
        this.checkForNewNotifications();
    }

    stopPeriodicCheck() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }

    playNotificationSound() {
        // Create and play a subtle notification sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            // Fallback: no sound if audio context fails
            console.log('Notification sound not available');
        }
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const notificationTime = new Date(timestamp);
        const diffInSeconds = Math.floor((now - notificationTime) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours === 1 ? '' : 's'} ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days === 1 ? '' : 's'} ago`;
        }
    }

    bindEvents() {
        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            this.stopPeriodicCheck();
        });

        // Handle visibility change (pause when tab is not active)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopPeriodicCheck();
            } else {
                this.startPeriodicCheck();
            }
        });
    }

    // Public method to manually trigger notification check
    refresh() {
        this.checkForNewNotifications();
    }

    // Get current notification count
    getNotificationCount() {
        return this.notifications.length;
    }

    // Clear all notifications
    clearAll() {
        this.notifications.forEach(notification => {
            this.dismissNotification(notification.id);
        });
    }
}

// Initialize notification system when DOM is ready
let notificationSystem;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing notification system...');
    // Only initialize if user is logged in (has role cookie)
    const userRole = getCookie('role');
    console.log('User role:', userRole);
    if (userRole) {
        console.log('Initializing notification system for role:', userRole);
        notificationSystem = new NotificationSystem();
        console.log('Notification system initialized');
    } else {
        console.log('No user role found, skipping notification system');
    }
});

// Utility function to get cookie value
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Make notification system available globally
window.notificationSystem = notificationSystem;
