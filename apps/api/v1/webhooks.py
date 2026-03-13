from ninja import Router, Schema
from pydantic import Field

router = Router()


class TransactionItemSchema(Schema):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    discount: float = 0
    total_price: float
    is_promotional: bool = False


class TransactionWebhookSchema(Schema):
    transaction_id: str
    card_number: str
    store_id: str
    total_amount: float
    bonus_earned: float = 0
    bonus_spent: float = 0
    items: list[TransactionItemSchema]
    timestamp: str


class TransactionWebhookResponseSchema(Schema):
    success: bool
    transaction_id: str | None = None
    error: str | None = None


@router.post("/transaction", response=TransactionWebhookResponseSchema)
def receive_transaction_webhook(request, data: TransactionWebhookSchema):
    """Receive transaction from ERP system"""
    from apps.loyalty.models import LoyaltyCard, BonusLedger
    from apps.transactions.models import Transaction, TransactionItem
    from apps.stores.models import Store
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from datetime import datetime
    
    try:
        card = LoyaltyCard.objects.filter(card_number=data.card_number).first()
        
        if not card:
            return TransactionWebhookResponseSchema(
                success=False, error="Карта не найдена"
            )
        
        store = get_object_or_404(Store, id=data.store_id)
        
        transaction = Transaction.objects.create(
            user=card.user,
            store=store,
            transaction_number=f"TRX-{data.transaction_id}",
            total_amount=data.total_amount,
            bonus_earned=data.bonus_earned,
            bonus_spent=data.bonus_spent,
            status="completed",
            transaction_date=timezone.make_aware(
                datetime.fromisoformat(data.timestamp.replace("Z", "+00:00"))
            ),
            erp_id=data.transaction_id
        )
        
        for item in data.items:
            TransactionItem.objects.create(
                transaction=transaction,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                total_price=item.total_price,
                is_promotional=item.is_promotional,
            )
        
        if data.bonus_earned > 0:
            BonusLedger.objects.create(
                user=card.user,
                transaction=transaction,
                type="earned",
                amount=data.bonus_earned,
                description=f"Покупка в {store.name}",
            )
        
        if data.bonus_spent > 0:
            BonusLedger.objects.create(
                user=card.user,
                transaction=transaction,
                type="spent",
                amount=data.bonus_spent,
                description=f"Списание бонусов",
            )
        
        return TransactionWebhookResponseSchema(
            success=True,
            transaction_id=str(transaction.id)
        )
        
    except Exception as e:
        return TransactionWebhookResponseSchema(
            success=False,
            error=str(e)
        )