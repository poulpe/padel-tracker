from padel_tracker.services.match_manager import MatchManager

from padel_tracker.database.db_trials import create_db_and_tables, commit_to_db, read_from_db
from padel_tracker.models.hero_trials import Hero

def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    commit_to_db(hero_1, hero_2, hero_3)
    #commit_to_db(hero_1)

    print(f"hero_1.id = {hero_1.id}")

if __name__ == "__main__":
    create_db_and_tables()
    create_heroes()
    results = read_from_db(Hero, where = Hero.name=="Rusty-Man")
    print(results)
    print("END")