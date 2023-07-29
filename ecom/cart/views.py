from django.shortcuts import render, redirect
from products.models import *
from accounts.models import *
from cart.models import *
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db import transaction


# Create your views here.
def cart_page(request):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        user_carts = Cart.objects.filter(user=user)

        sub_total = Cart.objects.filter(user=user).aggregate(total=Sum('total'))
        savings = Cart.objects.filter(user=user).aggregate(total=Sum('discount'))

        return render(request, 'pages/cart.html', {'cart': user_carts, 'sub_total': sub_total['total'], 'savings': savings['total']})
    return render(request, 'pages/cart.html')


def add_to_cart(request, id):
    response_data = {'success': False}

    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        variant = Variant.objects.get(id=id)
        try:
            user_cart = Cart.objects.get(user=user, variant=variant)
            if Cart.objects.filter(variant=variant).exists():
                user_cart.quantity += 1
                user_cart.total= user_cart.calculate_total_price()
                user_cart.discount = user_cart.calculate_total_quantity_discount()
                user_cart.save()

        except Cart.DoesNotExist:
            new_cart = Cart.objects.create(user=user, variant=variant, quantity=1)
            new_cart.total = new_cart.calculate_total_price()
            new_cart.discount = variant.discount
            new_cart.save()

        response_data['success'] = True

    return JsonResponse(response_data)

def delete_cartItem(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])

        user_cart = Cart.objects.get(id=id)
        if user_cart:
            user_cart.delete()
    return redirect('cart_page')

def cartItem_quantity_update(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        user_cart = Cart.objects.get(id=id)

        if user_cart:
            new_quantity = int(request.GET.get('quantity'))
            user_cart.quantity = new_quantity
            user_cart.total = user_cart.calculate_total_price()
            user_cart.discount = user_cart.calculate_total_quantity_discount()
            user_cart.save()

            response_data = {
                'total': user_cart.total
            }
            return JsonResponse(response_data)

    return JsonResponse({'error': 'Failed to update quantity'})

def add_address(request):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        if request.method == 'POST':
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            country = request.POST.get('country')
            default_address = request.POST.get('default_address') == 'on'

            page =  request.POST.get('url')

            errors = {}
            if not address:
                errors['address'] = 'Address is required.'
            if not city:
                errors['city'] = 'City is required.'
            if not state:
                errors['state'] = 'State is required.'
            if not zip_code:
                errors['zip_code'] = 'Zip code is required.'
            if not country:
                errors['country'] = 'Country is required.'

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            address = ShippingAddress.objects.create(user=user, address=address, city=city, state=state, zip_code=zip_code, country=country)

            if default_address:
                ShippingAddress.objects.filter(user=user).exclude(id=address.id).update(default_address=False)

        return redirect(page)


def delete_address(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        address = ShippingAddress.objects.get(id=id)
        if address:
            try:
                if address.default_address:
                    next_address = ShippingAddress.objects.filter(user=user).exclude(id=address.id).first()
                    next_address.default_address = True
                    next_address.save()
            except:
                pass
            address.delete()
        return redirect('profile_page')

def edit_profile(request):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])

        if request.method == 'POST':
            name = request.POST['name']
            phone_number = request.POST['phone']
            email = request.POST['email']
            cur_password = request.POST['cur_password']
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            check_user = authenticate(request, username=user.phone_number,password=cur_password)
            if check_user:
                user_modal_user = User.objects.get(username=request.session['phone_number'])
                if new_password == confirm_password:
                    user.name = name
                    user.phone_number = phone_number
                    user.email = email
                    user.save()

                    user_modal_user.set_password(new_password)
                    user_modal_user.save()

                    return redirect('profile_page')
                else:
                    messages.error(request, "Passwords do not match.")
                    return redirect('address')
            else:
                messages.error(request, "Invalid credentials.")
                return redirect('address')
    return redirect('user_login')


# ----------------------------------Orders-----------------------------------------

def order_confirm(request):

    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']
        user = Profile.objects.get(phone_number=phone_number)

        if request.method == 'POST':
            address_id = request.POST.get('selected_address')
            payment_method = request.POST.get('payment_method')

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
                order.payment_type = payment_method
                order.save()

                order_num = order.order_num


            return render(request, 'pages/order_confirm.html',{'order_number':order_num})

    return HttpResponse('Invalid request')

def cancel_order(request, id):
    item = OrderDetail.objects.get(id=id)
    if item.status != 'cancelled' and item.status != 'delivered':
        item.order_status = 'cancelled'
        item.save()

    return redirect('profile_orders')

def return_request(request, id):
    item = OrderDetail.objects.get(id=id)
    if request.method == 'POST':
        item.order_status = 'returned'
        item.save()
        return redirect('profile_orders')

    if item.order_status == 'delivered':
        return render(request, 'pages/return_reason.html', {'item': item})


