from django.shortcuts import render,redirect
from .models import *
import _struct

#from pypaystack import Transaction, Customer, Plan

from .forms import *
import base64
from django.core.exceptions import ObjectDoesNotExist
import binascii
from django.views.generic import View
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.safestring import SafeString
from django.utils.encoding import is_protected_type,force_str,smart_str,force_bytes,force_text,smart_bytes,smart_text,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage,send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import get_object_or_404,get_list_or_404,_get_queryset
from django.http import Http404,request,JsonResponse
import json
from django.http.response import JsonResponse
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.utils import timezone
from .decorator import *
from django.conf import settings
# Create your views here.


def product_view(request):
    if request.user.is_anonymous:
        productlist = Products.objects.all()
        context = {'productlist': productlist}
        return render(request, 'index.html', context)
    section = Section.objects.all()
    category  = Category.objects.all()
    order = Order.objects.filter(user=request.user, ordered=False)
    orderItem = OrderItem.objects.filter(order=order[0].pk)

    productlist = Products.objects.all()
    context = {'productlist': productlist,
               'OrderItems': orderItem,'category':category,
               'section':section
               }
    return render(request, 'index.html', context)


def product_detail_view(request,id):
    product_detail = Products.objects.get(id = id)
    context = {'product_detail':product_detail}
    return render(request,"product-detail.html",context)


def payments(request,id):
    # here request is made to paystack with price parameter   the price should
    # be in a disabled input..   also if checkout.payment-option == P
    # then request should e to paystack
    try:
        q = Order.objects.get(user=request.user,ordered=False)
        o = OrderItem.objects.filter(order_id=q.id)

        x = []
        z = []

        r = int()
        b = int()
        for i in o:
            v = i.realprice()
            x.append(v)
            print(x)
            r = sum(x)
            print(r)
        for c in o:
            j = c.saved_price()
            z.append(j)
            print(z)
            b = sum(z)
            print(b)


        paymentForm = PaymentForm(request.POST)
        paystack = settings.PAYSTACK_SECRET_KEY
        paystack_pk = settings.PAYSTACK_PUBLIC_KEY


        if request.method == 'POST':
            PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_SECRET_KEY
            print(PAYSTACK_PUBLIC_KEY)
            data = {'email': f'{request.user.customer.email}', 'amount': f'{r}'}
            print(f'{payment.email}')
            # url = f'https://api.paystack.co/transaction/verify/{payment.ref}'
            headers = {'Authorization': f'Bearer {PAYSTACK_PUBLIC_KEY}',
                       'content-Type': 'application/json'}
            response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
            print(response.status_code, response.text, response.json()['data']['reference'])



        # if request.method == 'POST':
        #     paymentForm = PaymentForm(request.POST)
        #     if paymentForm.is_valid():
        #         amount= paymentForm.cleaned_data.get('amount')
        #         print(amount)
        #         email = paymentForm.cleaned_data.get('email')
        #         a = Payment.objects.create(user=request.user,amount=amount,
        #                                email=email)
        #         print(a.user)
        #         a.ref = a.saver()
        #         a.save()
        #         print(a.ref)
        #         #context = {'paymentForm': paymentForm,'s': id, 'paystack': paystack,'a': a,'b':b}
        #         return redirect('verify_payment',a.id)
        #     else:
        #         print('not valid')
        context = {'paymentForm': paymentForm, 'o': o,
                   "r": r, "b": b,"paystack":paystack,
                   "paystack_pk":paystack_pk,}
        return render(request, "payments.html", context)

    except:
        ObjectDoesNotExist

        context = {}
        return render(request,"payments.html",context)

@login_required(login_url='login')
def Checkout(request):
    if request.method == "POST":
        print(request.POST)
    form = Checkoutform(request.POST )
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False, )
    if order_qs:
        billing_address = Checkoutt.objects.filter(user=request.user)
        if billing_address:
            print('bill exixts')


            return redirect('payments', billing_address[0].Payment_options)


        else:
            form = Checkoutform(request.POST)
            if form.is_valid():
                email = request.user.email
                Address = form.cleaned_data.get('Address')
                country = form.cleaned_data.get('country')
                state = form.cleaned_data.get('state')
                Zip= form.cleaned_data.get('Zip')
                payment_options = form.cleaned_data.get('payment_options')
                billing_address = Checkoutt.objects.create(user=request.user,
                                                              Email=email,
                                                              Address=Address,
                                                              Country=country,
                                                              state=state,
                                                              Zip=Zip,
                                                              Payment_options=payment_options,
                                                              )
                billing_address.save()
                print(billing_address)
                a = Order.objects.get(user=request.user,
                                        ordered=False,
                                      )
                a.Billing_address = billing_address
                print(a.Billing_address)
                a.save()
                return redirect('payments',a.Billing_address.Payment_options)
            else:
                print('not valid')
    else:
        messages.error(request,'you dont have an order')
    context = {'form': form}
    return render(request, 'checkout.html', context)

def verify_payment(request,id):
    print(id)
    # payment = Payment.objects.get(user=request.user,id=id)
    # print(payment.ref)
    PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_SECRET_KEY
    print(PAYSTACK_PUBLIC_KEY)
    url = f'https://api.paystack.co/transaction/verify/{id}'
    response = requests.get(url, headers={'Authorization': f'Bearer {PAYSTACK_PUBLIC_KEY}'})
    print(response.status_code, response.text)
    return response

    # data = {'email':f'{payment.email}','amount':f'{payment.amount}'}
    # print(f'{payment.email}')

    #url = f'https://api.paystack.co/transaction/verify/{payment.ref}'
    # headers = {'Authorization':f'Bearer {PAYSTACK_PUBLIC_KEY}',
    #             'content-Type':'application/json'}
    # response = requests.post('https://api.paystack.co/transaction/initialize',json=data,headers=headers)
    # print(response.status_code, response.text, response.json()['data']['reference'])
    # #print(res.text,res.status_code)

    # res = response.json()['data']['reference']
    # url = f'https://api.paystack.co/transaction/verify/{res}'
    # response = requests.get(url,headers= {'Authorization':f'Bearer {PAYSTACK_PUBLIC_KEY}'})
    # print(response.status_code,response.text)
    # return response

    #else:
        #response_data = response.json()
        #return response_data['status'],response_data['message']



user = {}
@authenticate_user
def signup_view(request,**kwargs):
    form = createuserform()
    if request.method == "POST":
        form = createuserform(request.POST)
        if form.is_valid():

            print(form.cleaned_data)
            user = form.save()
            user.is_active=False
            user.save()
            print(user.email)
            uid = base64.encode(force_bytes(user.pk) )


            current_site=get_current_site(request)
            email_subject = 'Activate your account'
            message = render_to_string('activate.html',
                {
                    'user':user,
                    'domain':current_site.domain,
                    'uid':uid

                }

            )
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER ,
                [user.email]
                )
            email_message.send()
           # print(user.username)
            #Customer.objects.create(name=user.username,user = user,email=user.email)  # with this method the Customer name wont change if the User's name is updated  it is better to use django signals
           # print(user)

           # username = form.cleaned_data.get('username')
          #  group = Group.objects.get(name="Customers")  #Group is the user group in the admin
           # user.groups.add(group)    #add form.save to a group named customer
           # messages.success(request,'signup successful'+ " " + username)# it is stored as a value  no need to assign a  value to the messages. no need to pass it through context
           # Customer.objects.create(user=user, name=user.username)
          #  return redirect('login')
    #a = form.errors
    context = {'form':form}
    return render(request,'signup.html',context)


def ActivateAccountView(request,uidb64):

    print(uidb64)
    uid = base64.decodebytes(force_bytes(uidb64))
    print(str (uid ))
    try:
        uid=uidb64.decode(base64)
        print(uid)
        user = User.objects.get(pk=1)

    except Exception as identifier:
        user= None
    # user = User.objects.get(pk=uidb64)
    # if user is not None :
    #     username = user.username
    #     group = Group.objects.get(name="Customers")
    #     user.groups.add(group)
    #     messages.add_message(request, messages.INFO, 'account activated succesfully')
    #     Customer.objects.create(user=user, name=user.username)
    #     user.is_active=True
    #     user.save()
    #     return redirect('login')
    return render(request,'actvation_failed.html',status=401)

@authenticate_user
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(username,password)
        if user is not None:  # not none    means the user name is there in database                login(request, username)

            login(request, user)
            print(request.user.customer.pk)
            d = str(request.user.customer.pk)
            print(d)
            uidb64 =base64.b64encode(d.encode('utf-8', errors='ignore'))
            print(uidb64)
            print(type(uidb64))
            print('u')
            return redirect('customer')
        else:
            messages.info(request, "Username OR Password is incorrect")  # you dont need to pass through context
    context = {}
    return render(request, 'login.html', context)

def student(request):
    #response = requests.get('http://127.0.0.1:8000/student')
    #print(response.content)
    student= Student_subject.objects.filter(student_id=1)
    context = {'student': student, }
    return render(request, 'student.html', context)

def ajaxview(request):
    form = ajaxform()
    context = {'form':form }
    return render(request, 'ajax.html', context)

@login_required(login_url='login')
def customer_view(request):
    a = request.user.customer.id

    customer = Customer.objects.get(id=a)
    print(customer.name)
    productlist = Products.objects.all()
    paginator = Paginator(productlist,2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    order = Order.objects.filter(user=request.user,ordered=False)
    if order:
        orderItem = OrderItem.objects.filter(order=order[0].pk)
        context = {'productlist': contacts,
                       "customer":customer,

                      'OrderItems':orderItem,
                   }
        return render(request, 'customer.html', context)
    context = {'productlist': contacts,
               "customer": customer,
               }
    return render(request, 'customer.html', context)



@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')

def all_orders(request):
    global orders
    orders = Order.objects.filter(ordered=False)


    context  = {"orders":orders}
    return render(request, 'allorders.html', context)

def order_detail(request,id):
    order = Order.objects.get(id=id)
    j = OrderItem.objects.filter(order=order)
    h = []
    for i in j:
        h.append(i.realprice())
        f = sum(h)

    context = {"j": j,"order":order,'f':f}
    return render(request, 'orderdetail.html', context)

# decorator for only admin
def order_summary(request):
    o = OrderItem.objects.filter(user=request.user)

    x = []
    z = []

    a = int()
    b = int()
    for i in o:
        v = i.realprice()
        x.append(v)
        print(x)
        a = sum(x)
        print(a)
    for c in o:
        j = c.saved_price()
        z.append(j)
        print(z)
        b = sum(z)
        print(b)

    context = {'o':o,"a":a,"b":b}
    return render(request, 'ordersummary.html', context)


def order_summary_for_Anonymous(request):

    context = {}
    return render(request, 'ordersummary.html', context)



def add_to_cart(request,id):
    # declaring Queryset

    if request.user.is_anonymous:
        print('anonymous')
        productlist = Products.objects.all()
        return redirect('customer')

    if request.method == 'POST':
        qty = request.POST.get('qty')
        print(qty)
        product = get_object_or_404(Products, id=id)
        order_qs = Order.objects.filter(user=request.user,
                                        ordered=False)

        orderitem_qs = OrderItem.objects.filter(user=request.user,
                                                ordered=False,
                                                item=product.id
                                                )
        # check to see iff there iss an Orderqueryset
        if order_qs:
            order = order_qs[0]  # this specifies it is the first  or newest qs
            if orderitem_qs:  # check for orderitem queryset

                orderitem_qs = OrderItem.objects.get(user=request.user,
                                                     ordered=False,
                                                     item_id=product.id)

                orderitem_qs.quantity = qty
                orderitem_qs.save()
                product.quantity = product.quantity - qty
                print(product.quantity)
                product.quantity.save()
                pass
            else:
                messages.info(request, 'item will be added to cart.')
                j = Order.objects.get(user=request.user,
                                      ordered=False,
                                      )
                OrderItem.objects.create(user=request.user,
                                         ordered=False,
                                         item_id=product.id,
                                         order=j,
                                         quantity=1)
                OrderItem.save
        else:
            Order.objects.create(user=request.user,
                                 ordered=False,
                                 ordered_date=timezone.now()
                                 )
            Order.save
            j = Order.objects.get(user=request.user,
                                  ordered=False,

                                  )
            OrderItem.objects.create(user=request.user,
                                     ordered=False,
                                     item_id=product.id,
                                     quantity=1,
                                     order=j)
            OrderItem.save

        return redirect('customer')


    product = get_object_or_404(Products,id=id)
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False )
    orderitem_qs = OrderItem.objects.filter(user=request.user,
                                    ordered=False,
                                    item=product.id
                                 )

    print(request.user)

    #check to see iff there iss an Orderqueryset
    if order_qs:
        order = order_qs[0] # this specifies it is the first queryset
        if orderitem_qs: # check for orderitem queryset

            orderitem_qs = OrderItem.objects.get(user=request.user,
                                            ordered=False,
                                            item_id=product.id)

            orderitem_qs.quantity = orderitem_qs.quantity + 1
            orderitem_qs.save()
            product.quantity = product.quantity - 1
            print(product.quantity)
            product.save()
        else:
            messages.info(request,'item will be added to cart.')
            j = Order.objects.get(user=request.user,
                                  ordered=False,
                                  )
            OrderItem.objects.create(user=request.user,
                                     ordered=False,
                                     item_id=product.id,
                                    order=j,
                                     quantity=1)
            OrderItem.save
    else:
        Order.objects.create(user=request.user,
                              ordered=False,
                              ordered_date= timezone.now()
                              )
        Order.save
        j = Order.objects.get(user=request.user,
                                 ordered=False,

                                 )
        OrderItem.objects.create(user=request.user,
                                 ordered=False,
                                 item_id=product.id,
                                 quantity=1,
                                 order=j)
        OrderItem.save



    return redirect('customer')








