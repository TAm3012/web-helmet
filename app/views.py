from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import *
from .models import Product
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib  import messages
from django.views.decorators.csrf import csrf_exempt
import os
from google.api_core.exceptions import InvalidArgument
from django.conf import settings
import paypalrestsdk
from .models import Order, OrderItem, ShippingAddress, Category
# Create your views here.
# Import cấu hình PayPal
import app.paypal_config
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox hoặc live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

@login_required
def checkout(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    user_not_login = "hidden"
    user_login = "show"

    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # Lưu thông tin vận chuyển
        shipping_address, created = ShippingAddress.objects.get_or_create(
            customer=customer,
            order=order,
            defaults={'address': address, 'mobile': phone, 'city': city, 'state': state}
        )

        # Giảm số lượng sản phẩm và ẩn sản phẩm nếu hết hàng
        for item in items:
            product = item.product
            if product.quantity >= item.quantity:
                product.quantity -= item.quantity
                product.save()
                if product.quantity <= 0:
                    # Ẩn sản phẩm nếu hết hàng
                    product.visible = False  # Bạn cần thêm trường 'visible' trong model Product
                    product.save()
            else:
                messages.error(request, f"Không đủ hàng cho sản phẩm {product.name}.")
                return redirect('cart')

        # Đánh dấu đơn hàng là hoàn thành
        order.complete = True
        order.save()

        messages.success(request, "Đơn hàng của bạn đã được xử lý thành công!")
        return redirect('home')

    categories = Category.objects.filter(is_sub=False)
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories
    }
    return render(request, 'app/checkout.html', context)


@login_required
def create_payment(request):
    customer = request.user
    order = Order.objects.get(customer=customer, complete=False)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/execute_payment/'),
            "cancel_url": request.build_absolute_uri('/checkout/')
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Order {}".format(order.id),
                    "sku": "order_{}".format(order.id),
                    "price": str(order.get_cart_total),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(order.get_cart_total),
                "currency": "USD"
            },
            "description": "Payment for Order {}".format(order.id)
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return HttpResponse("Error creating PayPal payment")

@login_required
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        transaction = payment.transactions[0]
        sku = transaction.item_list.items[0].sku
        order_id = sku.split("_")[-1]
        order = Order.objects.get(id=order_id)
        order.complete = True
        order.save()

        order_items = order.orderitem_set.all()
        for item in order_items:
            item.delete()

        return redirect('payment_success')
    else:
        return HttpResponse("Payment failed")

@login_required
def payment_success(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
        print(user_not_login)
        print(user_login)
    else:
        items =[] 
        order = {'get_cart_items' : 0, 'get_cart_total': 0}        
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    context= {'products': products, 'cartItems':cartItems,'user_not_login' : user_not_login, 'user_login' :user_login, 'categories':categories}
    return render(request, 'app/payment_success.html', context)
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
    searched = ""
    keys = Product.objects.none()  
    if request.method == "POST":
        searched = request.POST.get("searched", "")
        keys = Product.objects.filter(name__icontains=searched)  # Tìm kiếm không phân biệt chữ hoa chữ thường

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

    categories = Category.objects.filter(is_sub=False)
    
    context = {
        "searched": searched,
        "keys": keys,
        'products': keys,  # Chỉ trả về các sản phẩm tìm thấy
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories
    }
    return render(request, 'app/search.html', context)

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
    
    products = Product.objects.filter(visible=True)
    categories = Category.objects.filter(is_sub=False)

    context = {
        'products': products, 
        'cartItems': cartItems, 
        'user_not_login': user_not_login, 
        'user_login': user_login, 
        'categories': categories
    }
    return render(request, 'app/home.html', context)

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
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        if product.quantity >= 1:
            order_item.quantity += 1
            product.reduce_stock(1)  # Giảm số lượng sản phẩm
        else:
            messages.error(request, "Không đủ hàng để thêm vào giỏ.")
    elif action == 'remove':
        order_item.quantity -= 1
        product.quantity += 1  

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)


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
def search_ajax(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
        results = []
        for product in products:
            results.append({
                'name': product.name,
                'price': product.price,
                'image_url': product.ImageURL,
            })
        return JsonResponse({'products': results})
    else:
        return JsonResponse({'products': []})