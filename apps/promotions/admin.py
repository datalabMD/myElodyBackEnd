from django.contrib import admin
from .models import Promotion, NewsItem


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["title", "type", "start_date", "end_date", "is_active"]
    list_filter = ["type", "is_active"]
    search_fields = ["title"]


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ["title", "published_at", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["title"]