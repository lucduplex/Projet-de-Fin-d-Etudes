from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart,CartItem
from django.conf import settings
import stripe
from django.contrib.auth import login
from .forms import UserRegisterForm
from .models import Category
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {username}!")

                # Mettre à jour la session 'cart_count' avec la quantité totale dans CartItem
                cart = Cart.objects.filter(user=user, is_active=True).first()
                if cart:
                    total_quantity = CartItem.objects.filter(cart=cart).aggregate(total_qty=Sum('quantity'))['total_qty']
                    request.session['cart_count'] = total_quantity if total_quantity else 0
                else:
                    request.session['cart_count'] = 0
                
                request.session.modified = True
                return redirect('index')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})



def user_logout(request):
    logout(request)
    request.session.flush()  # Vider la session lors de la déconnexion
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('login')  # Redirection vers la page de connexion après déconnexion

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Vérifier si l'utilisateur a déjà un panier actif
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)

    # Vérifier si le produit est déjà dans le panier
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1, 'price': product.price}  # Par défaut, quantité de 1 si nouvel article
    )

    if not item_created:
        # Si l'article existe déjà, incrémentez simplement la quantité
        cart_item.quantity += 1
        cart_item.save()

    # Mettre à jour la quantité totale dans le panier et l'enregistrer dans la session
    total_quantity = CartItem.objects.filter(cart=cart).aggregate(total_qty=Sum('quantity'))['total_qty']
    request.session['cart_count'] = total_quantity if total_quantity else 0
    request.session.modified = True

    # Rediriger vers une page (par exemple, vers la liste des produits ou la page du panier)
    return redirect('listProducts')  # Rediriger vers votre vue qui affiche le panier

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
    categories = Category.objects.all() 
    return render(request, 'page_detail.html', {'product': product, 'categories': categories})

# À propos
def about(request):
    categories = Category.objects.all()
    return render(request, 'about.html', {'categories': categories})

# Base
def base(request):
    return render(request, 'base.html')
    
   

# Liste des produits
def listProducts(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'listProducts.html', {'categories': categories, 'products': products})

# Résultats de recherche
def search_results(request):
    query = request.GET.get('query')
    categories = Category.objects.all()
    if query:
        products = Product.objects.filter(name__icontains=query)  # Assurez-vous d'utiliser le bon nom de champ
    else:
        products = Product.objects.all()
    return render(request, 'search_results.html', {'products': products, 'query': query, 'categories': categories})

def cart(request):
    # Initialisation des variables
    cart_items = []
    total_price = 0.0  
    stripe.api_key = settings.STRIPE_PUBLIC_KEY
    categories = Category.objects.all()

    # Si l'utilisateur est authentifié, on récupère son panier actif
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            # Récupère tous les items dans le panier de l'utilisateur connecté
            cart_items = CartItem.objects.filter(cart=cart)
            
            # Calcule le prix total du panier
            total_price = sum(item.product.price * item.quantity for item in cart_items)
    else:
        # Gestion du panier pour les utilisateurs non authentifiés via session
        cart_session = request.session.get('cart', {})
        product_ids = list(cart_session.keys())
        products = Product.objects.filter(id__in=product_ids)

        # Récupérer les articles du panier dans la session
        for product in products:
            quantity = cart_session[str(product.id)]
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity
            })

        # Calculer le prix total pour les produits dans la session
        total_price = sum(item['total_price'] for item in cart_items)

    # Préparation des données pour Stripe (prix en centimes)
    total_price_stripe = total_price * 100  

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_price_stripe': total_price_stripe,
        'key': settings.STRIPE_PUBLIC_KEY,
        'categories': categories
    })

@login_required
def delete_product_of_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Récupérer le panier actif de l'utilisateur
    cart = Cart.objects.filter(user=user, is_active=True).first()

    if cart:
        try:
            # Récupérer l'élément du panier correspondant au produit
            cart_item = CartItem.objects.get(cart=cart, product=product)

            # Si la quantité est supérieure à 1, la décrémenter
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # Si la quantité est 1 ou moins, supprimer l'élément du panier
                cart_item.delete()

            # Mettre à jour la quantité totale dans le panier
            total_quantity = CartItem.objects.filter(cart=cart).aggregate(total_qty=Sum('quantity'))['total_qty']
            request.session['cart_count'] = total_quantity if total_quantity else 0
            request.session.modified = True

            # Si le panier est vide, le désactiver
            if not CartItem.objects.filter(cart=cart).exists():
                cart.is_active = False
                cart.save()

        except CartItem.DoesNotExist:
            # Le produit n'existe pas dans le panier
            pass

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
    categories = Category.objects.all()
    products = Product.objects.filter(category=category)
    return render(request, 'products_by_category.html', {'category': category, 'products': products,'categories': categories})





   