from django.urls import path
from . import views 

urlpatterns = [
    path("", views.store, name='store'),
    path("cart/", views.cart, name='cart'),
    path("checkout/", views.checkout, name="checkout"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("update_item/", views.UpdateItem, name='update_item'),
    path("process_order/", views.processOrder, name='process_order'),
]