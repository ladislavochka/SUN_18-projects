from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
ADMIN_PAGE = Path(__file__).with_name("admin.html")

@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_page():
    return ADMIN_PAGE.read_text(encoding="utf-8")
