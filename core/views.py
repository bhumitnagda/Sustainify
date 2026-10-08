import logging
import PyPDF2
import re
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import title
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from .models import Product, Product_Reivew, Certificate
from django.urls import reverse
from .forms import ReviewForm, VerificationCodeForm
from core.forms_vendor import VendorSignupForm, ProductImagesForm, ProductForm
from userauths.models import ContactUs, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Wishlist, Address, CartOrder
from django.core.mail import EmailMultiAlternatives
import stripe
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from core.models import (
    Product,
    Category,
    Vendor,
    CartOrderItems,
    CartOrder,
    Wishlist,
    Product_Images,
    Product_Reivew,
    Address
)
from django.core.mail import send_mail
import datetime
import random

from .utils import send_verification_email

logger = logging.getLogger(__name__)

# Homepage and Home Views
def index(request):
    logger.debug("Accessing index view")
    products = Product.objects.filter(featured=True, product_status="published").order_by("-id")
    context = {'products': products}
    return render(request, 'core/index.html', context)

def home(request):
    logger.debug("Accessing home view")
    products = Product.objects.filter(featured=True, product_status="published").order_by("-id")
    context = {'products': products}
    return render(request, 'core/index.html', context)

# Product Listing Views
def product_list_view(request):
    logger.debug("Accessing product_list_view")
    category_id = request.GET.get('category')
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(product_status="published", category__id=category_id).order_by("-id")
        context = {'products': products, 'current_category': current_category}
        return render(request, 'core/category_products.html', context)
    else:
        products = Product.objects.filter(product_status="published").order_by("-id")
        context = {'products': products}
        return render(request, 'core/product_list.html', context)

def category_list_view(request):
    logger.debug("Accessing category_list_view")
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, 'core/category_list.html', context)

def category_product_list_view(request, c_id):
    logger.debug(f"Accessing category_product_list_view for c_id: {c_id}")
    category = Category.objects.get(c_id=c_id)
    products = Product.objects.filter(product_status="published", category=category)
    context = {
        "category": category,
        "products": products,
    }
    return render(request, 'core/category_product_list.html', context)

# Vendor Views
def vendor_list_view(request):
    logger.debug("Accessing vendor_list_view")
    vendors = Vendor.objects.all()
    context = {"Vendors": vendors}
    return render(request, 'core/vendor_list.html', context)

def vendor_detail_view(request, v_id):
    logger.debug(f"Accessing vendor_detail_view for v_id: {v_id}")
    vendor = get_object_or_404(Vendor, v_id=v_id)
    Products = Product.objects.filter(vendor=vendor)
    return render(request, 'core/vendor_detail.html', {'Vendor': vendor, 'Products': Products})

# Static Pages
def about(request):
    logger.debug("Accessing about view")
    return render(request, "core/about.html")

def contact(request):
    logger.debug("Accessing contact view")
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        try:
            ContactUs.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Contact form error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'core/contact.html')

def ajax_contact(request):
    logger.debug("Accessing ajax_contact view")
    pass

def shop(request):
    logger.debug("Accessing shop view")
    products = Product.objects.filter(product_status="published")
    category = request.GET.get('category', '')

    if category:
        products = products.filter(category__title__iexact=category)

    products = products.order_by("-id")
    return render(request, "core/shop.html", {'products': products})

# Single Product View
def single_shop(request, product_id):
    logger.debug(f"Accessing single_shop for product_id: {product_id}")
    product_instance = get_object_or_404(Product, p_id=product_id)
    product_instance.refresh_from_db()
    quantities = range(1, 11)
    form = ReviewForm()

    # Fetch related products from the same category, excluding the current product
    related_products = Product.objects.filter(
        category=product_instance.category
    ).exclude(p_id=product_id).order_by('-id')[:10]

    shoe_sizes = "UK 6.5 | EU 40,UK 7 | EU 41 ,UK 8 | EU 42,UK 9 | EU 43,UK 9.5 | EU 44,UK 10 | EU 45".split(",")
    review = Product_Reivew.objects.filter(product=product_instance)
    return render(request, 'core/single_shop.html', {
        'product': product_instance,
        'quantities': quantities,
        'shoe_sizes': shoe_sizes,
        'related_products': related_products,
        'review': review,
        'form': form,
    })

########## Cart Functions (Add, Remove, and Display Cart) ##########
@login_required(login_url='userauths:sign-in')
def add_to_cart(request, product_id):
    logger.debug(f"Adding product {product_id} to cart")
    product = get_object_or_404(Product, p_id=product_id)

    # Get the desired quantity (default is 1)
    if request.method == 'POST':
        quantity = request.POST.get("quantity", 1)
    else:
        quantity = request.GET.get("quantity", 1)

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    # Retrieve the cart from session or create an empty cart
    cart = request.session.get('cart', {})

    # Update cart quantity or add new entry
    if str(product.p_id) in cart:
        cart[str(product.p_id)] += quantity
    else:
        cart[str(product.p_id)] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    # If the request is AJAX, return a JSON response instead of redirecting.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_item_count': sum(cart.values())
        })

    return redirect('core:cart')

def remove_from_cart(request, product_id):
    logger.debug(f"Removing product {product_id} from cart")
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('core:cart')

def cart_view(request):
    logger.debug("Accessing cart_view")
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for pid, qty in cart.items():
        try:
            product = Product.objects.get(p_id=pid)
            item_total = product.price * qty
            cart_items.append({
                'product': product,
                'quantity': qty,
                'item_total': item_total
            })
            subtotal += item_total
        except (Product.DoesNotExist, ValueError):
            continue

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'quantities': range(1, 11),
    }
    return render(request, 'core/add_to_cart.html', context)

def update_cart_quantity(request, product_id):
    logger.debug(f"Updating cart quantity for product {product_id}")
    if request.method == "POST":
        new_quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", {})
        if product_id in cart:
            cart[product_id] = new_quantity
            request.session["cart"] = cart
    return redirect('core:cart')

########## Tags ###############
def tag_list(request, tag_slug=None):
    logger.debug(f"Accessing tag_list with tag_slug: {tag_slug}")
    products = Product.objects.filter(product_status="published").order_by("-id")
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
    context = {"products": products}
    return render(request, "core/tag.html", context)

# Search View
def search_view(request):
    logger.debug("Accessing search_view")
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query).order_by("-date")
    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)

@login_required(login_url='userauths:sign-in')
def check_out(request):
    logger.debug("Accessing check_out")
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '200',
        'item_name': 'Order_item_no.3',
        'invoice': 'Invoice_no_3',
        'currency_code': 'INR',
        'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("core:payment_completed")),
        'cancel_url': 'http://{}{}'.format(host, reverse("core:payment_failed")),
    }
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip")
        phone = request.POST.get("phone")

        cart = request.session.get('cart', {})
        cart_items = []
        subtotal = 0
        for pid, qty in cart.items():
            try:
                product = Product.objects.get(p_id=pid)
                item_total = product.price * qty
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'total_price': item_total
                })
                subtotal += item_total
            except (Product.DoesNotExist, ValueError):
                continue

        shipping_cost = 10 if subtotal > 0 else 0
        cart_total = subtotal + shipping_cost

        order = CartOrder.objects.create(
            user=request.user,
            price=cart_total,
        )

        request.session['cart'] = {}

        if payment_method == "stripe":
            return redirect("core:stripe_payment", order_id=order.id)
        elif payment_method == "paypal":
            context = {
                'cart_items': cart_items,
                'cart_subtotal': subtotal,
                'shipping_cost': shipping_cost,
                'cart_total': cart_total,
                'paypal_payment_button': paypal_payment_button,
                'order': order,
            }
            return render(request, "core/checkout.html", context)
        else:
            order.paid_Status = False
            order.product_status = "process"
            order.save()
            messages.success(request, "Order confirmed and thanks for shopping!")
            return redirect("core:customer_orders")
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        subtotal = 0
        for pid, qty in cart.items():
            try:
                product = Product.objects.get(p_id=pid)
                item_total = product.price * qty
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'total_price': item_total
                })
                subtotal += item_total
            except (Product.DoesNotExist, ValueError):
                continue

        shipping_cost = 10 if subtotal > 0 else 0
        cart_total = subtotal + shipping_cost

        context = {
            'cart_items': cart_items,
            'cart_subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'cart_total': cart_total,
            'paypal_payment_button': paypal_payment_button,
        }
        return render(request, "core/checkout.html", context)

@login_required
def customer_dashboard(request):
    logger.debug(f"Accessing customer_dashboard for user: {request.user}")
    recent_orders = CartOrder.objects.filter(user=request.user).order_by('-order_date')[:5]
    wishlist_items = Wishlist.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    context = {
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
    }
    return render(request, 'core/customer_dashboard.html', context)

@login_required
def customer_orders(request):
    logger.debug(f"Accessing customer_orders for user: {request.user}")
    orders = CartOrder.objects.filter(user=request.user).order_by('-order_date')
    context = {'orders': orders}
    return render(request, 'core/customer_orders.html', context)

@login_required
def customer_account(request):
    logger.debug(f"Accessing customer_account for user: {request.user}")
    context = {
        'user': request.user,
    }
    return render(request, 'core/customer_account.html', context)

@login_required
def customer_settings(request):
    logger.debug(f"Accessing customer_settings for user: {request.user}")
    context = {}
    return render(request, 'core/customer_settings.html', context)

@login_required
def update_settings(request):
    logger.debug(f"Accessing update_settings for user: {request.user}")
    if request.method == "POST":
        notification = request.POST.get("notification")
        messages.success(request, "Settings updated successfully!")
    return redirect('core:customer_settings')

################ STRIPE ###########################
@csrf_exempt
@login_required(login_url='userauths:sign-in')
def stripe_payment(request, order_id):
    logger.debug(f"Accessing stripe_payment for order_id: {order_id}")
    try:
        order = CartOrder.objects.get(pk=order_id)
    except CartOrder.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    total_amount = int(order.price * 100)

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=order.user.email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": f"Order #{order.id}",
                        },
                        "unit_amount": total_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("core:stripe_payment_verify", args=[order.id])
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("core:stripe_payment_cancel", args=[order.id])
            ),
        )
    except Exception as e:
        logger.error(f"Stripe payment error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

    return redirect(checkout_session.url)


@login_required(login_url='userauths:sign-in')
def stripe_payment_verify(request, order_id):
    logger.debug(f"Accessing stripe_payment_verify for order_id: {order_id}")
    try:
        order = CartOrder.objects.get(pk=order_id)
    except CartOrder.DoesNotExist:
        return HttpResponse("Order not found", status=404)

    session_id = request.GET.get("session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.error(f"Stripe session retrieval error: {str(e)}")
        return HttpResponse(f"Error retrieving session: {e}", status=500)

    if session.payment_status == "paid":
        if not order.paid_Status:
            order.paid_Status = True
            order.save()
        return redirect(f"/payment_status/{order.id}/?payment_status=paid")
    else:
        return redirect(f"/payment_status/{order.id}/?payment_status=failed")

def stripe_payment_cancel(request, order_id):
    logger.debug(f"Accessing stripe_payment_cancel for order_id: {order_id}")
    return render(request, "core/stripe_payment_cancel.html", {"order_id": order_id})

def payment_status(request, order_id):
    logger.debug(f"Accessing payment_status for order_id: {order_id}")
    payment_status = request.GET.get('payment_status', '')
    try:
        order = CartOrder.objects.get(id=order_id)
    except CartOrder.DoesNotExist:
        return HttpResponse("Order not found", status=404)

    context = {
        'payment_status': payment_status,
        'order_id': order_id,
        'order': order
    }
    return render(request, 'core/payment_status.html', context)

def payment_completed_view(request):
    logger.debug("Accessing payment_completed_view")
    return render(request, 'core/payment_completed.html')

def payment_failed_view(request):
    logger.debug("Accessing payment_failed_view")
    return render(request, 'core/payment_failed.html')

#### VENDOR ######################

User = get_user_model()



def vendor_signup(request):
    """
    1. Creates a new User (user_type=2), inactive.
    2. Creates a UserProfile (auto-generates a 6-digit code) and emails it.
    3. Parses & saves the uploaded ISO PDF as a Certificate.
    4. Logs the user in and redirects to /verify-email/.
    """
    if request.method == 'POST':
        form = VendorSignupForm(request.POST, request.FILES)
        if form.is_valid():
            # 1) Create inactive vendor user
            user = form.save(commit=False)
            user.user_type = 2               # mark as Vendor
            user.is_active = False           # lock until verified
            user.save()

            # 2) Create profile (this auto-generates a code)
            profile = UserProfile.objects.create(user=user)
            code = profile.verification_code

            # **NEW:** send the code via email
            send_verification_email(user, code)

            # 3) Parse ISO PDF and save Vendor + Certificate
            iso = form.cleaned_data['iso_certificate']
            text = ""
            try:
                reader = PyPDF2.PdfReader(iso)
                text = "".join(p.extract_text() or "" for p in reader.pages)
            except:
                pass

            no_pat   = r"Certificate\s*(?:No(?:\.|umber)?):?\s*([A-Za-z0-9/\-]+)"
            date_pat = r"(\d{2}[./\-]\d{2}[./\-]\d{4})"
            iss_pat  = rf"Issuance\s+Date:?\s*{date_pat}"
            exp_pat  = rf"(?:Expiry|Expires?):?\s*{date_pat}"

            cert_no_m = re.search(no_pat, text, re.IGNORECASE)
            iss_m     = re.search(iss_pat, text, re.IGNORECASE)
            exp_m     = re.search(exp_pat, text, re.IGNORECASE)

            def parse_date(s):
                for fmt in ("%d.%m.%Y","%d/%m/%Y","%d-%m-%Y"):
                    try: return datetime.datetime.strptime(s, fmt).date()
                    except: pass
                return datetime.date.today()

            cert_no    = cert_no_m.group(1) if cert_no_m else ""
            issued_on  = parse_date(iss_m.group(1)) if iss_m else datetime.date.today()
            expires_on = parse_date(exp_m.group(1)) if exp_m else datetime.date.today()

            vendor = Vendor.objects.create(
                user        = user,
                title       = form.cleaned_data['title'],
                contact     = form.cleaned_data['contact'],
                email       = user.email,
                description = form.cleaned_data['description'],
                address     = form.cleaned_data['address'],
                image       = iso
            )
            Certificate.objects.create(
                vendor     = vendor,
                file       = iso,
                cert_no    = cert_no,
                issued_on  = issued_on,
                expires_on = expires_on,
            )

            # 4) Log the user in (so they can access /verify-email/)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            messages.success(request,
                "Registration successful! A 6-digit code has been sent to your email. "
                "Enter it now to verify your account."
            )
            return redirect('core:verify_email')

        messages.error(request, "Please fix the errors below.")
    else:
        form = VendorSignupForm()

    return render(request, 'core/vendor_signup.html', {'form': form})


from .forms import VerificationCodeForm  # Add this import

# core/views.py

import logging
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from userauths.models import UserProfile
from core.models import Vendor
from .forms import VerificationCodeForm

logger = logging.getLogger(__name__)

def verify_email(request):
    logger.debug("Accessing verify_email view")
    if request.method == "POST":
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # 1) Look up the profile by code
                profile = UserProfile.objects.get(verification_code=code)
            except UserProfile.DoesNotExist:
                logger.debug("Invalid verification code")
                messages.error(request, "Invalid verification code.")
                return render(request, "core/verify_email.html", {'form': form})

            # 2) Mark profile and user as verified/active
            profile.is_verified = True
            profile.verification_code = None
            profile.save()

            user = profile.user
            user.is_active = True
            user.save()

            # 3) Log them in (so they can hit their dashboard)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Email verified successfully!")

            # 4) Redirect based on user_type
            #    2 == Vendor, 1 == Customer
            if getattr(user, 'user_type', None) == 2:
                return redirect("core:vendor_dashboard")
            else:
                return redirect("core:index")

        # form invalid
        messages.error(request, "Please enter a valid 6-digit code.")
    else:
        form = VerificationCodeForm()

    return render(request, "core/verify_email.html", {'form': form})

def vendor_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # 1) Find the user by email
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return render(request, 'core/vendor_login.html')

        # 2) Check password
        if not user.check_password(password):
            messages.error(request, "Invalid password.")
            return render(request, 'core/vendor_login.html')

        # 3) Check that this user has a Vendor profile
        if not Vendor.objects.filter(user=user).exists():
            messages.error(request, "This account is not registered as a vendor.")
            return render(request, 'core/vendor_login.html')

        # 4) All good—log them in
        login(request, user)
        return redirect('core:vendor_dashboard')

    # GET: just show the login form
    return render(request, 'core/vendor_login.html')

def product_review(request, p_id):
    logger.debug(f"Accessing product_review for p_id: {p_id}")
    product = get_object_or_404(Product, p_id=p_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Your review has been submitted.')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('core:single_shop', product_id=p_id)

@login_required
def vendor_dashboard(request):
    logger.debug(f"Accessing vendor_dashboard for user: {request.user}")
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(vendor=vendor)
        certificates = vendor.certificates.all() if hasattr(vendor, 'certificates') else []
    except Vendor.DoesNotExist:
        messages.error(request, "You are not associated with a vendor profile.")
        return redirect('core:vendor_signup')

    product_form = ProductForm()
    images_form = ProductImagesForm()
    context = {
        'vendor': vendor,
        'products': products,
        'certificates': certificates,
        'product_form': product_form,
        'images_form': images_form,
    }
    return render(request, 'core/vendor_dashboard.html', context)

@login_required
def vendor_add_product(request):
    logger.debug(f"Accessing vendor_add_product for user: {request.user}")
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, "You are not associated with a vendor profile.")
        return redirect('core:vendor_signup')

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        images_form = ProductImagesForm(request.POST, request.FILES)

        if product_form.is_valid() and images_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.vendor = vendor
            product.save()
            product_form.save_m2m()

            images = request.FILES.getlist('images')
            for image in images:
                Product_Images.objects.create(product=product, images=image)

            messages.success(request, 'Product added successfully!')
            return redirect('core:vendor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        product_form = ProductForm()
        images_form = ProductImagesForm()

    return render(request, 'core/vendor_dashboard.html', {
        'product_form': product_form,
        'images_form': images_form,
        'vendor': vendor,
        'certificates': vendor.certificates.all() if hasattr(vendor, 'certificates') else [],
        'products': Product.objects.filter(vendor=vendor),
    })

@login_required
def vendor_edit_product(request, p_id):
    logger.debug(f"Accessing vendor_edit_product for p_id: {p_id}")
    try:
        vendor = Vendor.objects.get(user=request.user)
        product = get_object_or_404(Product, p_id=p_id, vendor=vendor)
    except Vendor.DoesNotExist:
        messages.error(request, "You are not associated with a vendor profile.")
        return redirect('core:vendor_signup')

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        images_form = ProductImagesForm(request.POST, request.FILES)

        if product_form.is_valid() and images_form.is_valid():
            product = product_form.save()
            product_form.save_m2m()

            images = request.FILES.getlist('images')
            if images:
                Product_Images.objects.filter(product=product).delete()
                for image in images:
                    Product_Images.objects.create(product=product, images=image)

            messages.success(request, 'Product updated successfully!')
            return redirect('core:vendor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        product_form = ProductForm(instance=product)
        images_form = ProductImagesForm()

    return render(request, 'core/vendor_dashboard.html', {
        'product_form': product_form,
        'images_form': images_form,
        'vendor': vendor,
        'certificates': vendor.certificates.all() if hasattr(vendor, 'certificates') else [],
        'products': Product.objects.filter(vendor=vendor),
        'edit_mode': True,
    })