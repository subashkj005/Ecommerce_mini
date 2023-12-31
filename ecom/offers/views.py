from decimal import Decimal
from django.db.models import F
from django.contrib import messages
from django.shortcuts import render, redirect
from products.models import *
from offers.models import Offers, Coupons, UsedCoupons
from cart.models import Cart
from accounts.models import Profile


# Create your views here.

def create_offers(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = bool(request.POST.get('is_active'))
        description = request.POST.get('description')
        selected_category = request.POST.get('selected_category')

        # Convert string value to decimals
        discount_percentage = Decimal(request.POST.get('discount_percentage', '0.00'))
        # Selecting category
        category = Category.objects.get(id=selected_category)
        # Check whether any offers already exists
        check_category_exists = Offers.objects.filter(category=category)
        if check_category_exists:
            messages.error(request, 'Already a offer assigned to this category')
            return redirect('create_offers')

        offer = Offers.objects.create(
            name=name,
            category=category,
            description=description,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage,
            is_active=is_active,
            image=image
        )

        if is_active:
            # Fetch the variants that need to be updated using the related name
            variants_to_update = Variant.objects.filter(product__category=category)

            # Update the variants in a single query using F Object
            variants_to_update.update(
                price=F('original_price') - F('original_price') * discount_percentage / 100,
                discount=F('original_price') * discount_percentage / 100
            )

        return redirect('offers')
    return render(request, 'custom_admin/create_offers.html', {'categories': categories})


def offers(request):
    if 'username' in request.session:
        offers = Offers.objects.all()
        categories = Category.objects.all()
        return render(request, 'custom_admin/offers.html', {'offers': offers, 'categories': categories})
    return render(request, 'custom_admin/offers.html')


def update_offers(request, id):
    name = request.POST.get('name')
    image = request.FILES.get('image')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    discount_percentage = request.POST.get('discount_percentage')
    is_active = bool(request.POST.get('is_active'))
    description = request.POST.get('description')
    selected_category = request.POST.get('selected_category')

    offer = Offers.objects.get(id=id)
    category = Category.objects.get(id=selected_category)

    offer.name = name
    offer.start_date = start_date
    offer.end_date = end_date
    offer.is_active = is_active
    offer.category = category
    offer.discount_percentage = discount_percentage

    if image:
        offer.image = image
    if description:
        offer.description = description
    offer.save()

    if is_active:
        # Fetch the variants that need to be updated using the related name
        variants_to_update = Variant.objects.filter(product__category=category)

        # Update the variants in a single query using F Object
        variants_to_update.update(
            price=F('original_price') - F('original_price') * discount_percentage / 100,
            discount=F('original_price') * discount_percentage / 100
        )

    return redirect('offers')


def offer_active(request, id):
    offer = Offers.objects.get(id=id)
    category = offer.category

    discount_percentage = offer.discount_percentage

    if not offer.is_active:
        variants_to_update = Variant.objects.filter(product__category=category)
        variants_to_update.update(
            price=F('original_price') - F('original_price') * discount_percentage / 100,
            discount=F('original_price') * discount_percentage / 100
        )
        offer.is_active = True
    else:
        variants_to_update = Variant.objects.filter(product__category=category)
        variants_to_update.update(
            price=F('original_price'),
            discount=0
        )
        offer.is_active = False

    offer.save()

    return redirect('offers')


def coupon_page(request):
    if 'username' in request.session:
        coupons = Coupons.objects.filter(is_deleted=False)
        return render(request, 'custom_admin/coupons.html', {'coupons': coupons})
    return render(request, 'admin_login')


def create_coupon(request):
    if 'username' in request.session:
        if request.method == 'POST':
            code = request.POST.get('code')
            discount = request.POST.get('discount')
            min_amount = request.POST.get('min_amount')
            valid_to = request.POST.get('valid_to')

            coupon = Coupons.objects.create(code=code, discount=discount, min_amount=min_amount, valid_to=valid_to)
            return redirect('coupon_page')
        return render(request, 'custom_admin/create_coupon.html')
    return render(request, 'admin_login')

def edit_coupon(request, id):
    if 'username' in request.session:
        if request.method == 'POST':
            coupon = Coupons.objects.get(id=id)
            coupon.code = request.POST.get('code')
            coupon.discount = request.POST.get('discount')
            coupon.min_amount = request.POST.get('min_amount')
            coupon.valid_to = request.POST.get('valid_to')
            coupon.save()

        return redirect('coupon_page')
    return render(request, 'custom_admin/admin_login.html')

def coupon_activate(request, id):
    if 'username' in request.session:
        coupon = Coupons.objects.get(id=id)
        if coupon.is_active:
            coupon.is_active = False
        else:
            coupon.is_active = True
        coupon.save()

        return redirect('coupon_page')
    return render(request, 'custom_admin/admin_login.html')


def apply_coupon(request):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])

        if request.method == 'POST':
            entered_coupon = request.POST.get('entered_coupon')

            try:
                coupon = Coupons.objects.get(code=entered_coupon)
            except Coupons.DoesNotExist:
                messages.error(request, "Coupon doesn't exist")
                return redirect('cart_page')

            try:
                carts = Cart.objects.filter(user=user)
            except Cart.DoesNotExist:
                messages.error(request, "Add products to cart")
                return redirect('cart_page')

            used_coupon = UsedCoupons.objects.filter(user=user, coupons=coupon).exists()

            if coupon.is_valid and coupon.is_active:
                if not used_coupon:
                    cart_coupon = Cart.objects.filter(user=user, coupon__isnull=True)
                    if cart_coupon.exists():
                        carts.update(coupon=coupon)
                        messages.success(request, "Coupon Applied")
                    else:
                        messages.error(request, "Already coupon applied")
                else:
                    messages.error(request, "Coupon already used")
            else:
                messages.error(request, "Coupon expired")

            return redirect('cart_page')

        return redirect('cart_page')

    return redirect('user_login')

def delete_cart_coupon(request):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        carts = Cart.objects.filter(user=user)
        carts.update(coupon = None)
        return redirect('cart_page')
    return redirect('user_login')









