// PlannerX Frontend JavaScript

// Store Firebase ID token
let idToken = localStorage.getItem('auth_token') || localStorage.getItem('idToken');

// Force dev mode token for development
if (!idToken || idToken.includes('test@example.com')) {
    idToken = 'dev_demo_user:demo@plannerx.local';
    localStorage.setItem('auth_token', idToken);
    localStorage.setItem('idToken', idToken);
}

// Set token on all API requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    if (!options.headers) {
        options.headers = {};
    }
    
    // Add Authorization header for API calls
    if (url.startsWith('/tasks') || url.startsWith('/events') || 
        url.startsWith('/contacts') || url.startsWith('/settings') || 
        url.startsWith('/dashboard')) {
        options.headers['Authorization'] = `Bearer ${idToken}`;
    }
    
    return originalFetch(url, options);
};

// Helper: Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Helper: Format date for input
function formatDateForInput(date) {
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Helper: Parse form data to JSON
function formDataToJSON(formData) {
    const obj = {};
    for (let [key, value] of formData.entries()) {
        obj[key] = value;
    }
    return obj;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('PlannerX initialized');
    
    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// Export for use in templates
window.PlannerX = {
    showNotification,
    formatDateForInput,
    formDataToJSON,
    setToken: (token) => {
        idToken = token;
        localStorage.setItem('idToken', token);
    },
    getToken: () => idToken
};
