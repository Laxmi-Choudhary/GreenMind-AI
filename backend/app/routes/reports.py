from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.database import db_manager
from app.middleware.auth_middleware import get_current_user
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


# =====================================================
# GET ALL REPORTS
# =====================================================

@router.get("")
async def get_reports(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all reports for logged-in user.
    """

    try:
        reports = await db_manager.get_reports_by_user(
            current_user["id"]
        )

        return {
            "success": True,
            "count": len(reports),
            "reports": reports
        }

    except Exception as e:

        logger.exception(
            f"Failed to fetch reports: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to fetch reports."
        )


# =====================================================
# GENERATE REPORT
# =====================================================

@router.post("/generate")
async def generate_report(
    current_user: dict = Depends(get_current_user)
):
    """
    Generate weekly sustainability report.
    """

    try:

        # Fetch footprint history

        history = await db_manager.get_footprints_by_user(
            current_user["id"]
        )

        if history is None:
            history = []

        logger.info(
            f"Generating report for "
            f"user {current_user['id']}"
        )

        # Generate report from AI

        try:

            report_data = (
                await ai_service.get_weekly_report(
                    history,
                    current_user
                )
            )

        except Exception as ai_error:

            logger.exception(
                f"AI report generation failed: "
                f"{ai_error}"
            )

            report_data = None

        # Fallback report

        if not report_data:

            report_data = {
                "summary":
                    "Insufficient footprint data "
                    "available for detailed analysis.",

                "trends":
                    "Continue logging activities to "
                    "unlock sustainability trends.",

                "savings":
                    "0 kg CO2",

                "recommendations": [
                    "Track your carbon footprint daily.",
                    "Use public transport whenever possible.",
                    "Reduce electricity consumption.",
                    "Choose sustainable products."
                ],

                "score_change": 0
            }

        recommendations = report_data.get(
            "recommendations",
            []
        )

        if not isinstance(recommendations, list):
            recommendations = [
                str(recommendations)
            ]

        # Create report document

        report_doc = {

            "user_id":
                current_user["id"],

            "created_at":
                datetime.utcnow().isoformat(),

            "summary":
                report_data.get(
                    "summary",
                    ""
                ),

            "trends":
                report_data.get(
                    "trends",
                    ""
                ),

            "savings":
                report_data.get(
                    "savings",
                    "0 kg CO2"
                ),

            "recommendations":
                recommendations,

            "score_change":
                int(
                    report_data.get(
                        "score_change",
                        0
                    )
                )
        }

        # Save report

        saved_report = await db_manager.add_report(
            report_doc
        )

        # Reward user

        old_points = current_user.get(
            "points",
            0
        )

        new_points = old_points + 15

        new_level = (
            1 + new_points // 100
        )

        await db_manager.update_user(
            current_user["id"],
            {
                "points": new_points,
                "level": new_level
            }
        )

        logger.info(
            f"Report generated successfully "
            f"for user {current_user['id']}"
        )

        return {
            "success": True,

            "message":
                "Report generated successfully.",

            "report":
                saved_report,

            "reward": {
                "points_awarded": 15,
                "total_points": new_points,
                "current_level": new_level
            }
        }

    except Exception as e:

        logger.exception(
            f"Generate report failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


# =====================================================
# DOWNLOAD REPORT
# =====================================================

@router.get(
    "/{report_id}/download",
    response_class=PlainTextResponse
)
async def download_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download report as TXT file.
    """

    try:

        reports = await db_manager.get_reports_by_user(
            current_user["id"]
        )

        report = next(
            (
                r for r in reports
                if r.get("id") == report_id
            ),
            None
        )

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Report not found."
            )

        created_at = report.get(
            "created_at",
            datetime.utcnow().isoformat()
        )

        recommendations = report.get(
            "recommendations",
            []
        )

        if not isinstance(recommendations, list):
            recommendations = [
                str(recommendations)
            ]

        text = f"""
==================================================
            GREENMIND AI REPORT
==================================================

Date:
{created_at}

User:
{current_user.get('username', 'Unknown')}

Email:
{current_user.get('email', 'N/A')}

Level:
{current_user.get('level', 1)}

==================================================
SUMMARY
==================================================

{report.get('summary', 'N/A')}

==================================================
TRENDS
==================================================

{report.get('trends', 'N/A')}

==================================================
CARBON SAVINGS
==================================================

{report.get('savings', '0 kg CO2')}

==================================================
SCORE CHANGE
==================================================

{report.get('score_change', 0)}

==================================================
AI RECOMMENDATIONS
==================================================

"""

        if recommendations:

            for index, rec in enumerate(
                recommendations,
                start=1
            ):

                text += f"{index}. {rec}\n"

        else:

            text += (
                "No recommendations available.\n"
            )

        text += """

==================================================
Thank you for using GreenMind AI.

Continue tracking and reducing
your carbon footprint.

==================================================
"""

        filename = (
            f'greenmind_report_'
            f'{created_at[:10]}.txt'
        )

        headers = {
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }

        return PlainTextResponse(
            content=text,
            headers=headers
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Download report failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )