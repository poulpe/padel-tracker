# Padel Tracker

Small app to keep track of Padel matches

## TODO

- Loggings
  - [x] Overall stuff
- UI
  - [x] Basic Streamlit tuto
  - [x] General layout
  - [ ] Graphs
  - [ ] **User auth / login/logout ?**
- Database
  - [ ] Deletes
  - [x] Migrations
  - [x] Get 'data' online
- Analytics
  - [ ] Best teammate
  - [ ] Best rival ?
  - [ ] nb_games per Match
  - [ ] Other stats (V/D ratio)
Like select player, it shows these analytics
Otherwise, show in overall : strongest team

- Features
  - [ ] Allow several leagues ?


## Database
### Migrations

Database migration = models changed, how to reflect it on current database "automatically"  
Migrations has been configured with `Alembic`

#### Use cases
0) Init 
```commandline
alembic revision --autogenerate -m "first revision"
alembic upgrade head
```

1) Anything has been changed to models
```commandline
alembic revision --autogenerate -m "added new_field to Player"
alembic upgrade head
```
