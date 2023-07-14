from django.shortcuts import render, redirect
from products.models import *
from accounts.models import *
# Create your views here.

def homepage(request):

    categories = Category.objects.all()

    products = Product.objects.prefetch_related('variants')
    variants = []

    for product in products:
        first_variant = product.variants.first()
        if first_variant:
            variants.append(first_variant)
    print(variants)



    return render(request, 'pages/home_page.html', {'category_data': categories, 'variant_data': variants})

def productpage(request, id):
    all_products = Product.objects.all()[:5]

    variant = Variant.objects.get(id=id)
    variant_images = variant.colour.colour_images.all()


    return render(request, 'pages/product_page.html', {'variant':variant, 'all_products': all_products, 'variant_images':variant_images})

def test_page(request):
    return render(request, 'pages/test_page.html')

def profile_page(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)
        print(user)
        return render(request, 'pages/profile_page.html', {'user':user})

    return render(request, 'pages/profile_page.html',{'user': None})


