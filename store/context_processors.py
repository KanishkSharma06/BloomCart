from .models import Cart, CartItem # CartItem import karna zaroori hai

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            # Yahan cart.items.all() ki jagah filter use karein
            cart_items = CartItem.objects.filter(cart=cart)
            count = sum(item.quantity for item in cart_items)
            return {'cart_count': count}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}