from django.urls import path

from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('menu/', views.MenuListView.as_view(), name='menu'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('place-order/', views.PlaceOrderView.as_view(), name='place_order'),
    path(
        'order/success/<int:order_id>/',
        views.OrderSuccessView.as_view(),
        name='order_success'
    ),
    path(
        'order/track/',
        views.OrderTrackLookupView.as_view(),
        name='order_track_lookup'
    ),
    path(
        'order/track/<int:order_id>/',
        views.OrderTrackingView.as_view(),
        name='order_tracking'
    ),
    path(
        'api/order/<int:order_id>/status/',
        views.OrderStatusAPIView.as_view(),
        name='order_status_api'
    ),
    path('api/cart/sync/', views.CartSyncView.as_view(), name='cart_sync'),
    path('kitchen/', views.KitchenDashboardView.as_view(), name='kitchen_dashboard'),
    path(
        'kitchen/order/<int:order_id>/update/',
        views.UpdateOrderStatusView.as_view(),
        name='update_order_status'
    ),
]
