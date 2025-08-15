# Player errors
class PlayerExistsError(Exception):
    """Player already exists in database"""


class PlayerNotFoundError(Exception):
    """Player not found and probably doesn't exist in database"""


class InvalidPlayerNameError(Exception):
    """Player name is not valid : must have at least 2 alphabetical characters"""


# Team errors
class TeamExistsError(Exception):
    """Team already exists in database"""


class TeamNotFoundError(Exception):
    """Tean not found and probably doesn't exist in database"""


class SamePlayerInOneTeamError(Exception):
    """Same player have been selected to create 1 team"""


# Match errors
class MatchExistsError(Exception):
    """Match already exists in database"""


class MatchNotFoundError(Exception):
    """Match not found and probably doesn't exist in database"""


class MatchNotFinishedError(Exception):
    """Match score are not valid to determine winner/loser"""


class SamePlayerInBothTeamsError(Exception):
    """Same player is present in 2 competing teams, cannot duplicate people"""


# League errors
class LeagueExistsError(Exception):
    """League already exists in database"""


class LeagueNotFoundError(Exception):
    """League not found and probably doesn't exist in database"""


class InvalidLeagueNameError(Exception):
    """League name is not valid : must have at least 2 alphabetical characters"""


class PlayerNotInLeagueError(Exception):
    """Player is not part of the league"""


class PlayerAlreadyInLeagueError(Exception):
    """Player is already part of the league"""


# User errors
class UserNotFoundError(Exception):
    """User not found and probably doesn't exist in database"""


class UserExistsError(Exception):
    """User already exists in database"""


# Event errors
class EventExistsError(Exception):
    """Event already exists in database"""
