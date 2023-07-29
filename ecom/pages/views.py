from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from products.models import *
from accounts.models import *
from cart.models import *
from django.db.models import Sum, Count, F
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
import razorpay
# Create your views here.

def homepage(request):
    categories = Category.objects.all()

    products = Product.objects.prefetch_related('variants')[:8]
    variants = []

    for product in products:
        first_variant = product.variants.first()
        if first_variant:
            variants.append(first_variant)

    return render(request, 'pages/home_page.html', {'category_data': categories, 'variant_data': variants})

def productpage(request, id):
    all_products = Product.objects.all()[:5]

    variant = Variant.objects.get(id=id)
    variant_images = variant.colour.colour_images.all()


    return render(request, 'pages/product_page.html', {'variant':variant, 'all_products': all_products, 'variant_images':variant_images})



def product_list(request):
    categories = Category.objects.all()

    selected_categories = request.GET.getlist('categories[]')
    selected_categories = [int(cat_id) for cat_id in selected_categories if cat_id.isdigit()]

    if not selected_categories:
        products = Product.objects.filter(is_deleted=False)
    else:
        products = []
        for cat_id in selected_categories:
            category_products = Product.objects.filter(category__id=cat_id, is_deleted=False)
            products.extend(category_products)

    sort_by = request.GET.get('sortby')
    if sort_by == 'low':
        products = sorted(products, key=lambda p: p.variants.first().price)
    elif sort_by == 'high':
        products = sorted(products, key=lambda p: p.variants.first().price, reverse=True)

    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    product_data = paginator.get_page(page)

    context = {
        'categories': categories,
        'products': product_data,
        'cat_id': selected_categories,
        'sort_by': sort_by,
    }



    return render(request, 'pages/product_listing.html', context)



def category_page(request, id):
    category = Category.objects.get(id=id)
    categories = Category.objects.all()

    selected_categories = request.GET.getlist('categories[]')
    selected_categories = [int(cat_id) for cat_id in selected_categories if cat_id.isdigit()]

    if not selected_categories:
        products = Product.objects.filter(category=category,is_deleted=False)
    else:
        products = []
        for cat_id in selected_categories:
            category_products = Product.objects.filter(category__id=cat_id, is_deleted=False)
            products.extend(category_products)

    sort_by = request.GET.get('sortby')
    if sort_by == 'low':
        products = sorted(products, key=lambda p: p.variants.first().price)
    elif sort_by == 'high':
        products = sorted(products, key=lambda p: p.variants.first().price, reverse=True)

    context = {
        'categories': categories,
        'products': products,
        'cat_id': selected_categories,
        'sort_by': sort_by,
    }

    return render(request, 'pages/product_listing.html', context)



def test_page(request):
    return render(request, 'pages/return_reason.html')



def checkout(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        addresses = ShippingAddress.objects.filter(user=user)
        products = Cart.objects.filter(user=user)
        sub_total = Cart.objects.filter(user=user).aggregate(total=Sum('total'))

        # Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': sub_total['total']*100, 'currency': 'INR', 'payment_capture': 1})

        context = {
            'addresses': addresses,
            'products': products,
            'sub_total': sub_total['total'],
            'payment': payment
        }

        return render(request, 'pages/checkout.html', context)



def address(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        addresses = ShippingAddress.objects.filter(user=user)

        return render(request, 'pages/address.html', {'addresses':addresses})

    return render(request, 'pages/address.html',{'user': None})

def profile(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        return render(request, 'pages/profile.html', {'user':user})

    return render(request, 'pages/profile.html',{'user': None})

def account_details(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        return render(request, 'pages/account_details.html', {'user':user})

    return render(request, 'pages/account_details.html',{'user': None})

def profile_orders(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        orders = Order.objects.filter(user=user)
        orders_list = {}

        for order in orders:
            order_details = OrderDetail.objects.filter(order=order)
            orders_list[order.id] = {
                'order': order,
                'order_details': order_details
            }

        return render(request, 'pages/profile_orders.html', {'orders_list': orders_list})

    return render(request, 'pages/profile_orders.html')

