from django.shortcuts import render, redirect
from accounts.models import Profile
from wishlist.models import Wishlist
from products.models import Product, Variant
from cart.models import Cart


# Create your views here.
def wishlist(request):
    wishlist_items = None
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        wishlist_items = Wishlist.objects.filter(user=user).order_by('-id')

    return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist_items})


from django.http import JsonResponse


def add_to_wishlist(request, id):
    try:
        variant = Variant.objects.get(id=id)
    except Variant.DoesNotExist:
        pass

    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        wishlist, created = Wishlist.objects.get_or_create(user=user, variant=variant)

        if created:
            wishlist.variant = variant
            wishlist.save()  # Save the wishlist object when it is newly created

    # Return a success message in the JSON response
    return JsonResponse({'message': 'Product added to wishlist successfully'})


def delete_wishlist_item(request, id):
    if 'phone_number' in request.session:
        try:
            wishlist = Wishlist.objects.get(id=id)
        except Wishlist.DoesNotExist:
            pass

        wishlist.delete()

    return redirect('wishlist')


def wishlist_to_cart(request, id):
    if 'phone_number' in request.session:
        wishlist = Wishlist.objects.get(id=id)
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        variant = wishlist.variant
        cart, created = Cart.objects.get_or_create(user=user, variant=variant)

        if created:
            cart.total = cart.calculate_total_price()
            cart.discount = variant.discount
            # If the user cart have applied with a coupon
            cart_items = Cart.objects.filter(user=user, coupon__isnull=False)
            if cart_items:
                cart.coupon = cart_items.first().coupon
        else:
            if variant.stock > 0:
                cart.quantity += 1
                cart.total = cart.calculate_total_price()
                cart.discount = variant.discount
        cart.save()
        wishlist.delete()
    return redirect('cart_page')
