from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import *
from .models import Product
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib  import messages
from django.views.decorators.csrf import csrf_exempt
import os
from google.api_core.exceptions import InvalidArgument
from django.conf import settings
import paypalrestsdk
from .models import Order, OrderItem
# Create your views here.


# Import cấu hình PayPal
import app.paypal_config
def error_page(request):
    return render(request, 'app/error.html')

def payment(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)

        # Tạo một PayPal Payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payment/execute/'),
                "cancel_url": request.build_absolute_uri('/checkout/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Order {}".format(order_id),
                        "sku": "order_{}".format(order_id),
                        "price": str(order.get_cart_total),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(order.get_cart_total),
                    "currency": "USD"
                },
                "description": "Payment for Order {}".format(order_id)
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return redirect(approval_url)
        else:
            return HttpResponse("Error creating PayPal payment")

    return render(request, 'app/payment.html')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Xóa các mặt hàng trong giỏ hàng sau khi thanh toán thành công
        transaction = payment.transactions[0]
        sku = transaction.item_list.items[0].sku
        order_id = sku.split("_")[-1]
        order = Order.objects.get(id=order_id)
        order.complete = True
        order.save()

        # Xóa các mặt hàng trong giỏ hàng của người dùng
        order_items = order.orderitem_set.all()
        for item in order_items:
            item.delete()

        return render(request, 'app/payment_success.html')
    else:
        return HttpResponse("Payment failed")
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # Save shipping information
        shipping_address, created = ShippingAddress.objects.get_or_create(
            customer=customer,
            order=order,
            defaults={'address': address, 'mobile': phone, 'city': city, 'state': state}
        )

        return redirect('payment')

    categories = Category.objects.filter(is_sub=False)
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'user_not_login': user_not_login, 'user_login': user_login, 'categories': categories}
    return render(request, 'app/checkout.html', context)

def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items =[] 
        order = {'get_cart_items' : 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    context= {'items':items, 'order':order, 'cartItems': cartItems,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories}
    return render(request, 'app/detail.html',context) 
def category(request):
    categories = Category.objects.filter(is_sub = False)
    active_category = request.GET.get('category','')
    if active_category:
        products = Product.objects.filter(category__slug = active_category)
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[] 
        order = {'get_cart_items' : 0, 'get_cart_total': 0}        
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    context = {'categories': categories, 'products': products, 'active_category':active_category, 'user_not_login' : user_not_login, 'user_login' :user_login, 'cartItems':cartItems }
    return render(request, 'app/category.html', context)
def search(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        keys = Product.objects.filter(name__contains = searched)
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items =[] 
        order = {'get_cart_items' : 0, 'get_cart_total': 0}        
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    return render(request, 'app/search.html', {"searched": searched, "keys": keys, 'products': products, 'cartItems':cartItems,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories})

def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        user_not_login = "hidden"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    context= {'form':form,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories': categories}
    return render(request,'app/register.html', context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: messages.info(request,'user or password not correct!')
        user_not_login = "hidden"
        user_login = "show" 
    else:
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    context= {'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories}
    return render(request,'app/login.html', context)
def logoutPage(request):
    logout(request)
    return redirect('login')
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items =[] 
        order = {'get_cart_items' : 0, 'get_cart_total': 0}        
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    context= {'products': products, 'cartItems':cartItems,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories}
    return render(request, 'app/home.html',context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items =[] 
        order = {'get_cart_items':0,'get_cart_total':0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    context= {'items':items, 'order':order, 'cartItems':cartItems,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories}
    return render(request, 'app/cart.html',context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
    if action == 'add':
        orderItem.quantity +=1
    elif action == 'remove':
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity <=0:
        orderItem.delete()
    
    return JsonResponse('added',safe = False)

@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = get_chatbot_response(message)  # Hàm này xử lý và trả lời tin nhắn
        return JsonResponse({'response': response})
    return JsonResponse({'response': 'Only POST method is allowed.'})

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'path_to_your_service_account_json_file.json'
DIALOGFLOW_PROJECT_ID = 'your-project-id'
DIALOGFLOW_LANGUAGE_CODE = 'vi','en'
SESSION_ID = 'current-user-id'

def get_chatbot_response(message):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=message, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
        return response.query_result.fulfillment_text
    except InvalidArgument:
        raise