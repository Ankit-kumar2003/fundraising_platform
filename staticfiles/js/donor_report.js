/* Donor Report Page JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reportForm');
    const generateBtn = document.getElementById('generateBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const alertContainer = document.getElementById('alertContainer');
    
    // Enhanced form submission with animations
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add loading state to button
            generateBtn.classList.add('loading');
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            generateBtn.disabled = true;
            
            // Show progress container with animation
            progressContainer.style.display = 'block';
            setTimeout(() => {
                progressContainer.classList.add('show');
            }, 100);
            
            // Animate progress bar
            animateProgress();
            
            // Submit form data
            const formData = new FormData(form);
            
            fetch('/donor-reports/generate/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Report generated successfully!', data.message);
                    if (data.download_url) {
                        setTimeout(() => {
                            window.location.href = data.download_url;
                        }, 1000);
                    }
                    // Refresh the page to show new report in recent reports
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    showAlert('error', 'Error generating report', data.message || 'An error occurred while generating the report.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'Network Error', 'Failed to generate report. Please check your connection and try again.');
            })
            .finally(() => {
                // Reset button state
                setTimeout(() => {
                    generateBtn.classList.remove('loading');
                    generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Report';
                    generateBtn.disabled = false;
                    
                    // Hide progress container
                    progressContainer.classList.remove('show');
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                        progressFill.style.width = '0%';
                    }, 300);
                }, 1500);
            });
        });
    }
    
    // Enhanced progress animation
    function animateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            progressFill.style.width = progress + '%';
            
            // Update progress text based on progress
            if (progress < 30) {
                progressText.textContent = 'Collecting donor data...';
            } else if (progress < 60) {
                progressText.textContent = 'Processing donations...';
            } else if (progress < 90) {
                progressText.textContent = 'Generating report...';
            } else {
                progressText.textContent = 'Finalizing...';
            }
        }, 200);
    }
    
    // Enhanced alert system with animations
    function showAlert(type, title, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade-in" role="alert">
                <div class="alert-content">
                    <div class="alert-icon">
                        ${type === 'success' ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-exclamation-triangle"></i>'}
                    </div>
                    <div class="alert-text">
                        <strong>${title}</strong>
                        <p>${message}</p>
                    </div>
                </div>
                <button type="button" class="alert-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        alertContainer.innerHTML = alertHtml;
        
        // Auto-dismiss success alerts
        if (type === 'success') {
            setTimeout(() => {
                const alert = alertContainer.querySelector('.alert');
                if (alert) {
                    alert.classList.add('fade-out');
                    setTimeout(() => alert.remove(), 300);
                }
            }, 5000);
        }
    }
    
    // Make showAlert globally available
    window.showAlert = showAlert;
    
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn-primary, .quick-action-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to download buttons
    const downloadButtons = document.querySelectorAll('a[href*="download"]');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            this.style.pointerEvents = 'none';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.pointerEvents = 'auto';
            }, 3000);
        });
    });
    
    // Form validation enhancements
    if (form) {
        const formInputs = form.querySelectorAll('input, select');
        formInputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('focus', function() {
                this.parentElement.classList.remove('has-error');
            });
        });
    }
    
    function validateField(field) {
        const formGroup = field.parentElement;
        let isValid = true;
        
        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
        }
        
        if (field.type === 'date' && field.value) {
            const selectedDate = new Date(field.value);
            const today = new Date();
            
            if (field.name.includes('date_from') && selectedDate > today) {
                isValid = false;
            }
        }
        
        if (isValid) {
            formGroup.classList.remove('has-error');
            formGroup.classList.add('has-success');
        } else {
            formGroup.classList.remove('has-success');
            formGroup.classList.add('has-error');
        }
        
        return isValid;
    }
    
    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe cards for animation
    document.querySelectorAll('.glass-card').forEach(card => {
        observer.observe(card);
    });
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open alerts
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => alert.remove());
        }
        
        if (e.ctrlKey && e.key === 'Enter') {
            // Quick submit with Ctrl+Enter
            if (form && document.activeElement.closest('form') === form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });
    
    // Quick Actions functionality
    const refreshBtn = document.getElementById('refreshReports');
    const exportAllBtn = document.getElementById('exportAll');
    const quickGenerateBtn = document.getElementById('quickGenerate');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span class="btn-text">Refreshing...</span>';
            this.disabled = true;
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
    
    if (exportAllBtn) {
        exportAllBtn.addEventListener('click', function() {
            exportAllData();
        });
    }
    
    if (quickGenerateBtn) {
        quickGenerateBtn.addEventListener('click', function() {
            // Scroll to form and focus first field
            const reportForm = document.getElementById('reportForm');
            if (reportForm) {
                reportForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(() => {
                    const firstField = reportForm.querySelector('select, input');
                    if (firstField) firstField.focus();
                }, 500);
            }
        });
    }
    
    // Enhanced breadcrumb navigation
    const breadcrumbLinks = document.querySelectorAll('.breadcrumb-link');
    breadcrumbLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add loading state for navigation
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
            }
        });
    });
    
    // Add smooth transitions for quick actions
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Global function for export all data
function exportAllData() {
    const button = event.target.closest('.quick-action-btn');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span class="btn-text">Exporting...</span>';
    button.disabled = true;
    
    // Simulate export process
    setTimeout(() => {
        if (window.showAlert) {
            window.showAlert('success', 'Export Complete', 'All donor data has been exported successfully. The download should start automatically.');
        }
        button.innerHTML = originalText;
        button.disabled = false;
    }, 2000);
}

// Global function for retrying failed reports
function retryReport(reportId) {
    const button = event.target.closest('.btn-retry');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Retrying...';
    button.disabled = true;
    
    // Simulate retry process
    fetch(`/features/retry-report/${reportId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (window.showAlert) {
                window.showAlert('success', 'Report Retry Initiated', 'The report generation has been restarted. Please check back in a few minutes.');
            }
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            if (window.showAlert) {
                window.showAlert('error', 'Retry Failed', data.message || 'Failed to retry report generation.');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (window.showAlert) {
            window.showAlert('error', 'Network Error', 'Failed to retry report. Please check your connection and try again.');
        }
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Add CSS for ripple effect and animations
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    
    .fade-out {
        animation: fadeOut 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
    
    .animate-in {
        animation: slideInUp 0.6s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .has-error .form-control,
    .has-error select,
    .has-error textarea {
        border-color: var(--danger-500) !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
    
    .has-success .form-control,
    .has-success select,
    .has-success textarea {
        border-color: var(--success-500) !important;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
    }
`;
document.head.appendChild(style);