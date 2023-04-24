# Generated by Django 4.2 on 2023-04-20 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('company_name', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(choices=[('business', 'Business'), ('individual', 'Individual')], max_length=10)),
                ('display_name', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('website', models.URLField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('due_date', models.DateField()),
                ('billing_address', models.TextField()),
                ('shipping_address', models.TextField()),
                ('remarks', models.TextField()),
                ('shipping_charges', models.DecimalField(decimal_places=2, max_digits=10)),
                ('adjustment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_notes', models.TextField()),
                ('terms_and_conditions', models.TextField()),
                ('file_upload', models.FileField(blank=True, null=True, upload_to='')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='core.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_on_hand', models.IntegerField()),
                ('unit', models.CharField(max_length=50)),
                ('hsn_code', models.CharField(max_length=50)),
                ('created_source', models.CharField(max_length=255)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='ItemDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.invoice')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_details', to='core.item')),
            ],
        ),
    ]