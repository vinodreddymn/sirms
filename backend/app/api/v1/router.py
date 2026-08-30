from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.asset.router import router as asset_router
from app.api.v1.dashboard.router import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.common.router import router as common_router
from app.api.v1.incidents.router import router as incidents_router
from app.api.v1.work_requests.router import router as work_requests_router
from app.api.v1.infrastructure.router import router as infrastructure_router
from app.api.v1.maintenance.router import router as maintenance_router
from app.api.v1.master.router import router as master_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.reports.router import router as reports_router
from app.api.v1.search.router import router as search_router
from app.api.v1.stock.router import router as stock_router
from app.api.v1.uploads.router import router as uploads_router
from app.api.v1.users.router import router as users_router
from app.api.v1.roles.router import router as roles_router
from app.api.v1.permissions.router import router as permissions_router
from app.api.v1.audit.router import router as audit_router
from app.api.v1.finance.router import router as finance_router
from app.api.v1.dispatch.router import router as dispatch_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(master_router)
api_router.include_router(common_router)
api_router.include_router(infrastructure_router)
api_router.include_router(asset_router)
api_router.include_router(incidents_router)
api_router.include_router(maintenance_router)
api_router.include_router(stock_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(search_router)
api_router.include_router(uploads_router)
api_router.include_router(notifications_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(audit_router)
api_router.include_router(finance_router)
api_router.include_router(dispatch_router)
api_router.include_router(work_requests_router)
