from django.urls import path , include
from core.views import index, product_list_view, category_list_view, home, vendor_list_view, about, vendor_detail_view, \
    contact, shop, single_shop, add_to_cart, category_product_list_view, tag_list, search_view, remove_from_cart, \
    cart_view, update_cart_quantity, check_out, customer_dashboard, customer_settings, customer_orders, \
    customer_account, update_settings, stripe_payment, stripe_payment_verify, stripe_payment_cancel, payment_status, \
    payment_completed_view, payment_failed_view,vendor_signup,vendor_login,vendor_dashboard,product_review,vendor_add_product,vendor_edit_product,verify_email

app_name = "core"

urlpatterns =[
    #homepage
    path("", index, name = "index"),
    path("products/",product_list_view,name = "product_list"),
    path("home/",home,name = "home"),

    #Category
    path("category/",category_list_view,name = "category_list"),
    path("category/<str:c_id>",category_product_list_view,name = "category_product_list"),

    #vendor
    path("vendors/", vendor_list_view, name="vendor_list"),
    path('vendors/<str:v_id>/', vendor_detail_view, name='vendor_detail'),

    path("about/",about,name = "about"),
    path("contact/",contact,name = "contact"),
    path("shop/",shop,name = "shop"),
    path('shop/<str:product_id>/', single_shop, name='single_shop'),

    # Add to cart
    path('add_to_cart/<str:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:product_id>/', remove_from_cart, name='remove_from_cart'),
    path("cart/", cart_view, name="cart"),
    path("update-cart-quantity/<str:product_id>/", update_cart_quantity, name="update_cart_quantity"),

    # Tags
    path("products/tags/<slug:tag_slug>/", tag_list, name="tags"),

    # Search
    path("search/",search_view,name = "search"),

    # check_out
    path("checkout/", check_out, name="checkout"),

    # Customer Dashboard URLs
    path("customer_dashboard/", customer_dashboard, name="customer_dashboard"),
    path("customer_orders/", customer_orders, name="customer_orders"),
    path("customer_account/",customer_account, name="customer_account"),
    path("customer_settings/",customer_settings, name="customer_settings"),
    path("update_settings/",update_settings, name="update_settings"),

    # stripe
    path("stripe_payment/<int:order_id>/", stripe_payment, name="stripe_payment"),
    path("stripe_payment_verify/<int:order_id>/", stripe_payment_verify, name="stripe_payment_verify"),
    path("stripe_payment_cancel/<int:order_id>/", stripe_payment_cancel, name="stripe_payment_cancel"),
    path('payment_status/<str:order_id>/', payment_status, name='payment_status'),

    # Paypal
    path('paypal/',include('paypal.standard.ipn.urls')),

# paypal payments
    path('payment_completed/',payment_completed_view , name = 'payment_completed'),
    path('payment_failed/', payment_failed_view, name='payment_failed'),

# Vendor
    path('vendor_signup/', vendor_signup, name='vendor_signup'),
    path('vendor_login/', vendor_login, name='vendor_login'),
    path('vendor_dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('add-product/', vendor_add_product, name='vendor_add_product'),
    path('edit-product/<str:p_id>/', vendor_edit_product, name='vendor_edit_product'),

# Review and Rating system
    path('product/<str:p_id>/review/',product_review, name='product_review'),

# Email verification
    path('verify-email/',verify_email, name='verify_email'),
]