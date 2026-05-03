from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Application
from ..schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(
    data: ApplicationCreate,
    session: Session = Depends(get_session),
):
    application = Application.model_validate(data)
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@router.get("", response_model=list[ApplicationRead])
def list_applications(session: Session = Depends(get_session)):
    statement = select(Application).order_by(Application.applied_at.desc())
    return session.exec(statement).all()


@router.get("/{app_id}", response_model=ApplicationRead)
def get_application(app_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return application


@router.patch("/{app_id}", response_model=ApplicationRead)
def update_application(
    app_id: int,
    data: ApplicationUpdate,
    session: Session = Depends(get_session),
):
    application = session.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(application, key, value)
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    session.delete(application)
    session.commit()
