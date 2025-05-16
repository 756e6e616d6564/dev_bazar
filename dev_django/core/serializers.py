from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, ProductCategory, Product, Sale, SaleItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'role')

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'stock', 'category', 
                 'category_name', 'image', 'barcode', 'cost_price', 'profit_margin')
    
    def get_profit_margin(self, obj):
        return obj.profit_margin()

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = SaleItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    seller_name = serializers.ReadOnlyField(source='seller.username')
    
    class Meta:
        model = Sale
        fields = ('id', 'seller', 'seller_name', 'total_amount', 'created_at', 'items')
