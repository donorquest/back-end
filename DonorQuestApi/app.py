from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from config import settings
from routers import auth, donors, requests as reqs, admin, notifications, matches
from audit import AuditMiddleware

limiter = Limiter(key_func=get_remote_address)
api_prefix = f"/api/donorquest/{settings.API_VERSION}"
app = FastAPI(
    title="DonorQuest",
    version="1.0.0",
    openapi_prefix=api_prefix
)
origins = [o.strip() for o in settings.API_CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuditMiddleware)

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(donors.router, prefix="/donors", tags=["donors"])
app.include_router(reqs.router, prefix="/requests", tags=["requests"])
app.include_router(matches.router, prefix="/matches", tags=["matches"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(notifications.router, prefix="/notify", tags=["notifications"])
