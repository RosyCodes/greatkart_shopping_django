from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# a private function that gets the session key
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        # for any keyword (color, size, brand, author) in the filter criteria
        for item in request.POST:
            key = item
            value = request.POST[key]        
            try:
                # gets the product that matches the filter
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                # creates a list of products that meet the filter criteria
                product_variation.append(variation)
            except:
                pass
  
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # gets the cart using the card_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    # provides grouping according to variations otherwise update the quantity
    is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
    # adds multiple products to cart
    if is_cart_item_exists:
        # look for the cart of the same variation and update the number
        cart_item = CartItem.objects.filter(product=product,cart=cart)

        # checks for existing variations from the database 
        # checks for the  new / current variation
        # item id from the database

        # checks if the current variation is present in the existing variations, then update the quantity
        ex_var_list = []   # empty list of existing variations
        id = [] # empty cart ID list

        for item in cart_item:
            existing_variation = item.variations.all()
            # returns a query set, so type cast the queryset into a list
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        # print(ex_var_list)

        if product_variation in ex_var_list:
            # increase the cart item quantity

            # searches for the cart ID:
            idex = ex_var_list.index(product_variation)
            item_id=id[idex]
            item = CartItem.objects.get(product=product,id=item_id)
            item.quantity +=1
            item.save()
           
        else:
            # create a new cart item
            item = CartItem.objects.create(product=product, quantity=1,cart=cart)
            
            # checks if the product variation is empty or not and add this to the existing cart
            if len(product_variation)>0:
                # clear the highlighted filter for each item
                item.variations.clear()
                # the asterisk (*) means to add all the product variations
                item.variations.add(*product_variation)
                item.save()
    else: 
        cart_item = CartItem.objects.create(
            product = product, # this is the product created at the start of this function
            quantity = 1,
            cart = cart,
        )

        # checks if the product variation is empty or not to a new cart
        if len(product_variation)>0:
            # clear the highlighted filter for each item
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

# removes / decrements product item
def remove_cart(request,product_id,cart_item_id):
    cart =  Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1 # decrements quantity
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


# removes cart_item
def remove_cart_item(request,product_id,cart_item_id):
    cart =  Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')





def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total=0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (total  * 7)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # ignore if nothing

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items':cart_items,
        'tax': tax,
        'grand_total':grand_total,
    }
    return render(request,'store/cart.html',context)
