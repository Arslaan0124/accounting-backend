# Generated by Django 4.2 on 2023-04-27 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_invoice_paymnet_status_alter_invoice_customer_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='paymnet_status',
            new_name='payment_status',
        ),
    ]