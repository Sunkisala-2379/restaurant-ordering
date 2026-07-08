from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import Category, MenuItem


class Command(BaseCommand):
    help = 'Seed the database with sample categories and menu items'

    def handle(self, *args, **options):
        categories_data = [
            {'name': 'Starters', 'icon': 'bi-egg-fried'},
            {'name': 'Main Course', 'icon': 'bi-cup-hot'},
            {'name': 'Breads', 'icon': 'bi-basket'},
            {'name': 'Desserts', 'icon': 'bi-cake2'},
            {'name': 'Beverages', 'icon': 'bi-cup-straw'},
        ]

        menu_items_data = {
            'Starters': [
                {
                    'name': 'Crispy Spring Rolls',
                    'description': 'Golden fried vegetable rolls served with sweet chili sauce.',
                    'price': Decimal('8.99'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400',
                },
                {
                    'name': 'Chicken Wings',
                    'description': 'Spicy buffalo wings with ranch dip and celery sticks.',
                    'price': Decimal('12.99'),
                    'is_vegetarian': False,
                    'is_spicy': True,
                    'image_url': 'https://images.unsplash.com/photo-1608039829572-78524f79c4c7?w=400',
                },
                {
                    'name': 'Garlic Bread',
                    'description': 'Toasted bread with garlic butter and herbs.',
                    'price': Decimal('6.49'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1619535850248-5a34a2a7c46e?w=400',
                },
            ],
            'Main Course': [
                {
                    'name': 'Grilled Salmon',
                    'description': 'Atlantic salmon with lemon butter sauce and seasonal vegetables.',
                    'price': Decimal('24.99'),
                    'is_vegetarian': False,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1467003909585-bf5a0e845d1a?w=400',
                },
                {
                    'name': 'Paneer Tikka Masala',
                    'description': 'Cottage cheese cubes in rich tomato cream gravy.',
                    'price': Decimal('16.99'),
                    'is_vegetarian': True,
                    'is_spicy': True,
                    'image_url': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
                },
                {
                    'name': 'Beef Burger',
                    'description': 'Juicy beef patty with cheddar, lettuce, and special sauce.',
                    'price': Decimal('15.99'),
                    'is_vegetarian': False,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400',
                },
                {
                    'name': 'Vegetable Pasta',
                    'description': 'Penne pasta with seasonal vegetables in marinara sauce.',
                    'price': Decimal('14.49'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400',
                },
            ],
            'Breads': [
                {
                    'name': 'Butter Naan',
                    'description': 'Soft leavened flatbread brushed with butter.',
                    'price': Decimal('3.99'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400',
                },
                {
                    'name': 'Garlic Naan',
                    'description': 'Naan topped with fresh garlic and coriander.',
                    'price': Decimal('4.49'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400',
                },
            ],
            'Desserts': [
                {
                    'name': 'Chocolate Lava Cake',
                    'description': 'Warm chocolate cake with molten center and vanilla ice cream.',
                    'price': Decimal('9.99'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400',
                },
                {
                    'name': 'Tiramisu',
                    'description': 'Classic Italian dessert with espresso-soaked ladyfingers.',
                    'price': Decimal('8.49'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400',
                },
            ],
            'Beverages': [
                {
                    'name': 'Fresh Lime Soda',
                    'description': 'Refreshing lime soda with mint and ice.',
                    'price': Decimal('4.99'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400',
                },
                {
                    'name': 'Iced Coffee',
                    'description': 'Cold brew coffee with milk and a touch of vanilla.',
                    'price': Decimal('5.49'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1517701603779-8fc327d65b46?w=400',
                },
                {
                    'name': 'Mango Smoothie',
                    'description': 'Blended fresh mango with yogurt and honey.',
                    'price': Decimal('6.99'),
                    'is_vegetarian': True,
                    'is_spicy': False,
                    'image_url': 'https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400',
                },
            ],
        }

        created_categories = 0
        created_items = 0

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            if created:
                created_categories += 1

            for item_data in menu_items_data.get(cat_data['name'], []):
                _, created = MenuItem.objects.get_or_create(
                    name=item_data['name'],
                    category=category,
                    defaults=item_data
                )
                if created:
                    created_items += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {created_categories} categories, '
            f'{created_items} menu items created.'
        ))
