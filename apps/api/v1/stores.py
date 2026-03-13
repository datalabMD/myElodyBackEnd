from datetime import datetime

from ninja import Router, Schema, Query
from pydantic import Field

router = Router()


class StoreSchema(Schema):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str = ""
    distance: float | None = None
    opening_hours: dict = {}
    services: dict = {}


class PaginatedResponse(Schema):
    items: list
    total: int
    page: int
    pages: int


@router.get("", response=PaginatedResponse)
def get_stores(
    request,
    lat: float | None = Query(None),
    lng: float | None = Query(None),
    radius: int = Query(5),
    search: str = Query(""),
    page: int = Query(1),
    limit: int = Query(20, le=100),
):
    """Get list of stores"""
    from apps.stores.models import Store
    
    queryset = Store.objects.filter(is_active=True)
    
    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(address__icontains=search)
    
    total = queryset.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    stores = queryset[offset:offset + limit]
    
    items = [
        StoreSchema(
            id=str(s.id),
            name=s.name,
            address=s.address,
            latitude=float(s.latitude),
            longitude=float(s.longitude),
            phone=s.phone or "",
            opening_hours=s.opening_hours or {},
            services=s.services or {},
        )
        for s in stores
    ]
    
    return PaginatedResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{store_id}", response=StoreSchema)
def get_store(request, store_id: str):
    """Get store details"""
    from apps.stores.models import Store
    from django.shortcuts import get_object_or_404
    
    store = get_object_or_404(Store, id=store_id, is_active=True)
    
    return StoreSchema(
        id=str(store.id),
        name=store.name,
        address=store.address,
        latitude=float(store.latitude),
        longitude=float(store.longitude),
        phone=store.phone or "",
        opening_hours=store.opening_hours or {},
        services=store.services or {},
    )