from ninja import NinjaAPI

api = NinjaAPI(title="Elody-Farm Loyalty API", version="1.0.0")

from apps.api.v1.auth import router as auth_router
from apps.api.v1.profile import router as profile_router
from apps.api.v1.loyalty import router as loyalty_router
from apps.api.v1.transactions import router as transactions_router
from apps.api.v1.promotions import router as promotions_router
from apps.api.v1.stores import router as stores_router
from apps.api.v1.notifications import router as notifications_router
from apps.api.v1.surveys import router as surveys_router
from apps.api.v1.settings import router as settings_router
from apps.api.v1.webhooks import router as webhooks_router

api.add_router("/auth/", auth_router, tags="Auth")
api.add_router("/profile/", profile_router, tags="Profile")
api.add_router("/loyalty/", loyalty_router, tags="Loyalty")
api.add_router("/transactions/", transactions_router, tags="Transactions")
api.add_router("/promotions/", promotions_router, tags="Promotions")
api.add_router("/stores/", stores_router, tags="Stores")
api.add_router("/notifications/", notifications_router, tags="Notifications")
api.add_router("/surveys/", surveys_router, tags="Surveys")
api.add_router("/settings/", settings_router, tags="Settings")
api.add_router("/webhooks/", webhooks_router, tags="Webhooks")