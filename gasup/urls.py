"""gasup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from hosting.views import *
from hosting.models import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('', product_view, name='products'),
    path('ajax/', ajaxview, name='ajax'),
    path('activate/<uidb64>/',ActivateAccountView,name='activate'),
    path('signup/', signup_view, name='signup'),
    path('allorders/', all_orders, name='allorders'),
    path('verify_payment/<str:id>/', verify_payment, name='verify_payment'),
    path('student/', student, name='student'),
    path('checkout/', Checkout, name='checkout'),
    #path('customer/<uidb64>/', customer_view, name='customer'),
    path('customer/', customer_view, name='customer'),
    path('ordersummary/',order_summary, name='ordersummary'),
    path('payments/<str:id>/',payments, name='payments'),
    path('ordersummaryAnonymous/',order_summary_for_Anonymous, name='ordersummaryAnonymous'),
    path('orderdetail/<int:id>/',  order_detail, name='orderdetail'),
    path('addtocart/<int:id>/',add_to_cart, name='addtocart'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('productdetail/<int:id>/', product_detail_view, name='productdetail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)