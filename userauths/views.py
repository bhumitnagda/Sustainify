# userauths/views.py

import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from core.utils import send_verification_email
from userauths.forms import UserRegisterForm
from userauths.models import UserProfile

User = get_user_model()

def register_view(request):
    """
    1) Create new customer (user_type=1) but leave is_active=False
    2) Create a UserProfile (auto-generates the 6-digit code)
    3) Email that code
    4) Log them in and redirect to the shared verify_email view
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # 1) build inactive user
            user = form.save(commit=False)
            user.user_type = 1
            user.is_active = False
            user.save()

            # 2) generate a profile (and code)
            profile = UserProfile.objects.create(user=user)
            code = profile.verification_code

            # 3) email them the code
            send_verification_email( user, code)

            # 4) auto-login so they can get to /verify-email/
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            messages.success(request,
                "Welcome! We’ve sent a 6-digit code to your email. "
                "Please enter it now to activate your account."
            )
            return redirect('core:verify_email')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, "userauths/sign-up.html", {'form': form})


def login_view(request):
    """
    Standard login, but if the customer isn’t yet active (hasn't verified),
    send them to the same verify_email page.
    """
    if request.user.is_authenticated:
        return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.warning(request, "Invalid email or password.")
            return render(request, "userauths/sign-in.html")

        if not user.is_active:
            # not yet verified → re-send code and push to verify
            profile, _ = UserProfile.objects.get_or_create(user=user)
            code = profile.verification_code
            send_verification_email( user, code)

            # log them in so they can access /verify-email/
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.warning(request,
                "Your email isn’t verified yet. We’ve resent your 6-digit code—"
                "please check your inbox and enter it now."
            )
            return redirect('core:verify_email')

        # fully active
        login(request, user)
        messages.success(request, "Welcome back! You are now logged in.")
        return redirect("core:index")

    return render(request, "userauths/sign-in.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("userauths:sign-in")
