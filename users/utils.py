from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings


def send_totp_email(user, token):
    send_mail(
        "Your One-Time Password",
        f"Your OTP is {token}",
        "",
        [user.email],
        fail_silently=False,
    )


def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    valid_until = datetime.now() + timedelta(minutes=1)

    request.session["otp_secret"] = totp.secret
    request.session["valid_until"] = str(valid_until)
    username = request.session["username"]
    user = get_object_or_404(User, username=username)
    if settings.DEBUG:
        print(f"OTP for {user.username} is {otp}")
    send_totp_email(user, otp)
