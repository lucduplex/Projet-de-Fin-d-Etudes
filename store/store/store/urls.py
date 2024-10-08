from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from products import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Page d'accueil
    path('', views.index, name='index'),
    
    # Détail d'un produit
    path('product/<int:id>/', views.page_detail, name='page_detail'),
    
    # Pages supplémentaires
    path('about/', views.about, name='about'),
    path('base/', views.base, name='base'),

    # Liste des produits et résultats de recherche
    path('listProducts/', views.listProducts, name='listProducts'),
    path('search_results/', views.search_results, name='search_results'),

    # Panier et gestion des produits dans le panier
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_product_of_cart/<int:product_id>/', views.delete_product_of_cart, name='delete_product_of_cart'), 
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Inscription
    path('register/', views.register, name='register'),
    
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
]

# Configuration pour servir les fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
