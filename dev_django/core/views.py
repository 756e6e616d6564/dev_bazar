from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, ProductCategory, Product, Sale, SaleItem
from .serializers import (UserSerializer, UserProfileSerializer, ProductCategorySerializer,
                         ProductSerializer, SaleSerializer, SaleItemSerializer)

import subprocess
import json

def landing_view(request):
    # Redireccionar a home si el usuario está autenticado
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def home_view(request):
    # Obtener productos con stock bajo
    low_stock_products = Product.objects.filter(stock__lt=5)
    
    # Obtener ventas recientes
    recent_sales = Sale.objects.all().order_by('-created_at')[:5]
    
    context = {
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales
    }
    
    return render(request, 'core/home.html', context)

@login_required
def sales_view(request):
    # Obtener todos los productos para mostrar en la interfaz
    products = Product.objects.all()
    
    # Obtener todas las categorías
    categories = ProductCategory.objects.all()
    
    context = {
        'products': products,
        'categories': categories
    }
    
    return render(request, 'core/sales.html', context)

@login_required
def products_view(request):
    # Obtener todos los productos
    products = Product.objects.all()
    
    # Obtener todas las categorías
    categories = ProductCategory.objects.all()
    
    context = {
        'products': products,
        'categories': categories
    }
    
    return render(request, 'core/products.html', context)

@login_required
def categories_view(request):
    # Obtener todas las categorías
    categories = ProductCategory.objects.all()
    
    context = {
        'categories': categories
    }
    
    return render(request, 'core/categories.html', context)

@login_required
def reports_view(request):
    # Obtener datos para el resumen
    total_sales = Sale.objects.aggregate(total=models.Sum('total_amount'))['total'] or 0
    num_sales = Sale.objects.count()
    average_sale = total_sales / num_sales if num_sales > 0 else 0
    
    # Datos para productos más vendidos
    top_products = []
    
    # Datos para ventas diarias
    from datetime import datetime, timedelta
    daily_sales = []
    
    # Ventas recientes
    recent_sales = Sale.objects.all().order_by('-created_at')[:10]
    
    context = {
        'summary': {
            'total_sales': total_sales,
            'num_sales': num_sales,
            'average_sale': average_sale,
            'items_sold': 0,
            'unique_products': 0,
            'estimated_profit': 0,
            'profit_margin': 0
        },
        'top_products': top_products,
        'daily_sales': daily_sales,
        'recent_sales': recent_sales
    }
    
    return render(request, 'core/reports.html', context)

@login_required
def sale_detail_view(request, sale_id):
    # Obtener la venta específica
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Calcular el total de items
    total_items = sum(item.quantity for item in sale.items.all())
    
    # Calcular costos y ganancias
    total_cost = sum(item.quantity * item.product.cost_price for item in sale.items.all())
    profit = sale.total_amount - total_cost
    profit_percentage = (profit / sale.total_amount * 100) if sale.total_amount > 0 else 0
    
    context = {
        'sale': sale,
        'total_items': total_items,
        'total_cost': total_cost,
        'profit': profit,
        'profit_percentage': profit_percentage
    }
    
    return render(request, 'core/sale_detail.html', context)

# API views para React
@login_required
@require_POST
def process_sale(request):
    try:
        # Obtener los datos del formulario
        total_amount = float(request.POST.get('total_amount', 0))
        product_ids = request.POST.getlist('item_product_id[]')
        quantities = request.POST.getlist('item_quantity[]')
        prices = request.POST.getlist('item_price[]')
        
        if not product_ids:
            return JsonResponse({'status': 'error', 'message': 'No hay productos en la venta'}, status=400)
        
        # Crear la venta
        sale = Sale.objects.create(seller=request.user, total_amount=total_amount)
        
        # Crear los items de la venta
        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = int(quantities[i])
            price = float(prices[i])
            
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                sale.delete()
                return JsonResponse({'status': 'error', 'message': f'Producto con ID {product_id} no existe'}, status=400)
            
            if quantity <= 0:
                sale.delete()
                return JsonResponse({'status': 'error', 'message': f'Cantidad inválida para producto {product.name}'}, status=400)
            
            if product.stock < quantity:
                sale.delete()
                return JsonResponse({'status': 'error', 'message': f'Stock insuficiente para {product.name}'}, status=400)
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price
            )
            
            # Actualizar stock
            product.stock -= quantity
            product.save()
        
        # Redirigir a la página de detalle de la venta
        return redirect('sale_detail', sale_id=sale.id)
    
    except Exception as e:
        # Si hay un error y la venta ya fue creada, eliminarla
        if 'sale' in locals():
            sale.delete()
        
        # Redirigir con mensaje de error
        from django.contrib import messages
        messages.error(request, f'Error al procesar la venta: {str(e)}')
        return redirect('sales')

@login_required
@require_POST
def save_product(request):
    try:
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        price = float(request.POST.get('price'))
        cost_price = float(request.POST.get('cost_price'))
        stock = int(request.POST.get('stock'))
        category_id = request.POST.get('category')
        barcode = request.POST.get('barcode')
        description = request.POST.get('description')
        
        category = None
        if category_id:
            try:
                category = ProductCategory.objects.get(pk=category_id)
            except ProductCategory.DoesNotExist:
                pass
        
        if product_id:
            # Actualizar producto existente
            product = get_object_or_404(Product, pk=product_id)
            product.name = name
            product.price = price
            product.cost_price = cost_price
            product.stock = stock
            product.category = category
            product.barcode = barcode
            product.description = description
            product.save()
        else:
            # Crear nuevo producto
            Product.objects.create(
                name=name,
                price=price,
                cost_price=cost_price,
                stock=stock,
                category=category,
                barcode=barcode,
                description=description
            )
        
        from django.contrib import messages
        messages.success(request, f'Producto {"actualizado" if product_id else "creado"} correctamente')
        
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error al guardar el producto: {str(e)}')
    
    return redirect('products')

@login_required
@require_POST
def delete_product(request):
    try:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        
        # Verificar si el producto tiene ventas asociadas
        if SaleItem.objects.filter(product=product).exists():
            from django.contrib import messages
            messages.warning(request, f'No se puede eliminar el producto "{product.name}" porque tiene ventas asociadas')
        else:
            product.delete()
            from django.contrib import messages
            messages.success(request, f'Producto "{product.name}" eliminado correctamente')
            
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error al eliminar el producto: {str(e)}')
    
    return redirect('products')

@login_required
@require_POST
def save_category(request):
    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if category_id:
            # Actualizar categoría existente
            category = get_object_or_404(ProductCategory, pk=category_id)
            category.name = name
            category.description = description
            category.save()
        else:
            # Crear nueva categoría
            ProductCategory.objects.create(
                name=name,
                description=description
            )
        
        from django.contrib import messages
        messages.success(request, f'Categoría {"actualizada" if category_id else "creada"} correctamente')
        
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error al guardar la categoría: {str(e)}')
    
    return redirect('categories')

@login_required
@require_POST
def delete_category(request):
    try:
        category_id = request.POST.get('category_id')
        category = get_object_or_404(ProductCategory, pk=category_id)
        
        # Al eliminar la categoría, los productos asociados quedarán sin categoría
        # pero no se eliminarán
        category.delete()
        
        from django.contrib import messages
        messages.success(request, f'Categoría "{category.name}" eliminada correctamente')
            
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    
    return redirect('categories')

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_sale(request):
    data = request.data
    total_amount = data.get('total_amount', 0)
    items = data.get('items', [])
    
    if not items:
        return Response({
            'status': 'error',
            'message': 'No hay productos en la venta'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Crear la venta
        sale = Sale.objects.create(seller=request.user, total_amount=total_amount)
        
        # Crear los items de la venta
        for item_data in items:
            product_id = item_data.get('product_id')
            if not product_id:
                raise ValueError("ID de producto faltante")
                
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise ValueError(f"Producto con ID {product_id} no existe")
                
            quantity = int(item_data.get('quantity', 1))
            if quantity <= 0:
                raise ValueError(f"Cantidad inválida para producto {product.name}")
                
            if product.stock < quantity:
                raise ValueError(f"Stock insuficiente para {product.name}")
                
            price = float(item_data.get('price', product.price))
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price
            )
            
            # Actualizar stock
            product.stock -= quantity
            product.save()
        
        return Response({
            'status': 'success',
            'sale_id': sale.id
        })
    except ValueError as e:
        # Si hay un error, eliminar la venta si ya fue creada
        if 'sale' in locals():
            sale.delete()
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Si hay un error, eliminar la venta si ya fue creada
        if 'sale' in locals():
            sale.delete()
        return Response({
            'status': 'error',
            'message': f"Error al procesar la venta: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def low_stock_products(request):
    """Retorna productos con stock bajo (menos de 5 unidades)"""
    threshold = int(request.query_params.get('threshold', 5))
    low_stock = Product.objects.filter(stock__lt=threshold)
    serializer = ProductSerializer(low_stock, many=True)
    return Response(serializer.data)

@csrf_exempt  # Evita verificación CSRF para permitir que GitHub envíe POSTs
def github_webhook(request):
    if request.method == 'POST':
        try:
            # Ruta a tu repo en el EC2
            repo_path = "/home/ec2-user/dev/dev_bazar"

            # Ejecuta git pull
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)

            # (Opcional) reiniciar Gunicorn o Supervisor
            # subprocess.run(["sudo", "systemctl", "restart", "gunicorn"], check=True)

            return HttpResponse("Actualizado", status=200)
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error en git pull: {e}", status=500)
    else:
        return HttpResponse("Método no permitido", status=405)
