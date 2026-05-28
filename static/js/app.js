// static/js/app.js
// Main Application Script - Smart Student Management System

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c🚀 SmartSMS Loaded Successfully', 'color: #00f5ff; font-size: 16px; font-weight: bold');
    
    // Initialize all modules
    initCounters();
    initSidebarToggle();
    initToastSystem();
    initDarkMode();
});

// Counter Animation for Dashboard Stats
function initCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseFloat(counter.getAttribute('data-target'));
        let count = 0;
        const increment = target / 60; // Smooth animation
        
        const updateCounter = () => {
            count += increment;
            if (count < target) {
                counter.textContent = count.toFixed(1);
                setTimeout(updateCounter, 30);
            } else {
                counter.textContent = target;
            }
        };
        updateCounter();
    });
}

// Sidebar Toggle for Mobile
function initSidebarToggle() {
    const sidebar = document.querySelector('.glass-sidebar');
    if (!sidebar) return;
    
    // Create mobile toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = '☰';
    toggleBtn.className = 'sidebar-toggle';
    document.querySelector('.top-nav').prepend(toggleBtn);
    
    toggleBtn.addEventListener('click', () => {
        sidebar.style.transform = sidebar.style.transform === 'translateX(0%)' 
            ? 'translateX(-100%)' 
            : 'translateX(0%)';
    });
}

// Toast Notification System
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">✕</button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

function initToastSystem() {
    // Global toast function available
    window.showToast = showToast;
}

// Dark/Light Mode Toggle (Future Ready)
function initDarkMode() {
    // Currently dark mode only, but ready for toggle
    console.log('🌙 Dark Mode Active');
}