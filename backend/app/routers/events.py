from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Application, TimelineEvent
from ..schemas import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate

router = APIRouter(prefix="/api/events", tags=["events"])

# 阶段 -> 投递状态 的映射；未列出的阶段（自定义）不联动状态
STATUS_FROM_STAGE: dict[str, str] = {
    "笔试/测评": "面试中",
    "一面": "面试中",
    "二面": "面试中",
    "三面": "面试中",
    "终面": "面试中",
    "HR 面": "面试中",
    "Offer 沟通": "已 Offer",
    "入职": "已 Offer",
    "被拒": "已拒",
    "主动放弃": "已结束",
    "泡池子": "已结束",
}


def _maybe_update_application_status(
    session: Session, application_id: int, stage: str
) -> None:
    new_status = STATUS_FROM_STAGE.get(stage)
    if new_status is None:
        return
    application = session.get(Application, application_id)
    if application is None:
        return
    application.status = new_status
    session.add(application)


@router.post("", response_model=TimelineEventRead, status_code=201)
def create_event(
    data: TimelineEventCreate,
    session: Session = Depends(get_session),
):
    application = session.get(Application, data.application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    event = TimelineEvent.model_validate(data)
    session.add(event)
    _maybe_update_application_status(session, data.application_id, data.stage)
    session.commit()
    session.refresh(event)
    return event


@router.get("", response_model=list[TimelineEventRead])
def list_events(
    application_id: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(TimelineEvent)
        .where(TimelineEvent.application_id == application_id)
        .order_by(TimelineEvent.happened_at.desc())
    )
    return session.exec(statement).all()


@router.patch("/{event_id}", response_model=TimelineEventRead)
def update_event(
    event_id: int,
    data: TimelineEventUpdate,
    session: Session = Depends(get_session),
):
    event = session.get(TimelineEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="时间线节点不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    session.add(event)
    if "stage" in update_data:
        _maybe_update_application_status(session, event.application_id, event.stage)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(TimelineEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="时间线节点不存在")
    session.delete(event)
    session.commit()
