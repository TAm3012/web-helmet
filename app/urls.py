from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name='checkout'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('execute_payment/', views.execute_payment, name='execute_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('update_item/', views.updateItem, name="update_item"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('search/', views.search, name="search"),
    path('category/', views.category, name="category"),
    path('detail/', views.detail, name="detail"),
    path('chatbot/', views.chatbot_view, name="chatbot"),
    path('search_ajax/', views.search_ajax, name='search_ajax'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('account/', views.account, name='account'),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('address/', views.address_list, name='address_list'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),

]
