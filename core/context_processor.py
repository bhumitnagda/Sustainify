from core.models import Category

def default(request):
    categories = Category.objects.all()
    # Use the session-based cart for everyone (authenticated or anonymous)
    cart = request.session.get('cart', {})
    cart_item_count = sum(cart.values())
    return {
        "categories": categories,
        "cart_item_count": cart_item_count,
    }
