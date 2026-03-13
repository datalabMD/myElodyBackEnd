from django.contrib import admin
from .models import LoyaltyCard, BonusLedger, BonusSettings


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(admin.ModelAdmin):
    list_display = ["card_number", "user", "is_virtual", "has_physical_card", "is_active", "created_at"]
    list_filter = ["is_virtual", "has_physical_card", "is_active"]
    search_fields = ["card_number", "user__phone"]


@admin.register(BonusLedger)
class BonusLedgerAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "amount", "created_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["user__phone"]


@admin.register(BonusSettings)
class BonusSettingsAdmin(admin.ModelAdmin):
    list_display = ["bonus_rate", "expiration_months", "min_bonus_to_spend"]