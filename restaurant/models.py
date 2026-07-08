from decimal import Decimal

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50,
        default='bi-egg-fried',
        help_text='Bootstrap icon class, e.g. bi-egg-fried'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default=''
    )

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('restaurant:menu')


class Order(models.Model):
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY = 'READY'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_READY, 'Ready'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    table_number = models.CharField(max_length=10, blank=True, default='')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RECEIVED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} - {self.customer_name}'

    def get_absolute_url(self):
        return reverse('restaurant:order_tracking', kwargs={'order_id': self.pk})

    @property
    def status_badge_class(self):
        badge_map = {
            self.STATUS_RECEIVED: 'bg-primary',
            self.STATUS_PREPARING: 'bg-warning text-dark',
            self.STATUS_READY: 'bg-success',
            self.STATUS_COMPLETED: 'bg-secondary',
        }
        return badge_map.get(self.status, 'bg-secondary')

    @property
    def status_index(self):
        status_order = [
            self.STATUS_RECEIVED,
            self.STATUS_PREPARING,
            self.STATUS_READY,
            self.STATUS_COMPLETED,
        ]
        return status_order.index(self.status)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity}x {self.menu_item.name}'

    @property
    def line_total(self):
        return self.price_at_order * self.quantity
