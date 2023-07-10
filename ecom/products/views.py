from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages

# Create your views here.


def categories(request):
    if 'username' in request.session:
        category = Category.objects.all()
        return render(request, 'products/category.html', {'category_data': category})
    return redirect('login')


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        check_category = Category.objects.filter(name=name).first()
        if check_category:
            messages.error(request, 'Category exists')
        else:
            category = Category(name=name,image=image)
            category.save()

    return redirect('categories')


def edit_category(request, category_id):
    if 'username' in request.session:
        category = Category.objects.get(id=category_id)

        if request.method == 'POST':
            category.name = request.POST.get('name')

            image = request.FILES.get('image')
            if image:
                category.image = image

            category.save()
            return redirect('categories')

        return render(request, 'products/category.html', {'category': category})
    return render(request, 'custom_admin/admin_login.html')

def delete_category(request,id):
    if 'username' in request.session:
        category = Category.objects.get(id=id)
        category.delete()

        return redirect('categories')
    return render(request, 'custom_admin/admin_login.html')


def product_page(request):
    if 'username' in request.session:
        all_category = Category.objects.all()
        products = Product.objects.filter(is_deleted=True)

        return render(request,'products/products.html', {'product_data': products, 'category_data': all_category })
    return render(request, 'custom_admin/admin_login.html')



def edit_products(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = Category.objects.get(id=request.POST.get('category'))
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')
        product.save()


        new_images = request.FILES.getlist('images')
        if new_images:
            product.images.all().delete()
            for image in new_images:
                product_image = ProductImage(product=product, image=image)
                product_image.save()

        return redirect('product')

    return render(request, 'products/products.html', {'product_data': Product.objects.all()})

def delete_image(request, id):
    image = ProductImage.objects.get(id=id)
    image.delete()
    return redirect('product')

def add_products(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        category = Category.objects.get(id=request.POST.get('category'))
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        
        product = Product(name=name, category=category, price=price, description=description, stock=stock,
                          image=image)
        product.save()
        
        images = request.FILES.getlist('images')[:3]
        for image in images:
            product_image = ProductImage(product=product, image=image)
            product_image.save()
            

        return redirect('product')




def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.is_deleted = False
    product.save()

    return redirect('product')








