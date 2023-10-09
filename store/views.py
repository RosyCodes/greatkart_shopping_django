from django.shortcuts import render, get_object_or_404
from .models import Product
from carts.models import CartItem
from category.models import Category

# imports the private function
from carts.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
    context = {
        'products':products,
        'product_count': product_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        # take note of the category__slug (2 underscores) to compare product_slug and category slug with Category model
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        # take note of the cart__cart_id (2 underscores) to go to cart field of CartItem model, then use the foreign key cart_id of Cart class
        # uses the private function _cart_id(request) to compare it with the cart_id
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
  
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request,'store/product_detail.html',context)