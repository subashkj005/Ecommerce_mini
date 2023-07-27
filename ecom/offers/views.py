from decimal import Decimal
from django.shortcuts import render, redirect
from products.models import Category
from offers.models import Offers

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
        discount_percentage = Decimal(request.POST.get('discount_percentage','0.00'))
        # Selecting category
        category = Category.objects.get(id=selected_category)

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

    return redirect('offers')

def offers(request):
    if 'username' in request.session:
        offers = Offers.objects.all()
        categories = Category.objects.all()
        return render(request, 'custom_admin/offers.html', {'offers': offers, 'categories':categories})
    return render(request,'custom_admin/offers.html')

def update_offers(request,id):
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

    return redirect('offers')

def offer_active(request, id):
    offer = Offers.objects.get(id=id)
    if offer.is_active == True:
        offer.is_active = False
    else:
        offer.is_active = True
    offer.save()

    return redirect('offers')