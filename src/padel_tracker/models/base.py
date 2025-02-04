from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, TIMESTAMP, Text, VARCHAR


class ValidatedSQLModel(SQLModel):
    model_config = ConfigDict(validate_assignment=True)


class Logs(SQLModel, table=True):
    timestamp: datetime = Field(primary_key=True, sa_type=TIMESTAMP(timezone=True))
    name: str | None = Field(sa_type=VARCHAR)
    level: str | None = Field(sa_type=VARCHAR)
    message: str | None = Field(sa_type=Text)
