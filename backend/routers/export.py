from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from dataclasses import dataclass
from models import ExportRequest
from typing import List

router = APIRouter()


def _to_result(data):
    from core.scoring_engine import ScoreResult, ScoreFactor
    factors = [ScoreFactor(name=f.name, value=f.value, max=f.max) for f in data.result.factors]
    return ScoreResult(
        score=data.result.score,
        risk=data.result.risk,
        duration=data.result.duration,
        fpy=data.result.fpy,
        inspection=data.result.inspection,
        ppap=data.result.ppap,
        recommendation=data.result.recommendation,
        factors=factors,
        pra_forecast=data.result.pra_forecast,
        conformance=data.result.conformance,
    )


def _to_checklist(items):
    from core.checklist_loader import ChecklistItem
    result = []
    for item in items:
        ci = ChecklistItem(
            step=item.step, text=item.text, phase=item.phase,
            critical=item.critical, warn=item.warn, done=item.done,
        )
        ci.owner = item.owner
        ci.due = item.due
        result.append(ci)
    return result


@router.post("/export/ppt")
def export_ppt(req: ExportRequest):
    from core.report_generator import generate_ppt
    try:
        data = generate_ppt(
            prog_type=req.prog_type,
            part_name=req.part_name,
            result=_to_result(req),
            checklist=_to_checklist(req.checklist),
            meta=req.meta,
            customer_name=req.customer_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    filename = f"Versigent_{req.part_name.replace(' ', '_')}_SafeLaunch.pptx"
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.post("/export/excel")
def export_excel(req: ExportRequest):
    from core.report_generator import generate_excel
    try:
        data = generate_excel(
            prog_type=req.prog_type,
            part_name=req.part_name,
            result=_to_result(req),
            checklist=_to_checklist(req.checklist),
            meta=req.meta,
            customer_name=req.customer_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    filename = f"Versigent_{req.part_name.replace(' ', '_')}_SafeLaunch.xlsx"
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
