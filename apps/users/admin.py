from django.contrib import admin
from .models import User, CustomerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["phone", "email", "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff", "created_at"]
    search_fields = ["phone", "email"]
    ordering = ["-created_at"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "loyalty_tier", "status", "registered_at"]
    list_filter = ["loyalty_tier", "status", "gender"]
    search_fields = ["first_name", "last_name", "user__phone"]
    ordering = ["-registered_at"]