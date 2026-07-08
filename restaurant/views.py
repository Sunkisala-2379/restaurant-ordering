import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, ListView, TemplateView

from .forms import CheckoutForm
from .models import Category, MenuItem, Order, OrderItem


def get_cart_from_session(request):
    return request.session.get('cart', {})


def save_cart_to_session(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def calculate_cart_totals(cart):
    subtotal = Decimal('0.00')
    for item in cart.values():
        try:
            price = Decimal(str(item.get('price', 0)))
            quantity = int(item.get('quantity', 0))
            subtotal += price * quantity
        except (InvalidOperation, ValueError, TypeError):
            continue
    tax = (subtotal * Decimal(str(settings.TAX_RATE))).quantize(Decimal('0.01'))
    grand_total = subtotal + tax
    return {
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
    }


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_items'] = (
            MenuItem.objects.filter(is_available=True)
            .select_related('category')[:6]
        )
        context['categories'] = Category.objects.all()[:8]
        return context


class MenuListView(ListView):
    model = MenuItem
    template_name = 'menu.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        queryset = (
            MenuItem.objects.filter(is_available=True)
            .select_related('category')
        )
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('q', '').strip()
        veg_filter = self.request.GET.get('veg')
        available_filter = self.request.GET.get('available')

        if category_slug:
            queryset = queryset.filter(category__name__iexact=category_slug)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if veg_filter == 'true':
            queryset = queryset.filter(is_vegetarian=True)
        elif veg_filter == 'false':
            queryset = queryset.filter(is_vegetarian=False)

        if available_filter == 'true':
            queryset = queryset.filter(is_available=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['veg_filter'] = self.request.GET.get('veg', '')
        context['available_filter'] = self.request.GET.get('available', '')
        return context


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart_from_session(self.request)
        totals = calculate_cart_totals(cart)
        context.update(totals)
        context['tax_rate_percent'] = int(settings.TAX_RATE * 100)
        return context


class CheckoutView(TemplateView):
    template_name = 'checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart_from_session(self.request)
        if not cart:
            messages.warning(self.request, 'Your cart is empty. Add items before checkout.')
        totals = calculate_cart_totals(cart)
        context['form'] = CheckoutForm()
        context.update(totals)
        context['tax_rate_percent'] = int(settings.TAX_RATE * 100)
        return context


class PlaceOrderView(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        cart = get_cart_from_session(request)
        if not cart:
            messages.error(request, 'Cannot place order with an empty cart.')
            return redirect('restaurant:cart')

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            totals = calculate_cart_totals(cart)
            return render(request, 'checkout.html', {
                'form': form,
                'tax_rate_percent': int(settings.TAX_RATE * 100),
                **totals,
            })

        try:
            with transaction.atomic():
                totals = calculate_cart_totals(cart)
                order = form.save(commit=False)
                order.total_amount = totals['grand_total']
                order.status = Order.STATUS_RECEIVED
                order.save()

                menu_item_ids = [int(k) for k in cart.keys()]
                menu_items = {
                    item.id: item
                    for item in MenuItem.objects.filter(
                        id__in=menu_item_ids,
                        is_available=True
                    )
                }

                order_items = []
                for item_id_str, cart_item in cart.items():
                    item_id = int(item_id_str)
                    menu_item = menu_items.get(item_id)
                    if not menu_item:
                        raise ValueError(f'Menu item {item_id} is no longer available.')

                    quantity = int(cart_item.get('quantity', 1))
                    if quantity < 1:
                        continue

                    order_items.append(OrderItem(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        price_at_order=menu_item.price,
                    ))

                if not order_items:
                    raise ValueError('No valid items in cart.')

                OrderItem.objects.bulk_create(order_items)

        except (ValueError, InvalidOperation) as exc:
            messages.error(request, str(exc))
            return redirect('restaurant:checkout')

        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, f'Order #{order.pk} placed successfully!')
        return redirect('restaurant:order_success', order_id=order.pk)


class OrderSuccessView(DetailView):
    model = Order
    template_name = 'success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'


class OrderTrackingView(DetailView):
    model = Order
    template_name = 'tracking.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_steps'] = [
            {'key': Order.STATUS_RECEIVED, 'label': 'Received', 'icon': 'bi-inbox'},
            {'key': Order.STATUS_PREPARING, 'label': 'Preparing', 'icon': 'bi-fire'},
            {'key': Order.STATUS_READY, 'label': 'Ready', 'icon': 'bi-bell'},
            {'key': Order.STATUS_COMPLETED, 'label': 'Completed', 'icon': 'bi-check-circle'},
        ]
        return context


class OrderStatusAPIView(DetailView):
    model = Order
    pk_url_kwarg = 'order_id'

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        return JsonResponse({
            'order_id': order.pk,
            'status': order.status,
            'status_display': order.get_status_display(),
            'status_index': order.status_index,
            'badge_class': order.status_badge_class,
        })


class KitchenDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'kitchen_dashboard.html'
    context_object_name = 'orders'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return (
            Order.objects.exclude(status=Order.STATUS_COMPLETED)
            .prefetch_related('items__menu_item')
            .order_by('created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_orders'] = (
            Order.objects.filter(status=Order.STATUS_COMPLETED)
            .prefetch_related('items__menu_item')[:10]
        )
        context['status_choices'] = Order.STATUS_CHOICES
        return context


class UpdateOrderStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    @method_decorator(csrf_protect)
    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        new_status = request.POST.get('status', '').strip()

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'success': False, 'error': 'Invalid status.'},
                    status=400
                )
            messages.error(request, 'Invalid order status.')
            return redirect('restaurant:kitchen_dashboard')

        order.status = new_status
        order.save(update_fields=['status'])

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'order_id': order.pk,
                'status': order.status,
                'status_display': order.get_status_display(),
                'badge_class': order.status_badge_class,
            })

        messages.success(
            request,
            f'Order #{order.pk} updated to {order.get_status_display()}.'
        )
        return redirect('restaurant:kitchen_dashboard')


class CartSyncView(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'error': 'Invalid JSON.'},
                status=400
            )

        cart = data.get('cart', {})
        if not isinstance(cart, dict):
            return JsonResponse(
                {'success': False, 'error': 'Cart must be an object.'},
                status=400
            )

        validated_cart = {}
        for item_id, item_data in cart.items():
            try:
                menu_item = MenuItem.objects.get(
                    pk=int(item_id),
                    is_available=True
                )
            except (MenuItem.DoesNotExist, ValueError, TypeError):
                continue

            quantity = int(item_data.get('quantity', 1))
            if quantity < 1:
                continue

            validated_cart[str(menu_item.pk)] = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': str(menu_item.price),
                'quantity': quantity,
                'image_url': menu_item.image_url,
                'is_vegetarian': menu_item.is_vegetarian,
            }

        save_cart_to_session(request, validated_cart)
        totals = calculate_cart_totals(validated_cart)

        return JsonResponse({
            'success': True,
            'cart_count': sum(
                item['quantity'] for item in validated_cart.values()
            ),
            'subtotal': str(totals['subtotal']),
            'tax': str(totals['tax']),
            'grand_total': str(totals['grand_total']),
        })

    def get(self, request):
        cart = get_cart_from_session(request)
        totals = calculate_cart_totals(cart)
        return JsonResponse({
            'success': True,
            'cart': cart,
            'cart_count': sum(item.get('quantity', 0) for item in cart.values()),
            'subtotal': str(totals['subtotal']),
            'tax': str(totals['tax']),
            'grand_total': str(totals['grand_total']),
        })


class OrderTrackLookupView(TemplateView):
    template_name = 'tracking.html'

    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id', '').strip()
        if order_id:
            try:
                order = Order.objects.get(pk=int(order_id))
                return redirect('restaurant:order_tracking', order_id=order.pk)
            except (Order.DoesNotExist, ValueError):
                messages.error(request, f'Order #{order_id} not found.')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lookup_mode'] = True
        context['status_steps'] = [
            {'key': Order.STATUS_RECEIVED, 'label': 'Received', 'icon': 'bi-inbox'},
            {'key': Order.STATUS_PREPARING, 'label': 'Preparing', 'icon': 'bi-fire'},
            {'key': Order.STATUS_READY, 'label': 'Ready', 'icon': 'bi-bell'},
            {'key': Order.STATUS_COMPLETED, 'label': 'Completed', 'icon': 'bi-check-circle'},
        ]
        return context


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
