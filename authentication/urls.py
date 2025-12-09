from django.urls import URLPattern, path

from .views import SignUp, SignIn, SignOut

urlpatterns: URLPattern = [
    path("register/", SignUp.as_view(), name="register"),
    path("login/", SignIn.as_view(), name="login"),
    path("logout/", SignOut.as_view(), name="logout"),
]
