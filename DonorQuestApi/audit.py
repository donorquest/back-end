from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from models import AuditLog
from datetime import datetime

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        try:
            db: Session = SessionLocal()
            uid = request.headers.get("X-User-Id")
            log = AuditLog(
                method=request.method,
                path=request.url.path,
                user_id=uid,
                status_code=response.status_code,
            )
            db.add(log); db.commit()
        except Exception:
            pass
        finally:
            try: db.close()
            except: pass
        return response
