from django.db import models
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _


class Customer(models.Model):
    TYPE_CHOICES = [('business', 'Business'), ('individual', 'Individual')]

    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    billing_address = models.TextField()
    shipping_address = models.TextField()

    def __str__(self):
        return self.name


class Invoice(models.Model):

    class status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        DRAFT = 'draft', _('Draft')
        COMPLETE = 'complete', _('Complete')

    class payment_status(models.TextChoices):
        PAID = 'paid', _('Paid')
        UNPAID = 'unpaid', _('Unpaid')

    user = models.ForeignKey(CustomUser,
                             related_name="invoices",
                             on_delete=models.CASCADE)

    customer = models.ForeignKey(Customer,
                                 related_name="invoices",
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
    sent_times = models.IntegerField(default=0)
    status = models.CharField(max_length=10,
                              choices=status.choices,
                              default=status.ACTIVE)
    payment_status = models.CharField(max_length=10,
                                      choices=payment_status.choices,
                                      default=payment_status.UNPAID)
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
