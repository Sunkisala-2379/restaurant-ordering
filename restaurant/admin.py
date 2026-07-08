from django.contrib import admin

from .models import Category, MenuItem, Order, OrderItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('name', 'price', 'is_vegetarian', 'is_spicy', 'is_available', 'image_url')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'item_count')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [MenuItemInline]

    @admin.display(description='Menu Items')
    def item_count(self, obj):
        return obj.menu_items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'is_vegetarian',
        'is_spicy', 'is_available'
    )
    list_filter = ('category', 'is_vegetarian', 'is_spicy', 'is_available')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    list_editable = ('is_available', 'price')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price_at_order', 'line_total_display')
    can_delete = False

    @admin.display(description='Line Total')
    def line_total_display(self, obj):
        if obj.pk:
            return f'${obj.line_total:.2f}'
        return '-'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone', 'table_number',
        'total_amount', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'total_amount')
    inlines = [OrderItemInline]
    list_editable = ('status',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price_at_order')
    list_filter = ('order__status',)
    search_fields = ('order__customer_name', 'menu_item__name')
    ordering = ('-order__created_at',)
