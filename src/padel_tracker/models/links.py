from uuid import UUID

from pydantic import PositiveInt
from sqlmodel import SQLModel, Field, Relationship


class LinkPlayerMatch(SQLModel, table=True):
    player_id: UUID | None = Field(None, foreign_key="player.id", primary_key=True)
    match_id: UUID | None = Field(None, foreign_key="match.id", primary_key=True)


class LinkPlayerTeam(SQLModel, table=True):
    player_id: UUID | None = Field(None, foreign_key="player.id", primary_key=True)
    team_id: UUID | None = Field(None, foreign_key="team.id", primary_key=True)


class LinkTeamMatch(SQLModel, table=True):
    team_id: UUID | None = Field(None, foreign_key="team.id", primary_key=True)
    match_id: UUID | None = Field(None, foreign_key="match.id", primary_key=True)


class LinkLeagueMatch(SQLModel, table=True):
    league_id: UUID | None = Field(None, foreign_key="league.id", primary_key=True)
    match_id: UUID | None = Field(None, foreign_key="match.id", primary_key=True)


class LinkPlayerLeague(SQLModel, table=True):
    player_id: UUID = Field(foreign_key="player.id", primary_key=True)
    league_id: UUID = Field(foreign_key="league.id", primary_key=True)
    player: "Player" = Relationship(back_populates="league_links")
    league: "League" = Relationship(back_populates="player_links")
    player_name: str | None = Field(None, description="For convenience")
    league_name: str | None = Field(None, description="For convenience")
    # elo_rating: PositiveInt = Field(ELO_BASE_RATING, index=True)
    rank: PositiveInt | None = Field(None, index=True, description="Rank in the league")
    best_rank: PositiveInt | None = Field(
        None,
        description="Best achieved rank ever in the league",
        repr=True,
    )


class LinkTeamLeague(SQLModel, table=True):
    team_id: UUID | None = Field(None, foreign_key="team.id", primary_key=True)
    league_id: UUID | None = Field(None, foreign_key="league.id", primary_key=True)


class LinkLeagueadminUser(SQLModel, table=True):
    league_id: UUID | None = Field(None, foreign_key="league.id", primary_key=True)
    user_id: UUID | None = Field(None, foreign_key="user.id", primary_key=True)
