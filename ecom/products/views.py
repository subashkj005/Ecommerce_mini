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
        products = Product.objects.filter(is_deleted=False)

        return render(request,'products/products.html', {'product_data': products, 'category_data': all_category })
    return render(request, 'custom_admin/admin_login.html')



def edit_products(request, id):
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = Category.objects.get(id=request.POST.get('category'))
        product.description = request.POST.get('description')
        product.save()

        return redirect('product')

    return render(request, 'products/products.html', {'product_data': Product.objects.all()})

def delete_image(request, id):
    image = ProductImage.objects.get(id=id)
    image.delete()
    return redirect('variant_page')

def add_products(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        category = Category.objects.get(id=request.POST.get('category'))
        description = request.POST.get('description')
        
        product = Product(name=name, category=category, description=description)
        product.save()

        return redirect('product')


def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.is_deleted = True
    product.save()

    return redirect('product')

def variant_page(request):
    variants = Variant.objects.filter(is_deleted=False)
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'custom_admin/variants_list.html', {'variant_data': variants, 'category_data': categories})


def add_variant_page(request):
    all_products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        colours = Color.objects.filter(product=product_id)
        return render(request, 'custom_admin/add_variants_page.html', {'product': product, 'colours': colours, 'all_products': all_products})

    return render(request, 'custom_admin/add_variants_page.html', {'all_products': all_products})

def add_color(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        colour_name = request.POST.get('colour_name')
        colour_code = request.POST.get('colour_code')

        product = Product.objects.get(id=product_id)
        color = Color.objects.create(product=product, name=colour_name, color_code=colour_code)

        return redirect('add_variant_page')

def add_variant(request):
    if request.method =='POST':
        product_id = request.POST.get('product_id')
        variant_colour = request.POST.get('variant_colour')
        variant_name = request.POST.get('variant_name')
        variant_price = request.POST.get('variant_price')
        variant_stock = request.POST.get('variant_stock')

        product = Product.objects.get(id=product_id)
        colour = Color.objects.get(id=variant_colour)

        variant = Variant.objects.create(product=product, colour=colour, name=variant_name, price=variant_price, original_price=variant_price, stock=variant_stock)

        # Adding Images

        images = request.FILES.getlist('images')
        if images:
            for image in images:
                variant_image = ProductImage(product=product, color=colour, image=image)
                variant_image.save()

        return redirect('add_variant_page')


def edit_variant(request, id):
    if request.method == 'POST':
        name = request.POST.get('product_name')
        colour = request.POST.get('colour')
        variant_name = request.POST.get('variant_name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')

        product = Product.objects.get(name=name)
        v_colour = Color.objects.get(id=colour)

        variant = Variant.objects.get(id=id)
        variant.name = variant_name
        variant.price = price
        variant.original_price = price
        variant.stock = stock
        variant.colour = v_colour
        variant.save()

        if description:
            product.description = description
            product.save()

        if images:
            for image in images:
                variant_image = ProductImage(product=product, color=v_colour, image=image)
                variant_image.save()

        return redirect('variant_page')

def variant_delete(request, id):
    variant = Variant.objects.get(id=id)
    variant.is_deleted = True
    variant.save()
    return redirect('variant_page')







