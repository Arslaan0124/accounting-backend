# Generated by Django 4.2 on 2023-04-27 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_paymnet_status_invoice_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(choices=[('P', 'Paid'), ('UP', 'Unpaid')], default='P', max_length=10),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('AC', 'Active'), ('DR', 'Draft'), ('CO', 'Complete')], default='AC', max_length=10),
        ),
    ]
