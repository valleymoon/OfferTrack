from datetime import datetime

from sqlmodel import Field, SQLModel


class ApplicationBase(SQLModel):
    company: str
    position: str
    jd: str = ""
    channel: str = ""
    applied_at: datetime
    status: str = "投递中"
    note: str = ""


class Application(ApplicationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class TimelineEventBase(SQLModel):
    application_id: int = Field(foreign_key="application.id")
    stage: str
    happened_at: datetime
    note: str = ""


class TimelineEvent(TimelineEventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class InterviewQuestionBase(SQLModel):
    event_id: int = Field(foreign_key="timelineevent.id")
    question: str
    my_answer: str = ""
    reflection: str = ""
    tags: str = ""


class InterviewQuestion(InterviewQuestionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
