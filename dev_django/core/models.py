from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    USER_ROLES = (
        ('admin', 'Administrador'),
        ('seller', 'Vendedor'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='seller')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name

    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.price) * 100
        return 0

class Sale(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta #{self.id} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity
