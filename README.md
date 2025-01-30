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
  - [x] Best teammate
  - [x] Best rival ?
  - [x] nb_games per Match
  - [x] Other stats (V/D ratio)
    - [x] Like select player, it shows these analytics
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
