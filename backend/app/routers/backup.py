from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import get_session
from ..models import Application, InterviewQuestion, TimelineEvent

router = APIRouter(prefix="/api/backup", tags=["backup"])

CURRENT_VERSION = 1


class BackupPayload(BaseModel):
    version: int
    exported_at: datetime | None = None
    applications: list[dict[str, Any]]
    events: list[dict[str, Any]]
    questions: list[dict[str, Any]]


class ImportRequest(BaseModel):
    mode: Literal["overwrite", "merge"]
    payload: BackupPayload


class ImportResult(BaseModel):
    mode: str
    applications_imported: int
    events_imported: int
    questions_imported: int


@router.get("/export", response_model=BackupPayload)
def export_all(session: Session = Depends(get_session)):
    apps = session.exec(select(Application)).all()
    events = session.exec(select(TimelineEvent)).all()
    questions = session.exec(select(InterviewQuestion)).all()
    return BackupPayload(
        version=CURRENT_VERSION,
        exported_at=datetime.now(),
        applications=[a.model_dump(mode="json") for a in apps],
        events=[e.model_dump(mode="json") for e in events],
        questions=[q.model_dump(mode="json") for q in questions],
    )


@router.post("/import", response_model=ImportResult)
def import_all(req: ImportRequest, session: Session = Depends(get_session)):
    if req.payload.version != CURRENT_VERSION:
        raise HTTPException(
            status_code=400,
            detail=f"备份文件版本 {req.payload.version} 不被支持（当前版本 {CURRENT_VERSION}）",
        )

    if req.mode == "overwrite":
        for q in session.exec(select(InterviewQuestion)).all():
            session.delete(q)
        for e in session.exec(select(TimelineEvent)).all():
            session.delete(e)
        for a in session.exec(select(Application)).all():
            session.delete(a)
        session.flush()

    app_id_map: dict[int, int] = {}
    for raw in req.payload.applications:
        old_id = raw.get("id")
        data = {k: v for k, v in raw.items() if k != "id"}
        application = Application.model_validate(data)
        session.add(application)
        session.flush()
        if old_id is not None and application.id is not None:
            app_id_map[int(old_id)] = application.id

    event_id_map: dict[int, int] = {}
    for raw in req.payload.events:
        old_id = raw.get("id")
        data = {k: v for k, v in raw.items() if k != "id"}
        old_app_id = data.get("application_id")
        if old_app_id is None:
            continue
        new_app_id = app_id_map.get(int(old_app_id))
        if new_app_id is None:
            continue
        data["application_id"] = new_app_id
        event = TimelineEvent.model_validate(data)
        session.add(event)
        session.flush()
        if old_id is not None and event.id is not None:
            event_id_map[int(old_id)] = event.id

    questions_imported = 0
    for raw in req.payload.questions:
        data = {k: v for k, v in raw.items() if k != "id"}
        old_event_id = data.get("event_id")
        if old_event_id is None:
            continue
        new_event_id = event_id_map.get(int(old_event_id))
        if new_event_id is None:
            continue
        data["event_id"] = new_event_id
        question = InterviewQuestion.model_validate(data)
        session.add(question)
        questions_imported += 1

    session.commit()

    return ImportResult(
        mode=req.mode,
        applications_imported=len(app_id_map),
        events_imported=len(event_id_map),
        questions_imported=questions_imported,
    )
