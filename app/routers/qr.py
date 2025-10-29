from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import time
import os
import qrcode
import io
import base64
from app.security import sign_token

router = APIRouter(tags=["qr"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


@router.get("/kiosk/session/{session_id}", response_class=HTMLResponse)
def kiosk_session(session_id: int, request: Request):
    return templates.TemplateResponse("kiosk_session.html", {"request": request, "session_id": session_id})


@router.post("/qr/rotate")
def rotate_token(session_id: int):
    exp = int(time.time()) + 30
    token = sign_token(session_id=session_id, exp_ts=exp)
    return JSONResponse({"token": token, "expires_at": exp})


@router.get("/qr/generate/{session_id}")
def generate_qr(session_id: int):
    exp = int(time.time()) + 30
    token = sign_token(session_id=session_id, exp_ts=exp)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return JSONResponse({
        "token": token,
        "expires_at": exp,
        "qr_image": f"data:image/png;base64,{img_str}"
    })
