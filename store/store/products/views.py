from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart
from django.conf import settings
import stripe
from django.contrib.auth import login
from .forms import UserRegisterForm
from .models import Category
from django.http import JsonResponse

# Ajouter un produit au panier
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    # Si le produit est déjà dans le panier, on incrémente la quantité
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    # Mettre à jour la session
    request.session['cart'] = cart

    # Mettre à jour le compteur du panier
    request.session['cart_count'] = sum(cart.values())
    request.session.modified = True

    return redirect('listProducts')

# Page d'accueil avec liste des produits
def index(request):
    if 'cart_count' not in request.session:
        request.session['cart_count'] = 0
    products = Product.objects.all()
    categories = Category.objects.all() 
    return render(request, 'index.html', {'products': products, 'categories': categories})

# Page de détail d'un produit
def page_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'page_detail.html', {'product': product})

# À propos
def about(request):
    return render(request, 'about.html')

# Base
def base(request):
    return render(request, 'base.html')

# Liste des produits
def listProducts(request):
    products = Product.objects.all()
    return render(request, 'listProducts.html', {'products': products})

# Résultats de recherche
def search_results(request):
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)  # Assurez-vous d'utiliser le bon nom de champ
    else:
        products = Product.objects.all()
    return render(request, 'search_results.html', {'products': products, 'query': query})

# Panier d'achats
def cart(request):
    products = []
    quantite = {}
    total_price = 0.0
    stripe.api_key = settings.STRIPE_PUBLIC_KEY

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            products = cart.products.all()
            quantite = {str(product.id): 1 for product in products}
            total_price = sum(float(product.price) * quantite[str(product.id)] for product in products)
    else:
        cart = request.session.get('cart', {})
        product_ids = list(map(int, cart.keys()))
        products = Product.objects.filter(id__in=product_ids)  # Correction ici : utiliser Product au lieu de Cart

        quantite = {str(product.id): int(cart.get(str(product.id), 0)) for product in products}
        total_price = sum(float(product.price) * quantite[str(product.id)] for product in products)
        
    total_price_stripe = total_price * 100  # Conversion pour Stripe

    prixTotalParProduct = []
    for product in products:
        product.quantite = quantite[str(product.id)]
        product.prix_total = product.price * product.quantite
        prixTotalParProduct.append(product)

    return render(request, 'cart.html', {
        'products': prixTotalParProduct,
        'total_price': total_price,
        'total_price_stripe': total_price_stripe,
        'key': settings.STRIPE_PUBLIC_KEY
    })

# Suppression d'un produit du panier
def supprimer_product(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
        else:
            del cart[product_id_str]
        
        # Mettre à jour le compteur du panier
        request.session['cart_count'] = sum(cart.values())
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('cart')

# Inscription de l'utilisateur
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'products_by_category.html', {'category': category, 'products': products})
