from django import template
from hosting.views import *

register = template.Library()

@register.filter
def category(value):
    print(value)
    c = Category.objects.filter(section_id=value)
    print(dir(c))
    return c

@register.filter
def brand(value):
    print(value)
    c = Brand.objects.filter(category_id=value)
    print(dir(c))
    return c

@register.filter
def product(value):
    print(value)
    c = Products.objects.filter(Brand_id=value)
    print(dir(c))
    return c
