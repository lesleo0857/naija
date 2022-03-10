from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http import Http404,request
from .models import *



def authenticate_user(view):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated :  # this would make sure that you cant goto signup page while u are signed in
            #return redirect('customer',request.user.customer.id)
            return redirect('customer')
        else:  # if u are not signed in then you can acces the signup page
            return view(request,*args,**kwargs)
    return wrapper_func


def anonymous_user(view):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_anonymous :
            print('anonymous')
            productlist = Products.objects.all()
            context = {}
            return render(request, 'ordersummary.html', context)

    return wrapper_func