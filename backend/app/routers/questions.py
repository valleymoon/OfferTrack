from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import InterviewQuestion, TimelineEvent
from ..schemas import (
    InterviewQuestionCreate,
    InterviewQuestionRead,
    InterviewQuestionUpdate,
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("", response_model=InterviewQuestionRead, status_code=201)
def create_question(
    data: InterviewQuestionCreate,
    session: Session = Depends(get_session),
):
    event = session.get(TimelineEvent, data.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="时间线节点不存在")
    question = InterviewQuestion.model_validate(data)
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@router.get("", response_model=list[InterviewQuestionRead])
def list_questions(
    event_id: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(InterviewQuestion)
        .where(InterviewQuestion.event_id == event_id)
        .order_by(InterviewQuestion.created_at.asc())
    )
    return session.exec(statement).all()


@router.patch("/{question_id}", response_model=InterviewQuestionRead)
def update_question(
    question_id: int,
    data: InterviewQuestionUpdate,
    session: Session = Depends(get_session),
):
    question = session.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="面试题不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@router.delete("/{question_id}", status_code=204)
def delete_question(question_id: int, session: Session = Depends(get_session)):
    question = session.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="面试题不存在")
    session.delete(question)
    session.commit()
