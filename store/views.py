from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
# Create your views here.


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()   
        cartItems = order.get_cart_items()
        print("cart total is : ",order.get_cart_total)
        print(cartItems)
    else: 
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        cartItems = order['get_cart_items']

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
    else: 
        items = []
        order = {
            'get_cart_total':0,
            'get_cart_items':0,   
            'shipping': False,
            }

    context = {
    "items" : items,
    "order": order,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else: 
        items = []
        order = {
            'get_cart_total':0,
            'get_cart_items':0,            
            }
    context = {"items" : items, "order": order, 'shipping': False}

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


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    print(transaction_id)
    data = json.loads(request.body)

    if request.user.is_authenticated: 
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
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
    else:
        print("user is not logged in ... ")

    return JsonResponse('Payment complete.... ', safe=False)
