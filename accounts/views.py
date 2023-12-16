from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# imports the private function for session cart_id
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
import requests


def register(request):
    form = RegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # cleaned_data fetches the value from the submitted form
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            # customizes a username for the user by getting just the firstpart of the email address
            username = email.split('@')[0]

            # calls the Account create_user method and assigns the submitted form
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Creates User Profile upon User Registration
            profile = UserProfile()
            profile.user_id = user.id
            # assign a default profile image that is saved in the static files media\default\
            profile.profile_picture = 'default/default_user.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('accounts/account_verification_email.html', {

                'user': user,
                'domain': current_site,
                # encrypts the pk and send it as part of the email
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # create a new token of the user
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # instead of passing a long message that fades away in 4 seconds
            # messages.success(request,'Thank you for registering with us. We have sent you a verification email link. Please confirm this link.')
            return redirect('/accounts/login/?command=verification&email='+email)
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:

            # checks if the user has a non-empty cart before login
            try:
                # the _cart_id is a  private function that gets the session key from the carts\views.py
                cart = Cart.objects.get(cart_id=_cart_id(request))
                # provides grouping according to variations otherwise update the quantity
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()

                # if the cart is not empty before login, save this cart to the user
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # getting the product by category (size/color) using the cart_id
                    # if user has added products into his shopping cart before login
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variation.
                    cart_item = CartItem.objects.filter(user=user)
                    # checks if the current variation is present in the existing variations, then update the quantity
                    ex_var_list = []   # empty list of existing variations
                    id = []  # empty cart ID list

                    for item in cart_item:
                        existing_variation = item.variations.all()
                        # returns a query set, so type cast the queryset into a list
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # Ex. product_variation  =  [1, 2, 3, 4, 6]
                    # Ex. ex_var_list  =  [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            # redirects to checkout if user has some non-empty cart
            url = request.META.get('HTTP_REFERER')
            # uses the REQUEST library

            try:
                print('HELLO')
                query = requests.utils.urlparse(url).query
                # print('query -->',query) # results to query --> 'next=/cart/checkout/'
                # splits next=/cart/checkout/

                params = dict(x.split('=') for x in query.split('&'))
                # print('params -->',params) # returns params --> {'next': '/cart/checkout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')

# this check if login was made before logout


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        # decodes the encrypted PK from the email with the activation link
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        # if there is no user
        user = None

    # if there is a valid and confirmed user from the email confirmation
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # makes the user active, so they can login
        user.save()
        messages.success(
            request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('register')

# forces a login first before the dashboard access


@login_required(login_url='login')
def dashboard(request):

    # counts the number of orders
    orders = Order.objects.order_by(
        '-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    # gets user profile
    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            # checks exactly the email match & case sensitive.
            user = Account.objects.get(email__exact=email)

            # Resets password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {

                'user': user,
                'domain': current_site,
                # encrypts the pk and send it as part of the email
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # create a new token of the user
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    # similar to email validation
    try:
        # decodes the encrypted PK from the email with the activation link
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        # if there is no user
        user = None

     # if the token is a valid from a secured request from the email confirmation
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired.')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            # hash the string password to password format
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

# dashboard functionality


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

# requires the user to login before changing the password


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        print("post - change password ")
        # gets the form current / new passwords entered
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # Compares the exact username (case sensitive) from the Account model (2 underscore username__exact)
        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # Django's built-in method ; checks hashed password if they are the same
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)  # Django's built-in method
                user.save()

                # auth.logout(request) IF YOU WANT TO LOGOUT and LOGIN AFTER CHANGING THE PASSWORD, ADD THIS LINE

                messages.success(request, 'Password updated successfully. ')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    # 2 underscore to get the order_number through order as a FK
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
