from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, ProductCategory, Product
import random

class Command(BaseCommand):
    help = 'Crea datos iniciales para la aplicación'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales...')
        
        # Crear usuarios
        self.create_users()
        
        # Crear categorías
        categories = self.create_categories()
        
        # Crear productos
        self.create_products(categories)
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales creados con éxito'))
    
    def create_users(self):
        # Crear usuario administrador si no existe
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            UserProfile.objects.create(user=admin, role='admin')
            self.stdout.write(f'Usuario administrador creado: {admin.username}')
        
        # Crear usuario vendedor si no existe
        if not User.objects.filter(username='vendedor').exists():
            seller = User.objects.create_user(
                username='vendedor',
                email='vendedor@example.com',
                password='vendedor123'
            )
            UserProfile.objects.create(user=seller, role='seller')
            self.stdout.write(f'Usuario vendedor creado: {seller.username}')
    
    def create_categories(self):
        categories = [
            {'name': 'Electrónica', 'description': 'Productos electrónicos y gadgets'},
            {'name': 'Ropa', 'description': 'Vestimenta y accesorios'},
            {'name': 'Alimentos', 'description': 'Productos alimenticios'},
            {'name': 'Hogar', 'description': 'Artículos para el hogar'},
            {'name': 'Juguetes', 'description': 'Juguetes y juegos'}
        ]
        
        created_categories = []
        
        for category_data in categories:
            category, created = ProductCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            created_categories.append(category)
            
            if created:
                self.stdout.write(f'Categoría creada: {category.name}')
            else:
                self.stdout.write(f'Categoría ya existente: {category.name}')
        
        return created_categories
    
    def create_products(self, categories):
        # Lista de productos de ejemplo para cada categoría
        products_by_category = {
            'Electrónica': [
                {'name': 'Smartphone X23', 'price': 299.99, 'cost_price': 199.99, 'stock': 20, 'barcode': 'ELEC001'},
                {'name': 'Auriculares Bluetooth', 'price': 49.99, 'cost_price': 25.00, 'stock': 30, 'barcode': 'ELEC002'},
                {'name': 'Tablet 10"', 'price': 199.99, 'cost_price': 120.00, 'stock': 15, 'barcode': 'ELEC003'},
                {'name': 'Cargador USB-C', 'price': 19.99, 'cost_price': 5.00, 'stock': 50, 'barcode': 'ELEC004'},
            ],
            'Ropa': [
                {'name': 'Camiseta Básica', 'price': 15.99, 'cost_price': 5.00, 'stock': 100, 'barcode': 'ROPA001'},
                {'name': 'Jeans Clásicos', 'price': 39.99, 'cost_price': 15.00, 'stock': 50, 'barcode': 'ROPA002'},
                {'name': 'Zapatillas Deportivas', 'price': 59.99, 'cost_price': 25.00, 'stock': 40, 'barcode': 'ROPA003'},
            ],
            'Alimentos': [
                {'name': 'Chocolate Premium', 'price': 5.99, 'cost_price': 2.00, 'stock': 200, 'barcode': 'ALIM001'},
                {'name': 'Café Gourmet', 'price': 8.99, 'cost_price': 3.50, 'stock': 100, 'barcode': 'ALIM002'},
                {'name': 'Aceite de Oliva', 'price': 12.99, 'cost_price': 6.00, 'stock': 80, 'barcode': 'ALIM003'},
            ],
            'Hogar': [
                {'name': 'Juego de Sábanas', 'price': 29.99, 'cost_price': 12.00, 'stock': 30, 'barcode': 'HOGAR001'},
                {'name': 'Lámpara LED', 'price': 24.99, 'cost_price': 10.00, 'stock': 25, 'barcode': 'HOGAR002'},
                {'name': 'Set de Cocina', 'price': 49.99, 'cost_price': 20.00, 'stock': 15, 'barcode': 'HOGAR003'},
            ],
            'Juguetes': [
                {'name': 'Peluche Oso', 'price': 14.99, 'cost_price': 4.00, 'stock': 40, 'barcode': 'JUG001'},
                {'name': 'Juego de Mesa', 'price': 19.99, 'cost_price': 8.00, 'stock': 25, 'barcode': 'JUG002'},
                {'name': 'Rompecabezas 1000 piezas', 'price': 24.99, 'cost_price': 10.00, 'stock': 20, 'barcode': 'JUG003'},
            ]
        }
        
        products_created = 0
        
        for category in categories:
            if category.name in products_by_category:
                products_data = products_by_category[category.name]
                
                for product_data in products_data:
                    product, created = Product.objects.get_or_create(
                        name=product_data['name'],
                        defaults={
                            'price': product_data['price'],
                            'cost_price': product_data['cost_price'],
                            'stock': product_data['stock'],
                            'barcode': product_data['barcode'],
                            'category': category,
                            'description': f'Descripción para {product_data["name"]}'
                        }
                    )
                    
                    if created:
                        products_created += 1
        
        self.stdout.write(f'{products_created} productos creados')
