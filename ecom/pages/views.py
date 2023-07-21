from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from products.models import *
from accounts.models import *
from cart.models import *
from django.db.models import Sum
from django.db import transaction
# Create your views here.

def homepage(request):
    categories = Category.objects.all()

    products = Product.objects.prefetch_related('variants')
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

def test_page(request):
    return render(request, 'pages/checkout.html')



def checkout(request):
    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        addresses = ShippingAddress.objects.filter(user=user)
        products = Cart.objects.filter(user=user)
        sub_total = Cart.objects.filter(user=user).aggregate(total=Sum('total'))

        return render(request, 'pages/checkout.html', {'addresses':addresses, 'products':products, 'sub_total': sub_total['total']})


from django.db import transaction


def order_confirm(request):

    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        if request.method == 'POST':
            address_id = request.POST.get('selected_address')

            products = Cart.objects.filter(user=user)

            with transaction.atomic():
                # Create the order
                order = Order.objects.create(user=user)
                if address_id:
                    selected_address = ShippingAddress.objects.get(id=address_id)
                    order.address = selected_address
                    order.save()

                # Process each product in the cart
                for cart_item in products:
                    variant = cart_item.variant

                    # Create the order detail for the product
                    order_detail = OrderDetail.objects.create(
                        order=order,
                        product=variant,
                        quantity=cart_item.quantity,
                        price=cart_item.variant.price,
                        total_price=cart_item.variant.price * cart_item.quantity
                    )

                    # Reduce the quantity in the variant stock
                    cart_item.variant.stock -= cart_item.quantity
                    cart_item.variant.save()

                    # Delete the product from the cart
                    cart_item.delete()

                order_total_price = OrderDetail.objects.filter(order=order).aggregate(total=Sum('total_price'))
                order.total = order_total_price['total']
                order.save()

                order_num = order.order_num


            return render(request, 'pages/order_confirm.html',{'order_number':order_num})

    return HttpResponse('Invalid request')


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
        orders_dict = {}

        for order in orders:
            order_details = OrderDetail.objects.filter(order=order)
            orders_dict[order.id] = {
                'order': order,
                'order_details': order_details
            }

        return render(request, 'pages/profile_orders.html', {'orders_dict': orders_dict})

    return render(request, 'pages/profile_orders.html')

