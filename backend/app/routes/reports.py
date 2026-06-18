from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from typing import List
from datetime import datetime
from app.database import db_manager
from app.services.ai_service import ai_service
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("")
async def get_reports(current_user: dict = Depends(get_current_user)):
    reports = await db_manager.get_reports_by_user(current_user["id"])
    return reports

@router.post("/generate")
async def generate_report(current_user: dict = Depends(get_current_user)):
    history = await db_manager.get_footprints_by_user(current_user["id"])
    
    # We pass user history and current user profile to AI Service
    report_data = await ai_service.get_weekly_report(history, current_user)
    
    report_doc = {
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().isoformat(),
        "summary": report_data.get("summary", ""),
        "trends": report_data.get("trends", ""),
        "savings": report_data.get("savings", "0.0 kg CO2"),
        "recommendations": report_data.get("recommendations", []),
        "score_change": report_data.get("score_change", 0)
    }
    
    saved = await db_manager.add_report(report_doc)
    
    # Update points for generating report
    updated_points = current_user.get("points", 0) + 15
    updated_level = 1 + updated_points // 100
    await db_manager.update_user(current_user["id"], {
        "points": updated_points,
        "level": updated_level
    })
    
    return saved

@router.get("/{report_id}/download", response_class=PlainTextResponse)
async def download_report(report_id: str, current_user: dict = Depends(get_current_user)):
    reports = await db_manager.get_reports_by_user(current_user["id"])
    target_report = None
    for rep in reports:
        if rep["id"] == report_id:
            target_report = rep
            break
            
    if not target_report:
        raise HTTPException(status_code=404, detail="Report not found")

    date_str = target_report["created_at"][:10]
    
    # Format a beautiful layout for raw file download
    report_text = f"""==================================================
        GREENMIND AI - WEEKLY SUSTAINABILITY REPORT
==================================================
Date Created: {target_report["created_at"][:19].replace("T", " ")} UTC
Account:      {current_user["username"]} ({current_user["email"]})
Current Level: Level {current_user["level"]}
--------------------------------------------------

EMISSIONS SUMMARY:
{target_report["summary"]}

TRENDS & PROGRESS:
{target_report["trends"]}

ESTIMATED CARBON SAVINGS THIS WEEK:
{target_report["savings"]}
(Compared to global daily per-person carbon averages)

SUSTAINABILITY SCORE DELTA:
Score Change: {"+" if target_report["score_change"] >= 0 else ""}{target_report["score_change"]}

AI SUSTAINABILITY COACH RECOMMENDATIONS:
"""
    for idx, rec in enumerate(target_report["recommendations"], 1):
        report_text += f"{idx}. [ ] {rec}\n"
        
    report_text += f"""
--------------------------------------------------
Thank you for using GreenMind AI! 
Keep tracking, reducing, and logging to protect our planet.
==================================================
"""
    
    headers = {
        "Content-Disposition": f'attachment; filename="greenmind_report_{date_str}.txt"'
    }
    
    return PlainTextResponse(content=report_text, headers=headers)
