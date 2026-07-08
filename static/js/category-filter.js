document.addEventListener('DOMContentLoaded', function() {
    const categoryFilter = document.getElementById('category-filter');
    const vegFilter = document.getElementById('veg-filter');
    const availableFilter = document.getElementById('available-filter');

    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    if (vegFilter) {
        vegFilter.addEventListener('change', applyFilters);
    }
    if (availableFilter) {
        availableFilter.addEventListener('change', applyFilters);
    }
});
