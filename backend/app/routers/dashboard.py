from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import Application, TimelineEvent

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

TERMINAL_STAGES = {"被拒", "主动放弃", "泡池子"}


@router.get("")
def get_dashboard(
    past_days: int = Query(3, ge=0, le=365),
    future_days: int = Query(7, ge=0, le=365),
    stale_days: int = Query(14, ge=1, le=365),
    session: Session = Depends(get_session),
):
    now = datetime.now()
    window_start = now - timedelta(days=past_days)
    window_end = now + timedelta(days=future_days)
    stale_threshold = now - timedelta(days=stale_days)

    apps = session.exec(select(Application)).all()
    app_map = {a.id: a for a in apps}

    stats = {
        "total": len(apps),
        "interviewing": sum(1 for a in apps if a.status == "面试中"),
        "offered": sum(1 for a in apps if a.status == "已 Offer"),
        "ended": sum(1 for a in apps if a.status in ("已拒", "已结束")),
    }

    events_in_window = session.exec(
        select(TimelineEvent)
        .where(TimelineEvent.happened_at >= window_start)
        .where(TimelineEvent.happened_at <= window_end)
        .order_by(TimelineEvent.happened_at.asc())
    ).all()

    upcoming = []
    for e in events_in_window:
        if e.stage in TERMINAL_STAGES:
            continue
        app = app_map.get(e.application_id)
        if app is None:
            continue
        upcoming.append({
            "event_id": e.id,
            "stage": e.stage,
            "happened_at": e.happened_at,
            "note": e.note,
            "application": {
                "id": app.id,
                "company": app.company,
                "position": app.position,
                "status": app.status,
            },
        })

    apps_with_events = set(
        session.exec(select(TimelineEvent.application_id).distinct()).all()
    )

    stale = []
    for a in apps:
        if a.id in apps_with_events:
            continue
        if a.applied_at >= stale_threshold:
            continue
        days_since = (now - a.applied_at).days
        stale.append({
            "id": a.id,
            "company": a.company,
            "position": a.position,
            "applied_at": a.applied_at,
            "days_since_applied": days_since,
        })
    stale.sort(key=lambda x: x["days_since_applied"], reverse=True)

    return {
        "stats": stats,
        "upcoming_interviews": upcoming,
        "stale_applications": stale,
    }
