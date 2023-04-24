from django.contrib import admin

# Register your models here.

from .models import Invoice, Item, ItemDetail, Customer

admin.site.register(Invoice)
admin.site.register(Item)
admin.site.register(ItemDetail)
admin.site.register(Customer)