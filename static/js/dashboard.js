/**
 * Dashboard JavaScript
 * Common functionality for the crypto dashboard
 */

// Global variables
let refreshInterval;
const REFRESH_INTERVAL = 300000; // 5 minutes

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
});

function initializeDashboard() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function setupEventListeners() {
    // Handle responsive table scrolling
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        table.addEventListener('scroll', function() {
            if (this.scrollLeft > 0) {
                this.classList.add('scrolled');
            } else {
                this.classList.remove('scrolled');
            }
        });
    });
    
    // Handle card hover effects
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Handle button loading states
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.dataset.loading !== 'false') {
                showButtonLoading(this);
            }
        });
    });
}

function startAutoRefresh() {
    // Auto-refresh data every 5 minutes
    refreshInterval = setInterval(() => {
        refreshDashboardData();
    }, REFRESH_INTERVAL);
    
    // Show refresh indicator
    showRefreshIndicator();
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function refreshDashboardData() {
    console.log('Auto-refreshing dashboard data...');
    
    // Refresh summary data
    if (typeof updateSummaryCards === 'function') {
        updateSummaryCards();
    }
    
    // Refresh market cap data if on market cap page
    if (typeof loadMarketCapData === 'function') {
        loadMarketCapData();
    }
    
    // Refresh performance data if on performance page
    if (typeof loadPerformanceData === 'function') {
        loadPerformanceData();
    }
    
    showRefreshIndicator();
}

function showRefreshIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'alert alert-info alert-dismissible fade show position-fixed';
    indicator.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    indicator.innerHTML = `
        <i class="fas fa-sync-alt fa-spin me-2"></i>
        Data refreshed automatically
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(indicator);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.remove();
        }
    }, 3000);
}

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    const originalDisabled = button.disabled;
    
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
    
    // Store original state
    button.dataset.originalText = originalText;
    button.dataset.originalDisabled = originalDisabled;
    
    // Auto-restore after 5 seconds if not manually restored
    setTimeout(() => {
        if (button.innerHTML.includes('Loading...')) {
            hideButtonLoading(button);
        }
    }, 5000);
}

function hideButtonLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = button.dataset.originalDisabled === 'true';
        
        delete button.dataset.originalText;
        delete button.dataset.originalDisabled;
    }
}

// Utility functions
function formatCurrency(amount, decimals = 2) {
    if (amount >= 1e12) {
        return '$' + (amount / 1e12).toFixed(decimals) + 'T';
    } else if (amount >= 1e9) {
        return '$' + (amount / 1e9).toFixed(decimals) + 'B';
    } else if (amount >= 1e6) {
        return '$' + (amount / 1e6).toFixed(decimals) + 'M';
    } else if (amount >= 1e3) {
        return '$' + (amount / 1e3).toFixed(decimals) + 'K';
    } else {
        return '$' + amount.toFixed(decimals);
    }
}

function formatNumber(number, decimals = 2) {
    if (number >= 1e9) {
        return (number / 1e9).toFixed(decimals) + 'B';
    } else if (number >= 1e6) {
        return (number / 1e6).toFixed(decimals) + 'M';
    } else if (number >= 1e3) {
        return (number / 1e3).toFixed(decimals) + 'K';
    } else {
        return number.toFixed(decimals);
    }
}

function formatPercentage(value, decimals = 2) {
    const formatted = value.toFixed(decimals);
    return value > 0 ? `+${formatted}%` : `${formatted}%`;
}

function getPerformanceClass(value) {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return 'neutral';
}

function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

function showError(message, title = 'Error') {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${title}
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove from DOM after hiding
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

function showConfirm(message, title = 'Confirm', callback = null) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-question-circle me-2"></i>
                        ${title}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="confirm-btn">Confirm</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Handle confirm button
    const confirmBtn = modal.querySelector('#confirm-btn');
    confirmBtn.addEventListener('click', () => {
        if (callback) callback();
        bsModal.hide();
    });
    
    // Remove from DOM after hiding
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API request failed:', error);
            showToast(`API request failed: ${error.message}`, 'danger');
            throw error;
        });
}

// Chart helper functions
function getChartColors(count) {
    const colors = [
        '#007bff', '#28a745', '#dc3545', '#ffc107', '#6f42c1',
        '#fd7e14', '#20c997', '#6c757d', '#e83e8c', '#17a2b8'
    ];
    
    return colors.slice(0, count);
}

function createChartGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color + '40'); // 25% opacity
    gradient.addColorStop(1, color + '00'); // 0% opacity
    return gradient;
}

// Export functions for global use
window.dashboardUtils = {
    formatCurrency,
    formatNumber,
    formatPercentage,
    getPerformanceClass,
    showToast,
    showError,
    showConfirm,
    apiRequest,
    getChartColors,
    createChartGradient,
    showButtonLoading,
    hideButtonLoading,
    refreshDashboardData,
    startAutoRefresh,
    stopAutoRefresh
};

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        refreshDashboardData();
    }
});

// Handle online/offline status
window.addEventListener('online', function() {
    showToast('Connection restored', 'success');
    refreshDashboardData();
});

window.addEventListener('offline', function() {
    showToast('Connection lost - data may be outdated', 'warning');
    stopAutoRefresh();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + R: Refresh data
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshDashboardData();
        showToast('Data refreshed manually', 'info');
    }
    
    // Escape: Close modals and dropdowns
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
        
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.previousElementSibling);
            if (bsDropdown) bsDropdown.hide();
        });
    }
});

console.log('Dashboard JavaScript loaded successfully');