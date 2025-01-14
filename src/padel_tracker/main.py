#from padel_tracker.services.match_manager import MatchManager

from padel_tracker.database.db import create_db_and_tables, get_db_session, commit_to_db, read_from_db
from padel_tracker.models.players import Player
from padel_tracker.models.matches import Match
from padel_tracker.services.ranking_manager import update_players_results

#from padel_tracker.models.hero_trials import Hero
#
# def create_heroes():
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
#     hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
#
#     commit_to_db(hero_1, hero_2, hero_3)
#     #commit_to_db(hero_1)
#
#     print(f"hero_1.id = {hero_1.id}")

def create_players():
    p1 = Player(name="p1", elo_rating=1000)
    p2 = Player(name="p2", elo_rating=1000)
    p3 = Player(name="p3", elo_rating=1200)
    p4 = Player(name="p4", elo_rating=1300)

    commit_to_db(p1,p2,p3,p4)

def get_p2() -> Player:
    result = read_from_db(Player, where=Player.name=="p2", unique=True)
    return result


if __name__ == "__main__":
    # Creation
    # create_db_and_tables()
    # p1 = Player(name="p1", elo_rating=1000)
    # p2 = Player(name="p2", elo_rating=940, nb_matches=100)
    # p3 = Player(name="p3", elo_rating=1200)
    # p4 = Player(name="p4", elo_rating=1100, nb_matches=50)
    # commit_to_db(p1,p2,p3,p4)


    # Update a match
    p1:Player = read_from_db(Player, where=Player.name=="p1", unique=True)
    p2:Player = read_from_db(Player, where=Player.name=="p2", unique=True)
    p3:Player = read_from_db(Player, where=Player.name=="p3", unique=True)
    p4:Player = read_from_db(Player, where=Player.name=="p4", unique=True)

    print(f"INIT {p1.elo_rating = }")
    print(f"INIT {p2.elo_rating = }")
    print(f"INIT {p3.elo_rating = }")
    print(f"INIT {p4.elo_rating = }")

    match1 = Match(players=[p1,p2,p3,p4], score="6-4, 6-3")
    #match_id = match1.id
    #commit_to_db(match1)
    #match1:Match = read_from_db(Match, where=Match.id==match_id, unique=True)
    print(match1)
    winners, losers = match1.get_winners_losers()
    print(winners)

    update_players_results(match1)
    commit_to_db(match1)

    print(f"UPDATED {p1.elo_rating = }")
    print(f"UPDATED {p2.elo_rating = }")
    print(f"UPDATED {p3.elo_rating = }")
    print(f"UPDATED {p4.elo_rating = }")
    print(p1)

    p1:Player = read_from_db(Player, where=Player.name=="p1", unique=True)
    p2:Player = read_from_db(Player, where=Player.name=="p2", unique=True)
    p3:Player = read_from_db(Player, where=Player.name=="p3", unique=True)
    p4:Player = read_from_db(Player, where=Player.name=="p4", unique=True)

    print(f"UPDATED FROM DB {p1.elo_rating = }")
    print(f"UPDATED FROM DB {p2.elo_rating = }")
    print(f"UPDATED FROM DB {p3.elo_rating = }")
    print(f"UPDATED FROM DB {p4.elo_rating = }")

    print("END")