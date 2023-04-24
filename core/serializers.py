from rest_framework import serializers
from .models import Invoice, ItemDetail, Item, Customer
from rest_framework import serializers
from users.serializers import UserSerializer


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'


class ItemDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = ItemDetail
        fields = ('id', 'item', 'quantity', 'rate', 'discount', 'tax')


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemDetailSerializer(many=True)
    customer = CustomerSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = ('id', 'user', 'customer', 'order_number', 'date', 'due_date',
                  'created_at', 'status', 'billing_address',
                  'shipping_address', 'remarks', 'shipping_charges',
                  'adjustment', 'customer_notes', 'terms_and_conditions',
                  'file_upload', 'items')

    # def create(self, validated_data):
    #     print(validated_data)
    #     item_details_data = validated_data.pop('items')
    #     customer_id = validated_data.pop('customer')
    #     customer = Customer.objects.get(id=customer_id)
    #     invoice = Invoice.objects.create(customer=customer, **validated_data)
    #     for item_detail_data in item_details_data:
    #         item_data = item_detail_data.pop('item')
    #         item = Item.objects.get(pk=item_data['id'])
    #         item_detail = ItemDetail.objects.create(invoice=invoice,
    #                                                 item=item,
    #                                                 **item_detail_data)
    #     return invoice
