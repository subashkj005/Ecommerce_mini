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
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    has_user_given_review = False
    user_product_purchase_status = False
    
    variant = Variant.objects.get(id=id)

    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        # Review
        user_product_purchase_status = UserPurchasedProducts.objects.filter(user=user,
                                                                            products=variant.product).exists()
        has_user_given_review = Reviews.objects.filter(user=user, product=variant.product).exists()

    all_products = Product.objects.filter(category__id=variant.product.category.id)[:5]
    variant_images = variant.colour.colour_images.all()
    variant_reviews = Reviews.objects.filter(product = variant.product)
    review_count = Reviews.objects.filter(product = variant.product).aggregate(total_reviews=Count('id'))

    
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
    return render(request, 'pages/product_order_status.html')



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
        
        paginator = Paginator(addresses, 4)  

        page = request.GET.get('page')
        try:
            address_page = paginator.page(page)
        except PageNotAnInteger:
            address_page = paginator.page(1)
        except EmptyPage:
            address_page = paginator.page(paginator.num_pages)

        return render(request, 'pages/address.html', {'addresses':address_page, 'address_page':address_page})

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
        
        paginator = Paginator(orders, 3)  

        page = request.GET.get('page')
        try:
            orders_page = paginator.page(page)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)

        orders_list = {}

        for order in orders_page:
            order_details = OrderDetail.objects.filter(order=order)
            orders_list[order.id] = {
                'order': order,
                'order_details': order_details
            }

        return render(request, 'pages/profile_orders.html', {'orders_list': orders_list, 'orders_page': orders_page})

    return render(request, 'pages/profile_orders.html')


def prdouct_order_status(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        order_item = OrderDetail.objects.get(id=id)
        
        return render(request, 'pages/product_order_status.html', {'order_item':order_item})
    return redirect('user_login')

def generate_pdf_invoice(request):
    template_path = 'pdf/invoice_pdf.html'
    
    if request.method=='POST':
        order_item = OrderDetail.objects.get(id=request.POST.get('order_id'))
        
        context = {'order': order_item } 

    template = get_template(template_path)
    html = template.render(context)
    
    now = datetime.datetime.now()
    order_id = order_item.order.order_num
    filename = f'Invoice_{order_id}_{now.strftime("%Y%m%d%H%M%S")}.pdf'

    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response

def about_page(request):
    return render(request, 'pages/about.html')
