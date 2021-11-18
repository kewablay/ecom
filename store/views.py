from django.shortcuts import render,redirect 
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


from .models import *
from django.http import JsonResponse
import json
import datetime

from . utils import cookieCart, guestOrder
# Create your views here.

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
                       
        if user is not None:
            login(request, user)
            active_user = request.user            
            return redirect('store')
    
    context = {}
    return render(request, 'store/login.html',context)


def registerPage(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST.get('username')
            user = User.objects.get(username=username)
            customer = Customer.objects.create(user=user)       
            messages.success(request, 'Account created successfully')
            return redirect('login')
            
    
    context = {'form': form}
    return render(request, 'store/register.html',context)


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()   
        cartItems = order.get_cart_items()
        print("cart total is : ",order.get_cart_total)
        print(cartItems)
    else: 
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        # print(customer)
        order = Order.objects.filter(customer=customer,complete=False).first()
        if not order:
            order = Order.objects.create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items()
    else: 
       cookieData = cookieCart(request)
       cartItems = cookieData['cartItems']
       order = cookieData['order']
       items = cookieData['items']

    context = {
    "items" : items,
    "order": order,
    "cartItems": cartItems
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items()
    else: 
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    context = {"items" : items, "order": order, 'shipping': False,"cartItems": cartItems}
    return render(request, 'store/checkout.html', context)


def UpdateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)    
    # print('Action:', action)
    # print('productId:', productId)
    if action == 'add':  
        orderItem.quantity = (orderItem.quantity + 1)
        # print(orderItem.order)
        # print(orderItem.quantity)
        orderItem.save()
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    print(transaction_id)
    data = json.loads(request.body)

    if request.user.is_authenticated: 
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
       customer, order = guestOrder(request, data)
            
    total = float(data['userFormData']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total: 
        order.complete = True
    order.save()
    
    if order.shipping == True: 
        ShippingAddress.objects.create(
            customer = customer,
            order= order, 
            address = data['shippingInfo']['address'],
            country = data['shippingInfo']['country'],
            city = data['shippingInfo']['city'],
            zipcode = data['shippingInfo']['zipcode'],
        )
        
    return JsonResponse('Payment complete.... ', safe=False)
