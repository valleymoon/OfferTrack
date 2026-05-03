from datetime import datetime

from sqlmodel import SQLModel

from .models import ApplicationBase, InterviewQuestionBase, TimelineEventBase


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(SQLModel):
    company: str | None = None
    position: str | None = None
    jd: str | None = None
    channel: str | None = None
    applied_at: datetime | None = None
    status: str | None = None
    note: str | None = None


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime


class TimelineEventCreate(TimelineEventBase):
    pass


class TimelineEventUpdate(SQLModel):
    stage: str | None = None
    happened_at: datetime | None = None
    note: str | None = None


class TimelineEventRead(TimelineEventBase):
    id: int
    created_at: datetime


class InterviewQuestionCreate(InterviewQuestionBase):
    pass


class InterviewQuestionUpdate(SQLModel):
    question: str | None = None
    my_answer: str | None = None
    reflection: str | None = None
    tags: str | None = None


class InterviewQuestionRead(InterviewQuestionBase):
    id: int
    created_at: datetime
