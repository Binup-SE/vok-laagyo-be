from flask import g

from app.api import api_bp
from app.common.response import Response


@api_bp.get("/tenant")
def tenant_info():
    tenant = g.tenant
    return Response.success(
        {
            "id": str(tenant.id),
            "slug": tenant.slug,
            "name": tenant.name,
            "status": tenant.status,
        }
    )
