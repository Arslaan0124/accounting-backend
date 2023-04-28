from django.urls import path, include
from rest_framework import routers
from .views import ItemViewSet, ItemDetailViewSet, InvoiceViewSet, CustomerViewSet
from .views import get_sales_and_profit, get_customers_with_sales, get_profit_and_cost_of_paid_invoices

from rest_framework_simplejwt.views import (
    TokenRefreshView, )

router = routers.DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'itemdetails', ItemDetailViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sales-profit/', get_sales_and_profit, name='sales_profit'),
    path('customer-sales/', get_customers_with_sales, name='customer_sales'),
    path('profit-loss/',
         get_profit_and_cost_of_paid_invoices,
         name='profit_loss'),
]