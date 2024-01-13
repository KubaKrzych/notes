from django.urls import path
from . import views

# Create your views here.
urlpatterns = [
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "register/",
        views.register,
        name="register",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "login/otp",
        views.otp_view,
        name="otp",
    ),
]
