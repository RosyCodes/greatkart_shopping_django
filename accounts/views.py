from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    form = RegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # cleaned_data fetches the value from the submitted form
            first_name = form.cleaned_data['first_name']
            last_name  = form.cleaned_data['last_name']
            email      = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password    = form.cleaned_data['password']
            # customizes a username for the user by getting just the firstpart of the email address
            username = email.split('@')[0]

            # calls the Account create_user method and assigns the submitted form
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email, username=username,password=password)
            user.phone_number = phone_number
            user.save()
            
            # USER ACTIVATION 
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('accounts/account_verification_email.html',{

                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #encrypts the pk and send it as part of the email
                'token': default_token_generator.make_token(user), # create a new token of the user
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # instead of passing a long message that fades away in 4 seconds
            # messages.success(request,'Thank you for registering with us. We have sent you a verification email link. Please confirm this link.')
            return redirect('/accounts/login/?command=verification&email='+email)        
    return render(request,'accounts/register.html',{'form':form})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,"You are now logged in.")
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials.')
            return redirect('login')

    return render(request,'accounts/login.html')

# this check if login was made before logout
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out.')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        # decodes the encrypted PK from the email with the activation link
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        # if there is no user
        user = None
    
    # if there is a valid and confirmed user from the email confirmation
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True # makes the user active, so they can login
        user.save()
        messages.success(request,"Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request,"Invalid activation link.")
        return redirect('register')

# forces a login first before the dashboard access
@login_required(login_url = 'login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) # checks exactly the email match & case sensitive.
           
            # Resets password email 
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html',{

                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #encrypts the pk and send it as part of the email
                'token': default_token_generator.make_token(user), # create a new token of the user
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist.')
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')


def resetpassword_validate(request,uidb64,token):
    # similar to email validation
    try:
        # decodes the encrypted PK from the email with the activation link
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        # if there is no user
        user = None

     # if the token is a valid from a secured request from the email confirmation
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link has expired.')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) # hash the string password to password format
            user.save()
            messages.success(request,'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request,'Passwords do not match.')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')
    