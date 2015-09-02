#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()

def deleteTournaments():
    """Remove all the tournament records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM tournaments")
    DB.commit()
    DB.close()


def deleteScoreboard():
    """Remove all the scoreboard records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM scoreboard")
    DB.commit()
    DB.close()

def createTournament(name):
    """Create a new tournament.

    Args:
        Name of tournament
    """
    DB = connect()
    c = DB.cursor()
    sql = "INSERT INTO tournaments (name) VALUES (%s) RETURNING id"
    c.execute(sql, (name,))
    tid = c.fetchone()[0]
    DB.commit()
    DB.close()
    return tid

def countPlayers(tid):
    """Returns the number of players currently registered for a tournament.

    Args:
        tid: id of tournament
    """
    DB = connect()
    c = DB.cursor()
    sql = """SELECT count(player) AS num
             FROM scoreboard
             WHERE tournament = %s"""
    c.execute(sql, (tid,))
    players = c.fetchone()[0]
    DB.close()
    return players

def registerPlayer(name, tid):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
      tid: id of tournament they are entering.
    """
    DB = connect()
    c = DB.cursor()
    player = "INSERT INTO players (name) VALUES (%s) RETURNING id"
    scoreboard = "INSERT INTO scoreboard (tournament,player,score,matches,bye) VALUES (%s,%s,%s,%s,%s)"
    c.execute(player, (name,))
    playerid = c.fetchone()[0]
    c.execute(scoreboard, (tid,playerid,0,0,0))
    DB.commit()
    DB.close()


def playerStandings(tid):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
        tid: id of tournament getting standings for

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    players = """SELECT s.player, p.name, s.score, s.matches, s.bye,
                    (SELECT SUM(s2.score)
                     FROM scoreboard AS s2
                     WHERE s2.player IN (SELECT loser
                                     FROM matches
                                     WHERE winner = s.player
                                     AND tournament = %s)
                     OR s2.player IN(SELECT winner
                                 FROM matches
                                 WHERE loser = s.player
                                 AND tournament = %s)) AS owm
                 FROM scoreboard AS s
                 INNER JOIN players AS p on p.id = s.player
                 WHERE tournament = %s
                 ORDER BY s.score DESC, owm DESC, s.matches DESC"""
    c.execute(players, (tid,tid,tid))
    ranks = []
    for row in c.fetchall():
        ranks.append(row)
    DB.close()
    return ranks

def reportMatch(tid, winner, loser, draw='FALSE'):
    """Records the outcome of a single match between two players.

    Args:
      tid: the id of the tournament match was in
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw:  if the match was a draw
    """
    if draw == 'TRUE':
        w_points = 1
        l_points = 1
    else:
        w_points = 3
        l_points = 0

    DB = connect()
    c = DB.cursor()
    ins = "INSERT INTO matches (tournament, winner, loser, draw) VALUES (%s,%s,%s,%s)"
    win = "UPDATE scoreboard SET score = score+%s, matches = matches+1 WHERE player = %s AND tournament = %s"
    los = "UPDATE scoreboard SET score = score+%s, matches = matches+1 WHERE player = %s AND tournament = %s"
    c.execute(ins, (tid, winner, loser, draw))
    c.execute(win, (w_points, winner, tid))
    c.execute(los, (l_points, loser, tid))
    DB.commit()
    DB.close()

def hasBye(id, tid):
    """Checks if player has bye.

    Args:
        id: id of player to check

    Returns true or false.
    """
    DB = connect()
    c= DB.cursor()
    sql = """SELECT bye
             FROM scoreboard
             WHERE player = %s
             AND tournament = %s"""
    c.execute(sql, (id,tid))
    bye = c.fetchone()[0]
    DB.close()
    if bye == 0:
        return True
    else:
        return False

def reportBye(player, tid):
    """Assign points for a bye.

    Args:
      player: id of player who receives a bye.
      tid: the id of the tournament
    """
    DB = connect()
    c = DB.cursor()
    bye = "UPDATE scoreboard SET score = score+3, bye=bye+1 WHERE player = %s AND tournament = %s"
    c.execute(bye, (player,tid))
    DB.commit()
    DB.close()


def checkByes(tid, ranks, index):
    """Checks if players already have a bye

    Args:
        tid: tournament id
        ranks: list of current ranks from swissPairings()
        index: index to check

    Returns first id that is valid or original id if none are found.
    """
    if abs(index) > len(ranks):
        return -1
    elif not hasBye(ranks[index][0], tid):
        return index
    else:
        return checkByes(tid, ranks, (index - 1))

def validPair(player1, player2, tid):
    """Checks if two players have already played against each other

    Args:
        player1: the id number of first player to check
        player2: the id number of potentail paired player
        tid: the id of the tournament

    Return true if valid pair, false if not
    """
    DB = connect()
    c = DB.cursor()
    sql = """SELECT winner, loser
             FROM matches
             WHERE ((winner = %s AND loser = %s)
                    OR (winner = %s AND loser = %s))
             AND tournament = %s"""
    c.execute(sql, (player1, player2, player2, player1, tid))
    matches = c.rowcount
    DB.close()
    if matches > 0:
        return False
    return True

def checkPairs(tid, ranks, id1, id2):
    """Checks if two players have already had a match against each other.
    If they have, recursively checks through the list until a valid match is
    found.

    Args:
        tid: id of tournament
        ranks: list of current ranks from swissPairings()
        id1: player needing a match
        id2: potential matched player

    Returns id of matched player or original match if none are found.
    """
    if id2 >= len(ranks):
        return id1 + 1
    elif validPair(ranks[id1][0], ranks[id2][0], tid):
        return id2
    else:
        return checkPairs(tid, ranks, id1, (id2 + 1))

def swissPairings(tid):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
        tid: id of tournament you are gettings standings for

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ranks = playerStandings(tid)
    pairs = []

    numPlayers = countPlayers(tid)
    if numPlayers % 2 != 0:
        bye = ranks.pop(checkByes(tid, ranks, -1))
        reportBye(tid, bye[0])

    while len(ranks) > 1:
        validMatch = checkPairs(tid,ranks,0,1)
        player1 = ranks.pop(0)
        player2 = ranks.pop(validMatch - 1)
        pairs.append((player1[0],player1[1],player2[0],player2[1]))

    return pairs
