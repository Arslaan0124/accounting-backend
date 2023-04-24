from django.db import models
from users.models import CustomUser


class Customer(models.Model):
    TYPE_CHOICES = [('business', 'Business'), ('individual', 'Individual')]

    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('draft', 'Draft')]

    user = models.ForeignKey(CustomUser,
                             related_name="invoices",
                             on_delete=models.CASCADE)

    customer = models.ForeignKey(Customer,
                                 related_name="invoice",
                                 on_delete=models.CASCADE)
    order_number = models.CharField(max_length=255)
    date = models.DateField()
    due_date = models.DateField()
    billing_address = models.TextField()
    shipping_address = models.TextField()
    remarks = models.TextField()
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment = models.DecimalField(max_digits=10, decimal_places=2)
    customer_notes = models.TextField()
    terms_and_conditions = models.TextField()
    file_upload = models.FileField(blank=True, null=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default=STATUS_CHOICES[0])
    created_at = models.DateTimeField(auto_now_add=True)


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    stock_on_hand = models.IntegerField()
    unit = models.CharField(max_length=50)
    hsn_code = models.CharField(max_length=50)
    created_source = models.CharField(max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)


class ItemDetail(models.Model):
    invoice = models.ForeignKey(Invoice,
                                related_name='items',
                                on_delete=models.CASCADE)
    item = models.ForeignKey(Item,
                             related_name='item_details',
                             on_delete=models.CASCADE)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
