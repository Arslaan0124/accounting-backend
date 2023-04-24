from rest_framework import viewsets, status
from .models import Invoice, ItemDetail, Item, Customer
from .serializers import InvoiceSerializer, ItemDetailSerializer, ItemSerializer, CustomerSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.response import Response
from datetime import datetime
from users.models import CustomUser
from rest_framework import permissions
from rest_framework.decorators import action
from django.core.mail import send_mail


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def filter_queryset(self, queryset):
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ItemDetailViewSet(viewsets.ModelViewSet):
    queryset = ItemDetail.objects.all()
    serializer_class = ItemDetailSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        'customer': ['exact'],
        'date': ['exact', 'gte', 'lte'],
        'due_date': ['exact', 'gte', 'lte'],
        'order_number': ['exact'],
    }
    ordering_fields = ['order_number', 'date', 'due_date']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Invoice.objects.all()

        # Apply filters
        queryset = self.filter_queryset(queryset)

        # Apply ordering
        order = self.request.query_params.get('order')

        print(order)

        if order:
            if order.startswith('-'):
                queryset = queryset.order_by(order)
            else:
                queryset = queryset.order_by(order)

        return queryset

    def create(self, request, *args, **kwargs):
        print(request.user)
        user = CustomUser.objects.get(id=request.user.id)

        customer_id = request.data.get('customer')
        if not customer_id:
            return Response({'customer': 'This field is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'customer': 'Invalid customer ID.'},
                            status=status.HTTP_400_BAD_REQUEST)

        order_number = request.data.get('order_number')
        if not order_number:
            return Response({'order_number': 'This field is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        billing_address = request.data.get('billing_address', '')
        shipping_address = request.data.get('shipping_address', '')
        remarks = request.data.get('remarks', '')
        shipping_charges = request.data.get('shipping_charges', 0)
        adjustment = request.data.get('adjustment', 0)
        customer_notes = request.data.get('customer_notes', '')
        terms_and_conditions = request.data.get('terms_and_conditions', '')
        file_upload = request.FILES.get('file_upload')

        try:
            date = datetime.strptime(request.data['date'], '%Y-%m-%d')
        except ValueError:
            return Response({'date': 'Invalid date format.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            due_date = datetime.strptime(request.data['due_date'], '%Y-%m-%d')
        except ValueError:
            return Response({'due_date': 'Invalid date format.'},
                            status=status.HTTP_400_BAD_REQUEST)

        items = request.data.get('items', [])
        if not items:
            return Response({'items': 'This field is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(
            user=user,
            customer=customer,
            order_number=order_number,
            billing_address=billing_address,
            shipping_address=shipping_address,
            remarks=remarks,
            shipping_charges=shipping_charges,
            adjustment=adjustment,
            customer_notes=customer_notes,
            terms_and_conditions=terms_and_conditions,
            file_upload=file_upload,
            date=date.date(),
            due_date=due_date.date())

        for item in items:
            item_id = item.get('item')
            if not item_id:
                return Response({'items': 'Invalid item ID.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                item_obj = Item.objects.get(pk=item_id)
            except Item.DoesNotExist:
                return Response({'items': 'Invalid item ID.'},
                                status=status.HTTP_400_BAD_REQUEST)

            quantity = item.get('quantity', 0)
            rate = item.get('rate', 0)
            discount = item.get('discount', 0)
            tax = item.get('tax', 0)

            ItemDetail.objects.create(invoice=invoice,
                                      item=item_obj,
                                      quantity=(quantity),
                                      rate=(rate),
                                      discount=(discount),
                                      tax=(tax))
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=True, methods=['post'])
    # def send_mail(self, request, pk=None):
    #     try:
    #         invoice = Invoice.objects.get(pk=pk)
    #     except Invoice.DoesNotExist:
    #         return Response({'customer': 'Invalid Invoice ID.'},
    #                         status=status.HTTP_400_BAD_REQUEST)

    #     customer = invoice.customer

    #     send_mail(
    #         'Activate your account',
    #         f'Click the following link to activate your account: {settings.CLIENT_URL}/auth/activate/{token}',
    #         settings.EMAIL_HOST_USER,
    #         [user.email],
    #         fail_silently=False,
    #     )


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    filter_backends = [DjangoFilterBackend]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering_fields = ['rate', 'stock_on_hand', 'cost_price', 'selling_price']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Item.objects.all()

        # Apply filters
        queryset = self.filter_queryset(queryset)

        # Apply ordering
        order = self.request.query_params.get('order')

        if order:
            if order.startswith('-'):
                queryset = queryset.order_by(order)
            else:
                queryset = queryset.order_by(order)

        return queryset

    @action(detail=False, methods=['get'])
    def get_all_items(self, request):
        all_items = Item.objects.all()
        serializer = ItemSerializer(all_items, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)