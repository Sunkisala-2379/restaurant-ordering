document.addEventListener('DOMContentLoaded', function() {
    const timeline = document.getElementById('order-timeline');
    if (!timeline) return;

    const statusApiUrl = timeline.dataset.statusApi;
    const orderId = timeline.dataset.orderId;
    let currentStatus = timeline.dataset.currentStatus;
    let currentIndex = parseInt(timeline.dataset.currentIndex, 10);

    const REFRESH_INTERVAL = 5000;

    function updateTimeline(status, statusIndex, statusDisplay, badgeClass) {
        const badge = document.getElementById('order-status-badge');
        if (badge) {
            badge.textContent = statusDisplay;
            badge.className = 'badge fs-6 px-3 py-2 ' + badgeClass;
        }

        const steps = timeline.querySelectorAll('.timeline-step');
        const connectors = timeline.querySelectorAll('.timeline-connector');

        steps.forEach(function(step, index) {
            const content = step.querySelector('.timeline-content small');
            if (index <= statusIndex) {
                step.classList.add('active');
                if (index < statusIndex) {
                    content.textContent = 'Completed';
                    content.className = 'text-success';
                } else {
                    content.textContent = 'Current';
                    content.className = 'text-warning';
                }
            } else {
                step.classList.remove('active');
                content.textContent = 'Pending';
                content.className = 'text-muted';
            }
        });

        connectors.forEach(function(connector, index) {
            if (index < statusIndex) {
                connector.classList.add('active');
            } else {
                connector.classList.remove('active');
            }
        });

        currentStatus = status;
        currentIndex = statusIndex;
    }

    function fetchOrderStatus() {
        fetch(statusApiUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(function(response) {
            if (!response.ok) throw new Error('Failed to fetch status');
            return response.json();
        })
        .then(function(data) {
            if (data.status !== currentStatus) {
                const previousIndex = currentIndex;
                updateTimeline(
                    data.status,
                    data.status_index,
                    data.status_display,
                    data.badge_class
                );

                if (data.status === 'COMPLETED') {
                    showToast('Your order is complete! Enjoy your meal.', 'success');
                } else if (data.status_index > previousIndex) {
                    showToast('Order status updated: ' + data.status_display, 'info');
                }
            }
        })
        .catch(function() {
            // Silently retry on next interval
        });
    }

    const refreshTimer = setInterval(fetchOrderStatus, REFRESH_INTERVAL);

    window.addEventListener('beforeunload', function() {
        clearInterval(refreshTimer);
    });
});
