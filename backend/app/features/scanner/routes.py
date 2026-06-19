from fastapi import APIRouter, UploadFile, File
router = APIRouter(prefix="/api/scanner", tags=["scanner"])

@router.post("/scan")
async def scan_input(file: UploadFile = File(...)):
    return {"status": "scanned"}
