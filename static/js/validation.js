// static/js/validation.js
// Advanced Form Validation

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required]');

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#ff0066';
            
            // Create error message
            let error = input.nextElementSibling;
            if (!error || !error.classList.contains('error-msg')) {
                error = document.createElement('div');
                error.className = 'error-msg';
                error.style.color = '#ff0066';
                error.style.fontSize = '0.9rem';
                input.parentNode.insertBefore(error, input.nextSibling);
            }
            error.textContent = `${input.placeholder || 'This field'} is required`;
        } else {
            input.style.borderColor = '#00f5ff';
            const error = input.nextElementSibling;
            if (error && error.classList.contains('error-msg')) error.remove();
        }
    });

    return isValid;
}

// Email Validation
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Attach validation to all forms
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showToast('Please fill all required fields correctly!', 'error');
            }
        });
    });
});

// Global access
window.validateForm = validateForm;
window.isValidEmail = isValidEmail;