from rest_framework import serializers
from .models import Invoice, ItemDetail, Item, Customer, Address
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


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            'id', 'country', 'address', 'city', 'state', 'zip_code', 'phone'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    billing_address = AddressSerializer()
    shipping_address = AddressSerializer()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'company_name', 'type', 'display_name', 'email',
            'phone', 'website', 'created_at', 'billing_address',
            'shipping_address'
        ]

    def create(self, validated_data):
        billing_address_data = validated_data.pop('billing_address')
        shipping_address_data = validated_data.pop('shipping_address')

        billing_address = Address.objects.create(**billing_address_data)
        shipping_address = Address.objects.create(**shipping_address_data)

        customer = Customer.objects.create(billing_address=billing_address,
                                           shipping_address=shipping_address,
                                           **validated_data)

        return customer


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
