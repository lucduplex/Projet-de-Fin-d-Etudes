from django.shortcuts import render
from .models import Product

def index(request):
    if 'cart_count' not in request.session:
        request.session['cart_count'] = 0
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

