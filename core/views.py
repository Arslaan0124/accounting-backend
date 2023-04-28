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
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from django.db.models import Sum, F, FloatField
from django.http import JsonResponse
from decimal import Decimal


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    ordering_fields = ['created_at', 'type']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def get_invoices(self, request, pk=None):
        customer = self.get_object()
        invoices = customer.invoices
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def filter_queryset(self, queryset):
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_queryset(self):
        queryset = Customer.objects.all()

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
        'status': ['exact'],
        'payment_status': ['exact'],
    }
    ordering_fields = ['order_number', 'date', 'due_date']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Invoice.objects.all()
        queryset = self.filter_queryset(queryset)
        order = self.request.query_params.get('order')

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

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        invoice = self.get_object()
        customer_email = invoice.customer.email
        subject = f'Your invoice Number is {invoice.order_number}'

        # Load the HTML email template and render it with the invoice data
        template_path = 'email_templates/invoice_email_template.html'  # Set the path to your email template here
        html_message = render_to_string(template_path, {'invoice': invoice})

        # Generate the PDF version of the invoice
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"Invoice Number: {invoice.order_number}")
        p.drawString(100, 700, f"Customer Name: {invoice.customer.name}")
        p.drawString(100, 650, f"REST OF THE PDF WILL BE GENERATED LATER :)")
        p.showPage()
        p.save()
        pdf_content = buffer.getvalue()
        buffer.close()

        # Create the plain text version of the message by stripping the HTML tags from the HTML version
        text_message = strip_tags(html_message)

        # Attach both the PDF and HTML versions of the message to the email
        pdf_file = ContentFile(pdf_content)
        pdf_file.name = f"invoice-{invoice.order_number}.pdf"
        email = EmailMultiAlternatives(subject,
                                       text_message,
                                       from_email=settings.EMAIL_HOST_USER,
                                       to=[customer_email])
        email.attach_alternative(html_message, "text/html")
        email.attach(pdf_file.name, pdf_content, 'application/pdf')

        try:
            # Send the email
            email.send()

            invoice.sent_times += 1
            invoice.save()

            return Response({'success': True})
        except:
            return Response({'success': False})

    @action(detail=True, methods=['post'])
    def update_payment_status(self, request, pk=None):
        try:
            invoice = self.get_object()
            print(request.data)
            payment_status = request.data.get('payment_status', '').lower()

            if payment_status == 'paid':
                invoice.payment_status = 'paid'
            elif payment_status == 'unpaid':
                invoice.payment_status = 'unpaid'
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid payment status'
                })

            invoice.save()
            return Response({'success': True})
        except:
            return Response({'success': False})


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


# @action(detail=False, methods=['get'])
def get_sales_and_profit(request):
    # Calculate the date ranges for the past month, week, and year
    total_invoices = Invoice.objects.count()
    total_customers = Customer.objects.count()
    total_items = Item.objects.count()

    today = datetime.today().date()
    month_ago = today - timedelta(days=30)
    week_ago = today - timedelta(days=7)
    year_ago = today - timedelta(days=365)

    # Calculate the total sales and profits for the past month, week, and year
    sales_month = Invoice.objects.filter(
        date__gte=month_ago, payment_status='paid').aggregate(total_sales=Sum(
            F('items__rate') *
            F('items__quantity'), output_field=FloatField()))
    sales_week = Invoice.objects.filter(
        date__gte=week_ago, payment_status='paid').aggregate(total_sales=Sum(
            F('items__rate') *
            F('items__quantity'), output_field=FloatField()))
    sales_year = Invoice.objects.filter(
        date__gte=year_ago, payment_status='paid').aggregate(total_sales=Sum(
            F('items__rate') *
            F('items__quantity'), output_field=FloatField()))

    # profit_month = Invoice.objects.filter(
    #     date__gte=month_ago, payment_status='paid').annotate(
    #         total_cost=Sum('items__cost_price')).aggregate(
    #             total_profit=Sum(F('items__selling_price') *
    #                              F('items__quantity') - F('total_cost'),
    #                              output_field=FloatField()))
    # profit_week = Invoice.objects.filter(
    #     date__gte=week_ago, payment_status='paid').annotate(
    #         total_cost=Sum('items__cost_price')).aggregate(
    #             total_profit=Sum(F('items__selling_price') *
    #                              F('items__quantity') - F('total_cost'),
    #                              output_field=FloatField()))
    # profit_year = Invoice.objects.filter(
    #     date__gte=year_ago, payment_status='paid').annotate(
    #         total_cost=Sum('items__cost_price')).aggregate(
    #             total_profit=Sum(F('items__selling_price') *
    #                              F('items__quantity') - F('total_cost'),
    #                              output_field=FloatField()))

    # Return the sales and profits as a JSON response
    data = {
        'sales': {
            'month': sales_month['total_sales'] or 0,
            'week': sales_week['total_sales'] or 0,
            'year': sales_year['total_sales'] or 0,
        },
        'profits': {
            # 'month': profit_month['total_profit'] or 0,
            # 'week': profit_week['total_profit'] or 0,
            # 'year': profit_year['total_profit'] or 0,
        }
    }
    return JsonResponse(data)


def calculate_invoice_total(items):
    subtotals = []
    for item in items:
        quantity = item.quantity
        selling_price = float(item.item.selling_price)
        discount_percentage = float(item.discount)
        tax_percentage = float(item.tax)

        # Calculate subtotal
        subtotal = quantity * selling_price
        # Apply discount
        discount_amount = subtotal * (discount_percentage / 100)
        subtotal -= discount_amount
        # Apply tax
        tax_amount = subtotal * (tax_percentage / 100)
        subtotal += tax_amount

        subtotals.append(subtotal)

    # Calculate grand total
    grand_total = sum(subtotals)
    return grand_total


# GET ALL CUSTOMERS THAT HAVE SOME INVOICES WHICH ARE PAID
def get_customers_with_sales(request):
    # Get all customers that have at least one paid invoice
    customers = Customer.objects.filter(
        invoices__payment_status='paid').distinct()

    # Calculate total paid and unpaid invoices for each customer
    customer_totals = []
    for customer in customers:
        paid_invoices = customer.invoices.filter(payment_status='paid')
        unpaid_invoices = customer.invoices.filter(payment_status='unpaid')
        invoice_list = []
        total_sale = 0
        for invoice in paid_invoices:
            total_sale += calculate_invoice_total(invoice.items.all())
            invoice_list.append({
                'id':
                invoice.id,
                'order_number':
                invoice.order_number,
                'date':
                invoice.date,
                'total_sale':
                calculate_invoice_total(invoice.items.all())
            })
        customer_totals.append({
            'name': customer.name,
            'paid_invoices': paid_invoices.count(),
            'unpaid_invoices': unpaid_invoices.count(),
            'invoices': invoice_list,
            'total_sale': total_sale
        })

    # Return response with list of customer invoice totals
    return JsonResponse({'customer_totals': customer_totals})


def get_profit_and_cost_of_paid_invoices(request):
    # Get all paid invoices
    paid_invoices = Invoice.objects.filter(payment_status='paid')

    # Calculate total cost and profit of all paid invoices
    total_cost = Decimal(0)
    total_profit = float(0)
    invoice_list = []
    for invoice in paid_invoices:
        cost = Decimal(0)
        for item in invoice.items.all():
            cost += item.item.cost_price * item.quantity
        total_cost += cost
        revenue = calculate_invoice_total(invoice.items.all())
        profit = revenue - float(cost)
        total_profit += profit
        invoice_list.append({
            'id': invoice.id,
            'order_number': invoice.order_number,
            'date': invoice.date,
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
        })

    # Return response with total cost and profit of all paid invoices
    return JsonResponse({
        'total_cost': str(total_cost),
        'total_profit': str(total_profit),
        'invoices': invoice_list,
    })