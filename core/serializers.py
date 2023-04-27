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


class ItemDetailListSerializer(ItemDetailSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = ItemDetail
        fields = ('id', 'item')


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
                  'created_at', 'status', 'payment_status', 'billing_address',
                  'shipping_address', 'remarks', 'shipping_charges',
                  'adjustment', 'customer_notes', 'terms_and_conditions',
                  'sent_times', 'file_upload', 'items')
        read_only_fields = ('sent_times', )

    def get_fields(self):
        fields = super().get_fields()

        # Use ItemDetailListSerializer when a list of invoices is requested
        if 'view' in self.context:
            if self.context['view'].action == 'list':
                fields['items'] = ItemDetailListSerializer(many=True)
            else:
                fields['items'] = ItemDetailSerializer(many=True)
        else:
            fields['items'] = ItemDetailSerializer(many=True)

        return fields
