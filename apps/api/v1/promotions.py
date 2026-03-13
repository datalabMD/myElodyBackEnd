from datetime import datetime

from ninja import Router, Schema, Query

router = Router()


class PromotionSchema(Schema):
    id: str
    title: str
    subtitle: str = ""
    image_url: str = ""
    start_date: str
    end_date: str
    type: str
    category: str = ""


class PromotionDetailSchema(PromotionSchema):
    description: str
    participating_stores: list[dict] = []


class PaginatedResponse(Schema):
    items: list
    total: int
    page: int
    pages: int


@router.get("", response=PaginatedResponse)
def get_promotions(request, page: int = 1, limit: int = 20, type: str = "promotion"):
    """Get promotions"""
    from apps.promotions.models import Promotion
    from datetime import date
    
    today = date.today()
    queryset = Promotion.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
        type=type
    )
    
    total = queryset.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    items = [
        PromotionSchema(
            id=str(p.id),
            title=p.title,
            subtitle=p.subtitle or "",
            image_url=p.image_url or "",
            start_date=str(p.start_date),
            end_date=str(p.end_date),
            type=p.type,
            category=p.category or "",
        )
        for p in queryset[offset:offset + limit]
    ]
    
    return PaginatedResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{promotion_id}", response=PromotionDetailSchema)
def get_promotion(request, promotion_id: str):
    """Get promotion details"""
    from apps.promotions.models import Promotion
    from django.shortcuts import get_object_or_404
    
    promotion = get_object_or_404(Promotion, id=promotion_id, is_active=True)
    
    stores = [
        {"id": str(s.id), "name": s.name, "address": s.address}
        for s in promotion.participating_stores.all()
    ]
    
    return PromotionDetailSchema(
        id=str(promotion.id),
        title=promotion.title,
        subtitle=promotion.subtitle or "",
        description=promotion.description,
        image_url=promotion.image_url or "",
        start_date=str(promotion.start_date),
        end_date=str(promotion.end_date),
        type=promotion.type,
        category=promotion.category or "",
        participating_stores=stores,
    )


@router.get("/news", response=PaginatedResponse)
def get_news(request, page: int = 1, limit: int = 20):
    """Get news"""
    return get_promotions(request, page, limit, type="news")