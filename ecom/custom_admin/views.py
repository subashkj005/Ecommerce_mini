from django.shortcuts import render, redirect
from .models import Admin
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from accounts.models import Profile
from cart.models import Order, OrderDetail


# Create your views here.

def admin_login(request):
    if 'username' in request.session:
        return render(request,'custom_admin/admin_home.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in and make session
            request.session['username'] = username
            # Redirect to a success page or perform other actions
            return render(request,'custom_admin/admin_home.html')
        else:
            # Authentication failed, display an error message or perform other actions
            error_message = "Invalid username or password"
            return render(request, 'custom_admin/admin_login.html', {'error_message': error_message})

    # If the request method is GET, render the login form
    return render(request, 'custom_admin/admin_login.html')


def admin_home(request):
    if 'username' in request.session:
        return render(request, 'custom_admin/admin_home.html')

    return redirect('admin_login')

def users(request):
    user = Profile.objects.all()
    return render(request, 'custom_admin/users.html', {'users':user})

def user_status(request, id):
    # if 'username' in request.session:
        user = Profile.objects.get(id = id)
        if user.is_active:
            user.is_active = 0
            user.save()
            return redirect('users')
        else:
            user.is_active = 1
            user.save()
            return redirect('users')


def admin_logout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('admin_login')

def orders(request):
    if 'username' in request.session:

        orders = Order.objects.all().order_by('date_created')
        return render(request, 'custom_admin/orders.html', {'orders':orders})

    return redirect('admin_login')

def order_details(request, id):
    if 'username' in request.session:
        order = Order.objects.get(id = id)
        return render(request, 'custom_admin/order_details.html', {'order':order})

    return redirect('admin_login')

def order_status_update(request, ord_id, item_id):
    if 'username' in request.session:
        order = Order.objects.get(id = ord_id)
        item = OrderDetail.objects.get(id = item_id)

        if request.method == 'POST':
            status = request.POST.get('order_status')
            item.order_status = status
            item.save()

            return redirect('order_details', id=ord_id)

        return render(request, 'custom_admin.html', {'order':order} )
    return redirect('admin_login')

