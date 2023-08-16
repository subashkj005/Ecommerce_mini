from django.shortcuts import render,redirect
from accounts.models import Profile
from .models import Reviews
from products.models import Variant
from django.http import JsonResponse

def add_review(request, id):
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        if request.method == 'POST':
            review = request.POST.get('review')
            rating = request.POST.get('rating')
            variant = Variant.objects.get(id=id)
            
            user_review, created = Reviews.objects.get_or_create(
                user=user,
                product=variant.product,
                review=review,
                rating=rating
            )
            
            return redirect('add_review', id=id)

        return redirect('product_page', id=id)
    return redirect('user_login')
            

                