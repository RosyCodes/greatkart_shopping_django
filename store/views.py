from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from carts.models import CartItem
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages

from orders.models import OrderProduct

from .forms import ReviewForm

# imports the private function
from carts.views import _cart_id
from django.http import HttpResponse

# imports Q for Querying a keyword using filter in 2 different fields
from django.db.models import Q

# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None

    # displays products by categories or not
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True).order_by('id')
        # adding pagination gets only specific # of items ie. 1
        paginator = Paginator(products, 1)
        # gets the URL of the specific page #
        page = request.GET.get('page')
        # shows the retrieved # of products ie. 1
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        # adding pagination gets only specific # of items ie. 3
        paginator = Paginator(products, 3)
        # gets the URL of the specific page #
        page = request.GET.get('page')
        # shows the retrieved # of products ie. 6
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {

        'products': paged_products,
        'product_count': product_count,

    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        # take note of the category__slug (2 underscores) to compare product_slug and category slug with Category model
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        # take note of the cart__cart_id (2 underscores) to go to cart field of CartItem model, then use the foreign key cart_id of Cart class
        # uses the private function _cart_id(request) to compare it with the cart_id
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
            request), product=single_product).exists()

    except Exception as e:
        raise e
    # checks if a user has some ordered product for reviews.
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # get the reviews for this specific product
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True)

    # get the product gallery
    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        # stores the searched word i.e keyword='jeans' to variable
        keyword = request.GET['keyword']
        if keyword:
            # searches the keyword in the descriptions of all products, check the double underscore for description__icontains=keyword OR if it's in the product name
            # the Q for query is to search for the keyword in 2 different fields. If this is not the case, simply use filter without Q
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    # stores the current web page url to this variable before the review
    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        try:
            # checks if the user has written a review for this product, so, the user can update
            # the use of user__id and product__id (2 underscore) to mean the user id of Account and product id of Product in the ReviewRating model.
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            # updates/replaces the old review with this new input
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, 'Thank you! Your review has been updated.')
            # after the product review, goes back to the web page before the review was made
            return redirect(url)
        except ReviewRating.DoesNotExist:
            # store a new review if user has not made a previous product review
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                # captures the form input with the name='subject'
                data.subject = form.cleaned_data['subject']
                # captures the form input with the name='rating'
                data.rating = form.cleaned_data['rating']
                # captures the form input with the name='review'
                data.review = form.cleaned_data['review']
                # stores the IP address of the user
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, 'Thank you! Your review has been submitted.')
                # after the product review, goes back to the web page before the review was made
                return redirect(url)
