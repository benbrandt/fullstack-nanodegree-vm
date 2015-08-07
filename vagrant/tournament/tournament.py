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


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(id) as num from players")
    players = c.fetchone()[0]
    DB.close()
    return players

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    cmd = "INSERT INTO players (name,wins,matches,bye) VALUES (%s,%s,%s,%s)"
    c.execute(cmd, (name,0,0,0))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    c.execute("""SELECT id, name, wins, matches, bye
                 FROM players
                 ORDER BY wins, matches
              """)
    ranks = []
    for row in c.fetchall():
        ranks.append(row)
    DB.close()
    return ranks

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    ins = "INSERT INTO matches (winner, loser) VALUES (%s,%s)"
    win = "UPDATE players SET wins = wins+1, matches = matches+1 WHERE id = %s"
    los = "UPDATE players SET matches = matches+1 WHERE id = %s"
    c.execute(ins, (winner, loser))
    c.execute(win, (winner,))
    c.execute(los, (loser,))
    DB.commit()
    DB.close()

def hasBye(id):
    """Checks if player has bye.

    Args:
        id: id of player to check

    Returns true or false.
    """
    DB = connect()
    c= DB.cursor()
    sql = """SELECT bye
             FROM players
             WHERE id = %s"""
    c.execute(sql, (id,))
    bye = c.fetchone()[0]
    DB.close()
    if bye == 0:
        return True
    else:
        return False

def reportBye(player):
    """Assign points for a bye.

    Args:
      player: id of player who receives a bye.
    """
    DB = connect()
    c = DB.cursor()
    bye = "UPDATE players SET wins = wins+1, matches = matches+1, bye=bye+1 WHERE id = %s"
    c.execute(bye, (player,))
    DB.commit()
    DB.close()


def checkByes(ranks, index):
    """Checks if players already have a bye

    Args:
        ranks: list of current ranks from swissPairings()
        index: index to check

    Returns first id that is valid or original id if none are found.
    """
    if abs(index) > len(ranks):
        return -1
    elif hasBye(ranks[index][0]):
        return index
    else:
        checkByes(ranks, (index - 1))

def validPair(player1, player2):
    """Checks if two players have already played against each other

    Args:
        player1: the id number of first player to check
        player2: the id number of potentail paired player

    Return true if valid pair, false if not
    """
    DB = connect()
    c = DB.cursor()
    sql = """SELECT winner, loser
             FROM matches
             WHERE (winner = %s AND loser = %s)
             OR (winner = %s AND loser = %s)"""
    c.execute(sql, (player1, player2, player2, player1))
    matches = c.rowcount
    DB.close()
    if matches > 0:
        return False
    return True

def checkPairs(ranks, id1, id2):
    """Checks if two players have already had a match against each other.
    If they have, recursively checks through the list until a valid match is
    found.

    Args:
        ranks: list of current ranks from swissPairings()
        id1: player needing a match
        id2: potential matched player

    Returns id of matched player or original match if none are found.
    """
    if (id2 + 1) >= len(ranks):
        return id1
    elif validPair(ranks[id1][0], ranks[id2][0]):
        return id2 - 1
    else:
        checkPairs(ranks, id1, (id2 + 1))

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ranks = playerStandings()
    pairs = []

    numPlayers = countPlayers()
    if numPlayers % 2 != 0:
        bye = ranks.pop(checkByes(ranks, -1))
        reportBye(bye[0])

    while len(ranks) > 1:
        validMatch = checkPairs(ranks,0,1)
        player1 = ranks.pop(0)
        player2 = ranks.pop(validMatch)
        pairs.append((player1[0], player1[1],player2[0],player2[1]))
    return pairs
