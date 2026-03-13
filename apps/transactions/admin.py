from django.contrib import admin
from .models import Transaction, TransactionItem


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_number", "user", "store", "total_amount", "status", "transaction_date"]
    list_filter = ["status", "transaction_date"]
    search_fields = ["transaction_number", "user__phone"]


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ["transaction", "product_name", "quantity", "total_price"]
    search_fields = ["product_name"]