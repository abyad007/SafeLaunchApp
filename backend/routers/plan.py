from fastapi import APIRouter, HTTPException
from models import ChecklistRequest, ChecklistItemOut
from typing import List

router = APIRouter()


@router.post("/plan", response_model=List[ChecklistItemOut])
def get_plan(req: ChecklistRequest):
    from core.checklist_loader import load_checklist
    try:
        items = load_checklist(req.prog_type, req.context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return [
        ChecklistItemOut(
            step=item.step,
            text=item.text,
            phase=item.phase,
            critical=item.critical,
            warn=getattr(item, "warn", item.critical),
            done=item.done,
            owner=getattr(item, "owner", ""),
            due=getattr(item, "due", ""),
        )
        for item in items
    ]
