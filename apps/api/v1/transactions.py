from ninja import Router, Schema, Query

router = Router()


class TransactionSchema(Schema):
    id: str
    transaction_number: str
    date: str
    store_name: str
    total_amount: float
    bonus_earned: float
    bonus_spent: float
    status: str


class TransactionItemSchema(Schema):
    product_name: str
    quantity: int
    unit_price: float
    discount: float
    total_price: float
    is_promotional: bool


class TransactionDetailSchema(Schema):
    id: str
    transaction_number: str
    date: str
    store: dict
    total_amount: float
    bonus_earned: float
    bonus_spent: float
    status: str
    items: list[TransactionItemSchema]


class PaginatedResponse(Schema):
    items: list
    total: int
    page: int
    pages: int


@router.get("", response=PaginatedResponse)
def get_transactions(
    request,
    page: int = Query(1),
    limit: int = Query(20, le=100),
    type: str = Query("all"),
):
    """Get user transactions"""
    from apps.transactions.models import Transaction
    
    queryset = Transaction.objects.filter(user=request.user).select_related("store")
    
    if type == "earned":
        queryset = queryset.filter(bonus_earned__gt=0)
    elif type == "spent":
        queryset = queryset.filter(bonus_spent__gt=0)
    
    total = queryset.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    transactions = queryset[offset:offset + limit]
    
    items = [
        TransactionSchema(
            id=str(t.id),
            transaction_number=t.transaction_number,
            date=t.transaction_date.isoformat(),
            store_name=t.store.name,
            total_amount=float(t.total_amount),
            bonus_earned=float(t.bonus_earned),
            bonus_spent=float(t.bonus_spent),
            status=t.status,
        )
        for t in transactions
    ]
    
    return PaginatedResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{transaction_id}", response=TransactionDetailSchema)
def get_transaction(request, transaction_id: str):
    """Get transaction details"""
    from apps.transactions.models import Transaction
    from django.shortcuts import get_object_or_404
    
    transaction = get_object_or_404(
        Transaction, id=transaction_id, user=request.user
    ).select_related("store").prefetch_related("items")
    
    items = [
        TransactionItemSchema(
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=float(item.unit_price),
            discount=float(item.discount),
            total_price=float(item.total_price),
            is_promotional=item.is_promotional,
        )
        for item in transaction.items.all()
    ]
    
    return TransactionDetailSchema(
        id=str(transaction.id),
        transaction_number=transaction.transaction_number,
        date=transaction.transaction_date.isoformat(),
        store={
            "id": str(transaction.store.id),
            "name": transaction.store.name,
            "address": transaction.store.address,
        },
        total_amount=float(transaction.total_amount),
        bonus_earned=float(transaction.bonus_earned),
        bonus_spent=float(transaction.bonus_spent),
        status=transaction.status,
        items=items,
    )