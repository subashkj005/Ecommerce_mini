from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from products.models import *
from accounts.models import *
from cart.models import *
from reviews.models import Reviews
from django.db.models import Sum, Count, F
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import razorpay
import json
from django.template.loader import render_to_string
# Create your views here.

def homepage(request):
    categories = Category.objects.all()

    products = Product.objects.prefetch_related('variants')[:8]
    variants = []

    for product in products:
        first_variant = product.variants.first()
        if first_variant:
            variants.append(first_variant)
    print(categories)
    print(variants)
    return render(request, 'pages/home_page.html', {'category_data': categories, 'variant_data': variants})

def productpage(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
    variant = Variant.objects.get(id=id)
    all_products = Product.objects.filter(category__id=variant.product.category.id)[:5]
    variant_images = variant.colour.colour_images.all()
    variant_reviews = Reviews.objects.filter(product = variant.product)
    review_count = Reviews.objects.filter(product = variant.product).aggregate(total_reviews=Count('id'))
    user_product_purchase_status = UserPurchasedProducts.objects.filter(user=user, products=variant.product).exists()
    has_user_given_review = Reviews.objects.filter(user=user,product=variant.product).exists()
    
    context = {
        'variant':variant,
        'all_products': all_products,
        'variant_images':variant_images,
        'reviews': variant_reviews,
        'review_count':review_count['total_reviews'],
        'user_product_purchase_status':user_product_purchase_status,
        'has_user_given_review':has_user_given_review
    }
    return render(request, 'pages/product_page.html', context)

def search_products(request):
    if request.method == 'POST':
        categories = Category.objects.all()
        search = request.POST.get('search')

        if search:
            products = Product.objects.filter(name__icontains=search)
        else:
            products = []
            
        context = {
        'categories': categories,
        'products': products,
        }
               
    return render(request, 'pages/product_listing.html', context)

def product_list(request):
    categories = Category.objects.all()

    products = Product.objects.filter(is_deleted=False)


    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    product_data = paginator.get_page(page)

    context = {
        'categories': categories,
        'products': product_data,
    }
    
    return render(request, 'pages/product_listing.html', context)



def filter_products(request):
    if request.method == 'POST':
        try:
            # Get the raw JSON data from the request body
            json_data = request.body.decode('utf-8')

            # Parse the JSON data into a Python dictionary
            data_dict = json.loads(json_data)

            # Access the selected category IDs from the 'categories' key as a list
            category_ids_list = data_dict.get('categories', [])

            if category_ids_list:
                products = Product.objects.filter(category__id__in=category_ids_list, is_deleted=False)
            else:
                products = Product.objects.filter(is_deleted=False)
                
            # Pagination
            paginator = Paginator(products, 8)
            page_number = request.GET.get('page')
            product_page = paginator.get_page(page_number)

            # Prepare the product data to send as JSON
            product_data = [
                {
                    'name': product.name,
                    'category_name':product.category.name,
                    'colour_name':product.colors.first().name,
                    'variant_id': product.variants.first().id,
                    'offer_price': product.variants.first().price,
                    'original_price':product.variants.first().original_price,
                    'image_url': product.images.first().image.url,
                    'has_offer': product.category.offers.exists() and product.category.offers.first().is_valid and product.category.offers.first().is_active,
                }
                for product in products
            ]

            response_data = {
                'products': product_data
            }
            
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Invalid method'}, status=405)

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
    return render(request, 'wishlist/wishlist.html')



def checkout(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        addresses = ShippingAddress.objects.filter(user=user)
        products = Cart.objects.filter(user=user)
        sub_total = Cart.objects.filter(user=user).aggregate(total=Sum('total'))

        if not products:
            return redirect('cart_page')

        if products.first().coupon:
            amount = sub_total['total']-products.first().coupon.discount
        else:
            amount = sub_total['total']

        # Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': amount*100, 'currency': 'INR', 'payment_capture': 1})

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

        orders = Order.objects.filter(user=user).order_by('-id')
        orders_list = {}

        for order in orders:
            order_details = OrderDetail.objects.filter(order=order)
            orders_list[order.id] = {
                'order': order,
                'order_details': order_details
            }

        return render(request, 'pages/profile_orders.html', {'orders_list': orders_list})

    return render(request, 'pages/profile_orders.html')

