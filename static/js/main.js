// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 5000);
    });
});

// Confirm before marking attendance
document.querySelectorAll('form').forEach(function(form) {
    if (form.querySelector('button[type="submit"]')) {
        form.querySelector('button[type="submit"]').addEventListener('click', function(e) {
            if (form.action.includes('mark-attendance') && form.method === 'POST') {
                if (!confirm('Are you sure you want to save this attendance?')) {
                    e.preventDefault();
                }
            }
        });
    }
});