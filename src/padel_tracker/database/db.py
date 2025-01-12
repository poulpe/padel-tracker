import datetime
from uuid import UUID, uuid4

from sqlalchemy import Table, Column, String, ForeignKey, Float, DateTime, relationship
from sqlalchemy.orm import declarative_base

# from padel_tracker.models.players import Player, Team
# from padel_tracker.models.matches import Match, MatchScore


if __name__ == "__main__":
    Base = declarative_base()

    player_match_association = Table(
        "player_match",
        Base.metadata,
        Column("player_id", String, ForeignKey("players.id"), primary_key=True),
        Column("match_id", String, ForeignKey("matches.id"), primary_key=True),
    )

    class Player(Base):
        __tablename__ = "players"

        id = Column(String, primary_key=True, default=lambda: str(uuid4()))
        name = Column(String, nullable=False)
        elo = Column(Float, default=1000.0)
        created_at = Column(DateTime, default=datetime.datetime.now)

        # Relation avec les matchs
        matches = relationship(
            "Match",
            secondary=player_match_association,
            back_populates="players",
        )

    class Match(Base):
        __tablename__ = "matches"

        id = Column(String, primary_key=True, default=lambda: str(uuid4()))
        date = Column(DateTime, default=datetime.datetime.now)
        scores = Column(String, nullable=False)  # Exemple: "6-4, 7-5"

        # Relation avec les joueurs
        players = relationship(
            "Player",
            secondary=player_match_association,
            back_populates="matches",
        )
