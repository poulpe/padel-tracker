# from sqlmodel import Field, SQLModel
#
# # Define Hero model
# class Hero(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     secret_name: str
#     age: int | None = Field(default=None, index=True)
#     # Link to other tables
#     team_id: int | None = Field(default=None, foreign_key="team.id")
#
# class Team(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     headquarters: str