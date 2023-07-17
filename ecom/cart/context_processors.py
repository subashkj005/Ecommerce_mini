from .models import Cart
from accounts.models import Profile

def cart_item_count(request):
    item_count = 0
    if 'phone_number' in request.session:
        user = Profile.objects.get(phone_number=request.session['phone_number'])
        item_count = Cart.objects.filter(user=user).count()
    return {'cart_item_count': item_count}