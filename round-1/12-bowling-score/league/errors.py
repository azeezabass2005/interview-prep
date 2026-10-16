class LeagueError(Exception):
    status = 400


class InvalidRoll(LeagueError):
    status = 400


class NotFound(LeagueError):
    status = 404
