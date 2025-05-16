from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, ProductCategory, Product, Sale, SaleItem

class APITestCase(TestCase):
    def setUp(self):
        # Crear usuario administrador para pruebas
        self.admin_user = User.objects.create_user(
            username='admin_test', 
            password='admin123'
        )
        UserProfile.objects.create(user=self.admin_user, role='admin')
        
        # Crear usuario vendedor para pruebas
        self.seller_user = User.objects.create_user(
            username='seller_test', 
            password='seller123'
        )
        UserProfile.objects.create(user=self.seller_user, role='seller')
        
        # Crear categoría para pruebas
        self.category = ProductCategory.objects.create(
            name='Test Category',
            description='Category for testing'
        )
        
        # Crear producto para pruebas
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            cost_price=50.00,
            stock=10,
            category=self.category,
            barcode='TEST123'
        )
        
        # Configurar cliente API
        self.client = APIClient()
    
    def test_login_api(self):
        """Probar el endpoint de login"""
        url = reverse('api_login')
        
        # Intento de login fallido
        response = self.client.post(url, {
            'username': 'wrong_user',
            'password': 'wrong_pass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Login exitoso con admin
        response = self.client.post(url, {
            'username': 'admin_test',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['role'], 'admin')
    
    def test_product_api(self):
        """Probar CRUD de productos"""
        # Login primero
        self.client.force_authenticate(user=self.admin_user)
        
        # Listar productos
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo tenemos un producto
        
        # Crear producto
        new_product_data = {
            'name': 'New Test Product',
            'price': 200.00,
            'cost_price': 100.00,
            'stock': 5,
            'category': self.category.id
        }
        response = self.client.post(url, new_product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que ahora hay 2 productos
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        
        # Obtener detalle del producto
        product_id = response.data[1]['id']
        url = reverse('product-detail', args=[product_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Test Product')
        
        # Actualizar producto
        update_data = {'name': 'Updated Product Name'}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        response = self.client.get(url)
        self.assertEqual(response.data['name'], 'Updated Product Name')
        
        # Eliminar producto
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que se eliminó
        response = self.client.get(reverse('product-list'))
        self.assertEqual(len(response.data), 1)
    
    def test_create_sale(self):
        """Probar creación de venta"""
        # Login como vendedor
        self.client.force_authenticate(user=self.seller_user)
        
        # Datos de la venta
        sale_data = {
            'total_amount': 200.00,
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2,
                    'price': 100.00
                }
            ]
        }
        
        # Crear venta
        url = reverse('create_sale')
        response = self.client.post(url, sale_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verificar que el stock se actualizó
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2 = 8
        
        # Verificar que se creó la venta en la BD
        self.assertEqual(Sale.objects.count(), 1)
        sale = Sale.objects.first()
        self.assertEqual(sale.seller, self.seller_user)
        self.assertEqual(float(sale.total_amount), 200.00)
        
        # Verificar items de la venta
        self.assertEqual(SaleItem.objects.count(), 1)
        sale_item = SaleItem.objects.first()
        self.assertEqual(sale_item.sale, sale)
        self.assertEqual(sale_item.product, self.product)
        self.assertEqual(sale_item.quantity, 2)
