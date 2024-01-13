from typing import Any
import pyotp
from .utils import send_otp
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegisterForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.password_validation import validate_password
from datetime import datetime
import time
from random import uniform


@csrf_protect
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email address.")
                return redirect("register")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("register")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect("register")

            try:
                validate_password(password, user=User)
            except ValidationError as e:
                for error in e:
                    messages.error(request, error)
                return redirect("register")

            user = User(
                username=username, email=email, password=make_password(password)
            )
            user.save()

            messages.success(request, "Your account has been created! Please log in.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    context = {"form": form}
    return render(request, template_name="users/register.html", context=context)


class LogoutView(auth_views.LogoutView):
    template_name = "users/logout.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        messages.success(request, "Successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        time.sleep(uniform(0.0, 1))
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session["username"] = username
            send_otp(request)

            return redirect("otp")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, template_name="users/login.html", context={"form": form})


@csrf_protect
def otp_view(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        username = request.session["username"]

        valid_untill = datetime.fromisoformat(request.session["valid_until"])
        otp_secret = request.session["otp_secret"]
        if otp_secret is None and valid_untill is None:
            messages.error(request, "OTP expired.")
            return redirect("login")

        if datetime.now() < valid_untill:
            totp = pyotp.TOTP(otp_secret, interval=60)
            if totp.verify(otp):
                user = get_object_or_404(User, username=username)
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                messages.success(request, "Successfully logged in.")
                return redirect("profile")
            else:
                messages.warning(request, "Invalid OTP.")
        else:
            messages.info(request, "OTP expired.")
        return redirect("login")

    return render(request, template_name="users/otp.html")
