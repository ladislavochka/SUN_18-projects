from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from auth import get_current_user

router = APIRouter(prefix="/images", tags=["Зображення"])
UPLOAD_DIR = Path(__file__).with_name("uploads")
ALLOWED = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED:
        raise HTTPException(400, "Дозволені формати: PNG, JPG, JPEG, WEBP, GIF")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Максимальний розмір файлу — 5 МБ")
    UPLOAD_DIR.mkdir(exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return {"image_name": filename, "url": f"/uploads/{filename}"}
