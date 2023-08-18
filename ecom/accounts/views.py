from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .models import *
import random
from twilio.rest import Client
import re
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm

@never_cache
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            # Check if the phone number exists in the database
            try:
                profile = Profile.objects.get(phone_number=phone_number)
            except Profile.DoesNotExist:
                messages.error(request, 'Your account does not exist')
                return redirect('user_login')

            # Check if the user is active
            if not profile.is_active:
                messages.error(request, 'Your account is inactive')
                return redirect('user_login')

            # If the phone number exists and the user is active, authenticate the user
            user = authenticate(request, username=phone_number, password=password)

            if user is not None:
                otp = str(random.randint(1000, 9999))
                # send_otp(otp)

                print('--------------------')
                print('OTP IS ' + otp)
                print('--------------------')
                request.session['user'] = {'phone_number': phone_number, 'otp': otp}
                return render(request, 'accounts/login_otp.html', {'phone': phone_number})
            else:
                messages.error(request, 'Incorrect password')
                return redirect('user_login')
        else:
            messages.error(request, 'Invalid form data')
            return redirect('user_login')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def login_otp(request):

    user = request.session.get('user')
    otp = user['otp']
    phone_number = user['phone_number']
    if request.method == 'POST':
        entered_otp = f"{request.POST.get('otp1')}{request.POST.get('otp2')}{request.POST.get('otp3')}{request.POST.get('otp4')}"
        if entered_otp == otp:
            del request.session['user']
            request.session['phone_number'] = phone_number

            return redirect('user_home')

        else:
            context = 'Invalid OTP'
            return render(request, 'accounts/login_otp.html', {'otp_err': context})

    return redirect('user_login')
 
    
def send_otp(otp):

    account_sid = 'AC8e5d47f05c224aa88a156759e1fae3c6'
    auth_token = 'dc265a5cace4fcb7be65839fc581a759'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body='Your otp is '+otp,
        from_='+14849698077',
        to='+917559961892'
    )
    print(message.sid)


@never_cache
def signup(request):
    if 'phone_number' in request.session:
        return redirect('user_home')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Custom Validation Checks
        name_regex = r"^[A-Z][a-z]*$"
        email_regex = r"^\w+@gmail\.com$"
        phone_regex = r"^\d{10}$"
        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        if not re.match(name_regex, name):
            messages.error(request, 'Name should start with a capital letter and only contain letters.')
            return redirect('signup')

        if not re.match(email_regex, email):
            messages.error(request, 'Email should be in the format user@gmail.com')
            return render(request, 'accounts/signup.html')

        if not re.match(phone_regex, phone_number):
            messages.error(request, 'Phone number should be exactly 10 digits')
            return render(request, 'accounts/signup.html')

        if not re.match(password_regex, password):
            messages.error(request, 'Password should contain at least one lowercase letter, one uppercase letter, one digit, one special character, and be at least 8 characters long.')
            return render(request, 'accounts/signup.html')

        check_phone = Profile.objects.filter(phone_number=phone_number).first()

        if check_phone:
            messages.error(request, 'Phone number already registered')
            return render(request, 'accounts/signup.html')

        if password == confirm_password:
            otp = str(random.randint(1000, 9999))
            # send_otp(otp)
            print('--------------------')
            print('OTP IS ' + otp)
            print('--------------------')

            request.session['user_details'] = {
                'name': name,
                'email': email,
                'phone_number': phone_number,
                'password': password,
                'otp': otp
            }

            return render(request, 'accounts/otp.html')
        else:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')

    return render(request, 'accounts/signup.html')

def forgot_password(request):
    if 'phone_number' in request.session:
        return redirect('user_home')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        try:
            user = Profile.objects.get(phone_number=phone_number)

            if user is not None:
                otp = str(random.randint(1000, 9999))
                # send_otp(otp)
                print('--------------------')
                print('OTP IS ' + otp)
                print('--------------------')

                request.session['user_details'] = {
                    'phone_number': phone_number,
                    'otp': otp
                }
                return render(request, 'accounts/forgot_otp.html')

        except Profile.DoesNotExist:

            context = 'Enter number correctly'
            return render(request, 'accounts/forgot.html', {'message': context})

    return render(request, 'accounts/forgot.html')


def forgot_otp(request):
    user_details = request.session.get('user_details')

    # if not user_details:
    #     return redirect('forgot')

    mobile = user_details['phone_number']

    if request.method == 'POST':
        entered_otp = f"{request.POST.get('otp1')}{request.POST.get('otp2')}{request.POST.get('otp3')}{request.POST.get('otp4')}"
        print('---------------------------------------------------------------')
        print(user_details)
        print('---------------------------------------------------------------')
        if entered_otp == user_details['otp']:
            return render(request, 'accounts/pass_confirm.html')

        else:
            context = 'Invalid OTP'
            return render(request, 'accounts/forgot_otp.html', {'phone_number': mobile, 'otp_err': context})

    return render(request, 'accounts/forgot_otp.html', {'phone_number': mobile})


def password_update(request):
    user_details = request.session.get('user_details')

    if not user_details:
        return redirect('forgot')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password == confirm_password:
            phone_number = user_details['phone_number']
            user = Profile.objects.get(phone_number=phone_number)
            user.password = password
            user.save()

            del request.session['user_details']

            return redirect('user_login')

        else:
            message = "Password doesn't match"
            return render(request, 'accounts/pass_confirm.html', {'message': message})

    return render(request, 'accounts/pass_confirm.html')
@never_cache
def otp(request):
    user_details = request.session.get('user_details')
    mobile = user_details['phone_number']

    if not user_details:
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = f"{request.POST.get('otp1')}{request.POST.get('otp2')}{request.POST.get('otp3')}{request.POST.get('otp4')}"

        if entered_otp == user_details['otp']:
            user = User.objects.create_user(
                username=user_details['phone_number'],
                password=user_details['password']
            )

            profile = Profile.objects.create(
                user=user,
                email=user_details['email'],
                name=user_details['name'],
                phone_number=user_details['phone_number']
            )

            del request.session['user_details']

            return redirect('user_login')
        else:
            context = 'Invalid OTP'
            return render(request, 'accounts/otp.html', {'otp_err':context})


    return render(request, 'accounts/otp.html', {'phone_number': mobile})



def logout(request):
    if 'phone_number' in request.session:
        request.session.flush()
    return redirect('user_login')

