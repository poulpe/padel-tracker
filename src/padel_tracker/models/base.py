from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, TIMESTAMP, Text, BIGINT, VARCHAR, Column


class ValidatedSQLModel(SQLModel):
    model_config = ConfigDict(validate_assignment=True)


class Logs(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(
            primary_key=True,
            type_=BIGINT,  # autoincrement=True,server_default="always"
        ),
    )
    timestamp: datetime | None = Field(
        sa_type=TIMESTAMP(timezone=True),
    )
    name: str | None = Field(sa_type=VARCHAR)
    level: str | None = Field(sa_type=VARCHAR)
    message: str | None = Field(sa_type=Text)
