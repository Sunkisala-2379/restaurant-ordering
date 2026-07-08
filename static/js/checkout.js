document.addEventListener('DOMContentLoaded', function() {
    renderCheckoutSummary();
    syncCartToSession(getCart());

    const form = document.getElementById('checkout-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const cart = getCart();
        const items = Object.values(cart);

        if (items.length === 0) {
            showToast('Your cart is empty. Add items before placing an order.', 'danger');
            return;
        }

        const nameField = document.getElementById('id_customer_name');
        const phoneField = document.getElementById('id_customer_phone');

        let valid = true;

        if (!nameField.value.trim() || nameField.value.trim().length < 2) {
            nameField.classList.add('is-invalid');
            valid = false;
        } else {
            nameField.classList.remove('is-invalid');
        }

        const phoneDigits = phoneField.value.replace(/\D/g, '');
        if (phoneDigits.length < 10) {
            phoneField.classList.add('is-invalid');
            valid = false;
        } else {
            phoneField.classList.remove('is-invalid');
        }

        if (!valid) {
            showToast('Please fill in all required fields correctly.', 'danger');
            return;
        }

        showLoading(true);

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
                form.submit();
            } else {
                showLoading(false);
                showToast('Failed to sync cart. Please try again.', 'danger');
            }
        })
        .catch(function() {
            showLoading(false);
            showToast('Network error. Please try again.', 'danger');
        });
    });
});

function renderCheckoutSummary() {
    const cart = getCart();
    const items = Object.values(cart);
    const container = document.getElementById('checkout-items-list');

    if (!container) return;

    if (items.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No items in cart</p>';
        return;
    }

    let html = '';
    items.forEach(function(item) {
        const lineTotal = parseFloat(item.price) * item.quantity;
        html += `
            <div class="d-flex justify-content-between py-2 border-bottom">
                <span>${item.quantity}x ${item.name}</span>
                <strong>${formatCurrency(lineTotal)}</strong>
            </div>
        `;
    });

    container.innerHTML = html;

    const subtotal = calculateSubtotal(cart);
    const tax = calculateTax(subtotal);
    const grandTotal = subtotal + tax;

    const subtotalEl = document.getElementById('checkout-subtotal');
    const taxEl = document.getElementById('checkout-tax');
    const grandTotalEl = document.getElementById('checkout-grand-total');

    if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
    if (taxEl) taxEl.textContent = formatCurrency(tax);
    if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grandTotal);
}
