class LeagueError(Exception):
    status = 400


class NotFound(LeagueError):
    status = 404
