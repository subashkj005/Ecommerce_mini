from django.shortcuts import render, redirect
from products.models import *
from accounts.models import *
# Create your views here.

def homepage(request):

    categories = Category.objects.all()
    products = Product.objects.all()[:9]

    print(products)

    return render(request, 'pages/home_page.html', {'category_data': categories, 'product_data': products})

def productpage(request, id):
    all_products = Product.objects.all()[:5]
    product = Product.objects.get(id=id)
    product_images = product.images.all()
    # images is the related name of ProductImage model
    print(product)


    return render(request, 'pages/product_page.html', {'product':product, 'all_products': all_products, 'product_images':product_images})

def test_page(request):
    return render(request, 'pages/test_page.html')

def profile_page(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)
        print(user)
        return render(request, 'pages/profile_page.html', {'user':user})

    return render(request, 'pages/profile_page.html',{'user': None})


