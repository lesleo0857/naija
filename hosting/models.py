from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.models import User
import base64
import secrets
from .paystack import PayStack
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import is_protected_type,force_str,smart_str,force_bytes,force_text,smart_bytes,smart_text,DjangoUnicodeDecodeError


# Create your models here

class Student(models.Model):
    name = models.CharField(max_length=200, null=True)
    reg_no =  models.IntegerField(null=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    title = models.CharField(max_length=200, null=True)
    unit_load =  models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    semester = models.IntegerField(null=True)


    def __str__(self):
        return self.title

class Student_subject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    grade = models.IntegerField(null=True)

    def __str__(self):
        return self.subject.title + " " + self.student.name

    def subject_grade(self):
        return self.grade * self.subject.unit_load




class Checkoutt(models.Model):
    user = models.ForeignKey(User,null = True,on_delete = models.CASCADE,default=True)
    Email = models.EmailField()
    Address = models.CharField(max_length=200,null=True)

    Country = CountryField(multiple=False)
    state = models.CharField(max_length=200, null=True,blank=False)
    Zip = models.CharField(max_length=200, null=True)
    Payment_options = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.user.username

    def paymenturl(self):
        return reverse('payment', kwargs={"id": self.Payment_options})


class Customer(models.Model):
    PLANS = (('Diamond','Diamond'),('Gold','Gold'),('Silver','Silver'))
    user = models.OneToOneField(User,null = True,on_delete = models.CASCADE,default=True)
    name  = models.CharField(null=True,max_length=200)
    phone = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    created = models.DateTimeField(null=True,auto_now=False,auto_now_add=True)
    plans = models.CharField(max_length=200,choices=PLANS,default= 'PLANS[0]')
    profile_pic = models.ImageField(default="/Koala.jpg/")

    def __str__(self):
        return str(self.user)

    def get_decode(self):
        return str(base64.b64encode(force_bytes(self.pk)))


    def get_absolute_url(self):
        return reverse('customer')    #,kwargs={"uidb64": self.get_decode()})

class Section(models.Model):

    name  = models.CharField(max_length=200,default='appliances')

    def __str__(self):
        return str(self.name)


class Category(models.Model):

    name  = models.CharField(max_length=200,default='appliances')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return str(self.name)


class Brand(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    name = models.CharField( max_length=200,default='appliances')

    def __str__(self):
        return str(self.name)

class Products(models.Model):
    TAGS = (
        ('Indoor', 'Indoor'),
            ('Outdoor', 'Outdoor'),
            ('Beauty','Beauty')
            )
    title  = models.CharField(max_length=200,null=True)
    price = models.FloatField(null=True)
    description = models.TextField(null=True,blank=True)
    discount =  models.FloatField(blank=True,null=True)
    quantity = models.IntegerField(null=True, default='0')
    rating = models.IntegerField(null=True, default='0')
    tag = models.CharField(max_length=200,choices=TAGS,default= 'TAGS[0]')
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    profile_pic = models.ImageField(blank=True)
    def __str__(self):
        return str(self.title)

    def add_to_cart_url(self):
        return reverse('addtocart',kwargs={"id":self.id})

    def get_absolute_url(self):
        return reverse('productdetail',kwargs={"id":self.id})



class Order(models.Model):
    STATUS = (('delivered','delivered'),('pending','pending'),('out for delivery','out for delivery'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(null=True)
    ordered = models.BooleanField(default=False)
    Billing_address = models.ForeignKey(Checkoutt, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.user)

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Products,null=True,on_delete=models.SET_NULL)
    quantity = models.IntegerField(null=True,default='0')
    ordered = models.BooleanField(default=False)
    order = models.ForeignKey(Order,null=True,on_delete=models.SET_NULL)


    def __str__(self):
        return str(str(self.user) + ' ' + str(self.item))


    def realprice(self):
        if self.item.discount:
            j =self.item.price - self.item.discount
            return j * self.quantity
        return self.item.price * self.quantity

    def saved_price(self):
        if self.item.discount:
            total_discount = self.item.discount * self.quantity
            return total_discount
        return self.realprice()

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True)
    ref = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self,*args,**kwargs) -> str:
        return f"Payment;{self.amount}"

    def saver(self,*args,**kwargs):
        if not self.ref:
            ref = secrets.token_urlsafe(self.pk)
            object_with_similar_ref = Payment.objects.filter(ref = ref)

            if not object_with_similar_ref:
                self.ref = ref
                return self.ref

    def amount_value(self):
        return self.amount*100

