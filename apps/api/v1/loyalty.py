from django.db.models import Sum
from ninja import Router, Schema

router = Router()


class LoyaltyCardSchema(Schema):
    card_number: str
    barcode_type: str
    barcode_data: str
    is_virtual: bool
    has_physical_card: bool
    is_active: bool
    created_at: str


class BonusBalanceSchema(Schema):
    total_bonus: float
    available_bonus: float
    pending_bonus: float = 0
    expired_bonus: float
    next_expiration_date: str | None = None
    tier: str
    tier_points: int = 0
    next_tier_threshold: int = 2000


class LinkPhysicalCardSchema(Schema):
    card_number: str


class LinkPhysicalCardResponseSchema(Schema):
    success: bool
    message: str
    card: LoyaltyCardSchema | None = None


def calculate_balance(user):
    from apps.loyalty.models import BonusLedger
    
    earned = BonusLedger.objects.filter(
        user=user, type="earned"
    ).aggregate(Sum("amount"))["amount__sum"] or 0
    
    spent = BonusLedger.objects.filter(
        user=user, type="spent"
    ).aggregate(Sum("amount"))["amount__sum"] or 0
    
    expired = BonusLedger.objects.filter(
        user=user, type="expired"
    ).aggregate(Sum("amount"))["amount__sum"] or 0
    
    bonus = BonusLedger.objects.filter(
        user=user, type="bonus"
    ).aggregate(Sum("amount"))["amount__sum"] or 0
    
    return {
        "total_bonus": float(earned + bonus),
        "available_bonus": float(earned + bonus - spent - expired),
        "pending_bonus": 0,
        "expired_bonus": float(expired),
    }


@router.get("/card", response=LoyaltyCardSchema)
def get_card(request):
    """Get loyalty card info"""
    from apps.loyalty.models import LoyaltyCard
    
    card = LoyaltyCard.objects.filter(user=request.user, is_virtual=True).first()
    
    if not card:
        from apps.loyalty.models import LoyaltyCard
        card_number = f"2{randint(1000000000, 9999999999)}"
        card = LoyaltyCard.objects.create(
            user=request.user,
            card_number=card_number,
            barcode_type="code128",
            is_virtual=True
        )
    
    return LoyaltyCardSchema(
        card_number=card.card_number,
        barcode_type=card.barcode_type,
        barcode_data=card.card_number,
        is_virtual=card.is_virtual,
        has_physical_card=card.has_physical_card,
        is_active=card.is_active,
        created_at=card.created_at.isoformat()
    )


@router.get("/balance", response=BonusBalanceSchema)
def get_balance(request):
    """Get bonus balance"""
    balance = calculate_balance(request.user)
    profile = request.user.profile
    
    return BonusBalanceSchema(
        total_bonus=balance["total_bonus"],
        available_bonus=balance["available_bonus"],
        pending_bonus=balance["pending_bonus"],
        expired_bonus=balance["expired_bonus"],
        next_expiration_date=None,
        tier=profile.loyalty_tier,
        tier_points=int(balance["available_bonus"]),
        next_tier_threshold=2000
    )


@router.post("/link-physical-card", response=LinkPhysicalCardResponseSchema)
def link_physical_card(request, data: LinkPhysicalCardSchema):
    """Link physical card to user"""
    from apps.loyalty.models import LoyaltyCard
    from django.shortcuts import get_object_or_404
    
    try:
        card = LoyaltyCard.objects.get(card_number=data.card_number, is_virtual=False)
        
        if card.user:
            return LinkPhysicalCardResponseSchema(
                success=False,
                message="Карта уже привязана"
            )
        
        card.user = request.user
        card.save()
        
        virtual_card = LoyaltyCard.objects.filter(
            user=request.user, is_virtual=True
        ).first()
        if virtual_card:
            virtual_card.has_physical_card = True
            virtual_card.save()
        
        return LinkPhysicalCardResponseSchema(
            success=True,
            message="Карта привязана",
            card=LoyaltyCardSchema(
                card_number=card.card_number,
                barcode_type=card.barcode_type,
                barcode_data=card.card_number,
                is_virtual=card.is_virtual,
                has_physical_card=card.has_physical_card,
                is_active=card.is_active,
                created_at=card.created_at.isoformat()
            )
        )
    except LoyaltyCard.DoesNotExist:
        return LinkPhysicalCardResponseSchema(
            success=False,
            message="Карта не найдена"
        )


from random import randint