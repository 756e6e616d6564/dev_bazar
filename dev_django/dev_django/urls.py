"""
URL configuration for dev_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from core.views import (landing_view, login_view, home_view, sales_view, products_view, 
                       categories_view, reports_view, sale_detail_view, process_sale,
                       save_product, delete_product, save_category, delete_category,
                       github_webhook, low_stock_products, ProductCategoryViewSet, 
                       ProductViewSet, SaleViewSet, create_sale)

# Configuración del router para la API
router = DefaultRouter()
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'sales', SaleViewSet)

urlpatterns = [
    # Vistas principales de la aplicación
    path('', landing_view, name='landing'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', home_view, name='home'),
    path('sales/', sales_view, name='sales'),
    path('sales/<int:sale_id>/', sale_detail_view, name='sale_detail'),
    path('products/', products_view, name='products'),
    path('categories/', categories_view, name='categories'),
    path('reports/', reports_view, name='reports'),
    
    # Endpoints para procesar formularios
    path('process-sale/', process_sale, name='process_sale'),
    path('save-product/', save_product, name='save_product'),
    path('delete-product/', delete_product, name='delete_product'),
    path('save-category/', save_category, name='save_category'),
    path('delete-category/', delete_category, name='delete_category'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Webhook
    path('github-webhook/', github_webhook),
    
    # API endpoints (se mantienen para compatibilidad con scripts/apps externas)
    path('api/', include(router.urls)),
    path('api/low-stock/', low_stock_products, name='low_stock'),
    path('api/create-sale/', create_sale, name='api_create_sale'),
    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
