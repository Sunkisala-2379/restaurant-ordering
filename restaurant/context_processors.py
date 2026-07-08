from django.conf import settings


def cart_context(request):
    """Expose cart item count from session to all templates."""
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    return {
        'cart_count': cart_count,
        'tax_rate': settings.TAX_RATE,
    }
