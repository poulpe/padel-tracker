from uuid import UUID
from sqlmodel import SQLModel, Field


class LinkPlayerMatch(SQLModel, table=True):
    player_id: UUID | None = Field(None, foreign_key="player.id", primary_key=True)
    match_id: UUID | None = Field(None, foreign_key="match.id", primary_key=True)


class LinkPlayerTeam(SQLModel, table=True):
    player_id: UUID | None = Field(None, foreign_key="player.id", primary_key=True)
    team_id: UUID | None = Field(None, foreign_key="team.id", primary_key=True)


class LinkTeamMatch(SQLModel, table=True):
    team_id: UUID | None = Field(None, foreign_key="team.id", primary_key=True)
    match_id: UUID | None = Field(None, foreign_key="match.id", primary_key=True)
