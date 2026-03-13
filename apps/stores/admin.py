from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "phone", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "address"]