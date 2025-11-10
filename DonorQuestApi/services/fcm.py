import os
import firebase_admin
from firebase_admin import credentials, messaging
from config import settings

_app = None

def _ensure():
    global _app
    if _app: return _app
    if not settings.API_FIREBASE_CREDENTIALS or not os.path.exists(settings.API_FIREBASE_CREDENTIALS):
        return None
    cred = credentials.Certificate(settings.API_FIREBASE_CREDENTIALS)
    _app = firebase_admin.initialize_app(cred)
    return _app

def send_to_token(token: str, title: str, body: str, data: dict=None):
    if not _ensure():
        return False
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data={k:str(v) for k,v in (data or {}).items()}
    )
    resp = messaging.send(message)
    return resp
