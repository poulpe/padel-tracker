from uuid import UUID, uuid4
from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, TIMESTAMP, Text, VARCHAR


class ValidatedSQLModel(SQLModel):
    model_config = ConfigDict(validate_assignment=True)


class Logs(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime | None = Field(sa_type=TIMESTAMP(timezone=True))
    name: str | None = Field(sa_type=VARCHAR)
    level: str | None = Field(sa_type=VARCHAR)
    message: str | None = Field(sa_type=Text)
