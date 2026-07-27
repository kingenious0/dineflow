/**
 * DineFlow Restaurant Management System — Core JavaScript Module
 */

document.addEventListener('DOMContentLoaded', function () {
    // ── Sidebar Toggle Functionality ──────────────────────────────────
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('mainWrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebarToggle && sidebar && mainWrapper) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
            } else {
                sidebar.classList.toggle('collapsed');
                mainWrapper.classList.toggle('sidebar-collapsed');
            }
        });
    }

    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.flash-container .alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Global Password Visibility Toggle Helper
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn ? btn.querySelector('i') : null;
    if (input) {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        if (icon) {
            if (icon.classList.contains('bi')) {
                icon.classList.toggle('bi-eye', !isPassword);
                icon.classList.toggle('bi-eye-slash', isPassword);
            } else {
                icon.classList.toggle('fa-eye', !isPassword);
                icon.classList.toggle('fa-eye-slash', isPassword);
            }
        }
    }
}
