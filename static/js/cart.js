const CART_STORAGE_KEY = 'smart_restaurant_cart';

function getCart() {
    try {
        const cart = localStorage.getItem(CART_STORAGE_KEY);
        return cart ? JSON.parse(cart) : {};
    } catch (e) {
        return {};
    }
}

function saveCart(cart) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    syncCartToSession(cart);
    updateCartBadge();
}

function addToCart(item) {
    const cart = getCart();
    const itemId = String(item.id);

    if (cart[itemId]) {
        cart[itemId].quantity += 1;
    } else {
        cart[itemId] = {
            id: item.id,
            name: item.name,
            price: parseFloat(item.price),
            quantity: 1,
            image_url: item.image || item.image_url || '',
            is_vegetarian: item.is_vegetarian || false,
        };
    }

    saveCart(cart);
    showToast(`${item.name} added to cart`, 'success');
}

function removeItem(itemId) {
    const cart = getCart();
    delete cart[String(itemId)];
    saveCart(cart);
}

function increaseQuantity(itemId) {
    const cart = getCart();
    const id = String(itemId);
    if (cart[id]) {
        cart[id].quantity += 1;
        saveCart(cart);
    }
}

function decreaseQuantity(itemId) {
    const cart = getCart();
    const id = String(itemId);
    if (cart[id]) {
        cart[id].quantity -= 1;
        if (cart[id].quantity <= 0) {
            delete cart[id];
        }
        saveCart(cart);
    }
}

function clearCart() {
    localStorage.removeItem(CART_STORAGE_KEY);
    syncCartToSession({});
    updateCartBadge();
}

function calculateSubtotal(cart) {
    cart = cart || getCart();
    let subtotal = 0;
    Object.values(cart).forEach(function(item) {
        subtotal += parseFloat(item.price) * parseInt(item.quantity, 10);
    });
    return subtotal;
}

function calculateTax(subtotal) {
    const taxRate = window.APP_CONFIG ? window.APP_CONFIG.taxRate : 0.08;
    return subtotal * taxRate;
}

function calculateGrandTotal(cart) {
    const subtotal = calculateSubtotal(cart);
    const tax = calculateTax(subtotal);
    return subtotal + tax;
}

function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

function updateCartBadge(count) {
    const badge = document.getElementById('navbar-cart-count');
    if (!badge) return;

    if (count === undefined) {
        const cart = getCart();
        count = Object.values(cart).reduce(function(sum, item) {
            return sum + item.quantity;
        }, 0);
    }

    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline' : 'none';
}

function syncCartToSession(cart) {
    if (!window.APP_CONFIG || !window.APP_CONFIG.cartSyncUrl) return;

    fetch(window.APP_CONFIG.cartSyncUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.APP_CONFIG.csrfToken,
        },
        body: JSON.stringify({ cart: cart }),
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            updateCartBadge(data.cart_count);
        }
    })
    .catch(function() {
        // Session sync is best-effort; localStorage remains source of truth
    });
}

function loadCartFromSession() {
    if (!window.APP_CONFIG || !window.APP_CONFIG.cartSyncUrl) return;

    fetch(window.APP_CONFIG.cartSyncUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': window.APP_CONFIG.csrfToken,
        },
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success && data.cart) {
            const localCart = getCart();
            const localCount = Object.keys(localCart).length;
            const sessionCount = Object.keys(data.cart).length;

            if (sessionCount > 0 && localCount === 0) {
                localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(data.cart));
                updateCartBadge(data.cart_count);
            }
        }
    })
    .catch(function() {});
}

function renderCartPage() {
    const cart = getCart();
    const items = Object.values(cart);
    const container = document.getElementById('cart-items-list');
    const emptyState = document.getElementById('empty-cart');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (!container) return;

    if (items.length === 0) {
        container.innerHTML = '';
        if (emptyState) emptyState.classList.remove('d-none');
        if (checkoutBtn) checkoutBtn.classList.add('disabled');
        updateTotalsDisplay(0, 0, 0);
        return;
    }

    if (emptyState) emptyState.classList.add('d-none');
    if (checkoutBtn) checkoutBtn.classList.remove('disabled');

    let html = '';
    items.forEach(function(item) {
        const lineTotal = parseFloat(item.price) * item.quantity;
        const imgHtml = item.image_url
            ? `<img src="${item.image_url}" alt="${item.name}" class="cart-item-img">`
            : `<div class="cart-item-img d-flex align-items-center justify-content-center bg-light"><i class="bi bi-image text-muted"></i></div>`;

        html += `
            <div class="cart-item d-flex align-items-center gap-3" data-id="${item.id}">
                ${imgHtml}
                <div class="flex-grow-1">
                    <h6 class="mb-1">${item.name}</h6>
                    <span class="text-warning fw-semibold">${formatCurrency(item.price)}</span>
                </div>
                <div class="quantity-control">
                    <button class="btn btn-outline-secondary btn-sm qty-decrease" data-id="${item.id}">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span class="qty-value">${item.quantity}</span>
                    <button class="btn btn-outline-secondary btn-sm qty-increase" data-id="${item.id}">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>
                <div class="text-end" style="min-width: 70px;">
                    <strong>${formatCurrency(lineTotal)}</strong>
                </div>
                <button class="btn btn-outline-danger btn-sm remove-item" data-id="${item.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
    });

    container.innerHTML = html;

    container.querySelectorAll('.qty-increase').forEach(function(btn) {
        btn.addEventListener('click', function() {
            increaseQuantity(btn.dataset.id);
            renderCartPage();
        });
    });

    container.querySelectorAll('.qty-decrease').forEach(function(btn) {
        btn.addEventListener('click', function() {
            decreaseQuantity(btn.dataset.id);
            renderCartPage();
        });
    });

    container.querySelectorAll('.remove-item').forEach(function(btn) {
        btn.addEventListener('click', function() {
            removeItem(btn.dataset.id);
            renderCartPage();
            showToast('Item removed from cart', 'info');
        });
    });

    const subtotal = calculateSubtotal(cart);
    const tax = calculateTax(subtotal);
    const grandTotal = subtotal + tax;
    updateTotalsDisplay(subtotal, tax, grandTotal);
}

function updateTotalsDisplay(subtotal, tax, grandTotal) {
    const subtotalEl = document.getElementById('cart-subtotal');
    const taxEl = document.getElementById('cart-tax');
    const grandTotalEl = document.getElementById('cart-grand-total');

    if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
    if (taxEl) taxEl.textContent = formatCurrency(tax);
    if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grandTotal);
}

function showToast(message, type) {
    type = type || 'success';
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' :
                    type === 'danger' ? 'bg-danger' :
                    type === 'info' ? 'bg-info' : 'bg-warning';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    updateCartBadge();
    loadCartFromSession();

    document.querySelectorAll('.add-to-cart-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            addToCart({
                id: parseInt(btn.dataset.id, 10),
                name: btn.dataset.name,
                price: btn.dataset.price,
                image: btn.dataset.image,
                is_vegetarian: btn.dataset.vegetarian === 'true',
            });
        });
    });
});
