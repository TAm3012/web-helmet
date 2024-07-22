from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('payment/', views.payment, name='payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('update_item/', views.updateItem, name="update_item"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('search/', views.search, name="search"),
    path('category/', views.category, name="category"),
    path('detail/', views.detail, name="detail"),
    path('chatbot/', views.chatbot_view, name="chatbot"),
    path('error/', views.error_page, name='error_page'),
]
