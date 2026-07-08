document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    let debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() {
            applyFilters();
        }, 400);
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            applyFilters();
        }
    });
});

function applyFilters() {
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const vegFilter = document.getElementById('veg-filter');
    const availableFilter = document.getElementById('available-filter');

    const params = new URLSearchParams();

    if (searchInput && searchInput.value.trim()) {
        params.set('q', searchInput.value.trim());
    }
    if (categoryFilter && categoryFilter.value) {
        params.set('category', categoryFilter.value);
    }
    if (vegFilter && vegFilter.value) {
        params.set('veg', vegFilter.value);
    }
    if (availableFilter && availableFilter.value) {
        params.set('available', availableFilter.value);
    }

    const queryString = params.toString();
    const newUrl = window.location.pathname + (queryString ? '?' + queryString : '');
    window.location.href = newUrl;
}
