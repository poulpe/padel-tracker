# Padel Tracker

Small app to keep track of Padel matches

## Overview
Padel Tracker is a small app I made to keep track of Padel matches with my friends and to allow analysis of our progresses over time.  
It provides player rankings using an Elo-based system and maintains a history of matches, teams, and individual performances.

The application is hosted on **Streamlit Community Cloud**  
➡ **https://poulpe-padel-tracker.streamlit.app**  

      
<img src="docs/img/screenshot_main_page_en.png" width="66%" height="66%"> 

## Features
- **Player and Team Management**: Add, update, and check player and team statistics.
- **Match Tracking**: Record match results (date, teams, scores)
- **Elo Ranking System**: Calculate player rankings dynamically based on match results.
- **Match History**: Store and visualize the ranking evolution of players over time.
- **League Management**: Ability to group players within a league, to follow/compare only your mates (player can also belong to several leagues)
- **Data Persistence**: Uses a PostgreSQL database hosted on Supabase. Can also be used in `local` mode to avoid any need of hosting database online.
- **Interactive UI**: Built with Streamlit, providing an intuitive and responsive interface in a web browser.
- **Visualization**: Charts and tables for ranking history and match statistics.
- **Multilingual Support**: Users can switch between English and French.

## Technologies used
- **Backend**: [SQLModel](https://github.com/tiangolo/sqlmodel) (SQLAlchemy + Pydantic)
- **Frontend**: [Streamlit](https://streamlit.io/) with modular pages and navigation
- **Database**: PostgreSQL (Hosted on [Supabase](https://supabase.com/))
- **Database migrations**: Managed with [Alembic](https://alembic.sqlalchemy.org/)
- **Logging**: Logs are stored in Supabase for tracking application events

## Roadmap / Ideas
- Loggings
  - [x] Overall stuff
- UI
  - [x] Basic Streamlit tuto
  - [x] General layout
  - [ ] Graphs
  - [ ] **User auth / login/logout ?**
- Users
  - [ ] Manage users ? (authentification, access...)
- Database
  - [ ] Deletes
  - [x] Migrations
  - [x] Get 'data' online
- Analytics
  - [x] Best teammate
  - [x] Best rival ?
  - [x] nb_games per Match
  - [x] Other stats (V/D ratio)
    - [x] Like select player, it shows these analytics
- Extra features
  - [x] Allow several leagues
- Tests
  - [ ] Not the funniest part, but, eh...

## Gallery

| <img src="docs/img/screenshot_check_player_page_en2.png" width="90%" height="90%"> | <img src="docs/img/screenshot_main_page_dark_en.png" width="90%" height="90%"> |
|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|


---
# Some specifities

## Database
### Migrations

Database migration = models changed, how to reflect it on current database "automatically"  
Migrations has been configured with `Alembic`

#### Use cases
0) Init 
```shell
alembic revision --autogenerate -m "first revision"
alembic upgrade head
```

1) Anything has been changed to models
```shell
alembic revision --autogenerate -m "added new_field to Player"
alembic upgrade head
```

## Run locally and reproduce this app
### .env
To run the application locally, you need to set up environment variables in a .env file for secret management. 
Below is the required structure:
```text
# Run parameters
log_level_console=INFO
db_mode=local # "local" or "cloud"
run_mode=test # "test" or "prod"

# Cloud database related (not needed if you just run locally)
user=my_database_user 
password=my_database_password 
host=my_database_host 
port=my_database_port 
dbname=my_dbname
supabase_api_url=my_api_url
supabase_api_key=my_api_key
```
If you set `db_mode` to `local`, it will just create/read/update a local database in `data/` folder, so you don't need to have a database if you want to only do locally.

Note: secret management for the streamlit hosted app is done via the dedicated
[streamlit secret management method](https://docs.streamlit.io/develop/concepts/connections/secrets-management).  
The app is looking in priority if any `.streamlit/secrets.toml` file is defined,
otherwise it falls back to checking if an `.env` file is there.

### Run locally
1) Clone the repository
2) Make sure ``uv`` is installed on your setup
3) In a terminal, go to folder and run the project via typing this command:  
(it will install project automatically if not already installed)
```shell
uv run padel-tracker
```

Note: this actually runs the following command inside a venv:  
```streamlit run src/padel-tracker/ui/streamlit_app.py```

---
© 2025 Padel Tracker
