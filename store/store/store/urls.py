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
    path('supprimer_product/<int:product_id>/', views.supprimer_product, name='supprimer_product'), 

    # Inscription
    path('register/', views.register, name='register'),
    
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
]

# Configuration pour servir les fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
