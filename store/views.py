from django.shortcuts import render
from .models import *
# Create your views here.


def store(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        # print(customer)
        order = Order.objects.filter(customer=customer,complete=False).first() # or .last() based on your requirements
        if not order:
            order = Order.objects.create(customer=customer,complete=False)
        print(order)
        items = order.orderitem_set.all()
        print(items)
    # else: 
    #     items = []

    context = {"items" : items}
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)