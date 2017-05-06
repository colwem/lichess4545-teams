#! /usr/bin/env python
import random
import json
import re
import time

infile = open("s7test.json",'r')
playerdata = json.load(infile)
print "This data was read from file."
infile.close()
#print playerdata

class Player:
    pref_score = 0
    team = None
    board = None
    req_met = False
    def __init__(self, name, rating, friends):
        self.name = name
        self.rating = rating 
        self.friends = friends
    def __repr__(self):
        #return str((self.name, self.rating, self.friends, self.pref_score, self.team))
        #return str((self.name, [friend.name for friend in self.friends], self.pref_score))
        return str((self.name, self.board, self.rating, self.req_met))
    def setPrefScore(self):
        self.pref_score = 0
        for friend in self.friends:
            if friend in self.team.getBoards():
                self.pref_score += 1
            else:
                self.pref_score -= 1
        #player with more than 5 choices can be <5 preference even if all teammates are preferred
    def setReqMet(self):
        for friend in self.friends:
            if friend in self.team.getBoards():
                self.req_met = True
                friend.req_met = True
            else:
                self.req_met = False
class Team:
    def __init__(self):
        self.boards = [None,None,None,None,None,None]
    def __str__(self):
        return str((self.boards, self.team_pref_score, self.getMean()))
    def __repr__(self):
        return "Team:{0}".format(id(self))
    def changeBoard(self, board, new_player):
        #updates the player on a board and updates that player's team attribute
        if self.boards[board]:
            self.boards[board].team = None
        self.boards[board] = new_player
        if new_player.team:
            new_player.team.boards[board] = None
        new_player.team = self
    def getMean(self):
        ratings = [board.rating for board in self.boards]
        mean = sum(ratings) / len(ratings)
        return mean
    def getBoards(self):
        return self.boards
    def getPlayer(self, board):
        return self.boards[board]
    def setTeamPrefScore(self):
        self.team_pref_score = sum([x.pref_score for x in self.boards])

def updatePref(): #update preference scores
    for player in players:
        player.setPrefScore()
    for team in teams:
        team.setTeamPrefScore()
def updateSort(): #based on preference score high to low
    players.sort(key=lambda player: (player.team.team_pref_score, player.pref_score), reverse = False)
    teams.sort(key=lambda team: team.team_pref_score, reverse = False)

#Initial assignment to teams based on rating, boards alternate by descending and ascending rating order for balance.
players = []
for player in playerdata:
    players.append(Player(player['name'], player['rating'], player['friends']))
players.sort(key=lambda player: player.rating, reverse=True)
num_teams = ((len(players) - (len(players)%12)) / 6)
print("{0} deleted".format(len(players[num_teams*6:])))
del players[num_teams*6:]
players_split = [players[i:i + num_teams] for i in xrange(0, len(players), num_teams)]

for board in players_split[1::2]:
    board.reverse()
for n, board in enumerate(players_split):
    for player in board:
        player.board = n
teams = []
for n in xrange(num_teams):
    teams.append(Team())
for n, board in enumerate(players_split):
    for team, player in enumerate(board):
        teams[team].changeBoard(n, player)

#Convert players' friends from name to references of the friend's player object
for player in players:
    player.friends = re.split("[^a-zA-Z0-9]+", player.friends)
for player in players:
    temp_friends = []
    for friend in player.friends:
        for potentialfriend in players:
            if friend.lower() == potentialfriend.name.lower():
                temp_friends.append(potentialfriend)
    player.friends = temp_friends
for player in players:
    for friend in player.friends:
        if friend.board == player.board:
            player.friends.remove(friend)
updatePref() #update preference scores
updateSort()

def swapPlayers(teama, playera, teamb, playerb, board):
    #swap players function - ensure players are same board for input
    teama.changeBoard(board,playerb)
    teamb.changeBoard(board,playera)

def testSwap(teama, playera, teamb, playerb, board):
    prior_pref = teama.team_pref_score + teamb.team_pref_score
    swapPlayers(teama, playera, teamb, playerb, board) #swap players forwards
    updatePref()
    post_pref = teama.team_pref_score + teamb.team_pref_score
    swapPlayers(teama, playerb, teamb, playera, board) #swap players back
    updatePref()
    return post_pref - prior_pref #more positive = better swap
"""
total = 0
for team in teams:
    total += team.team_pref_score
print total
"""
#PLAN
#take player from least happy team. calculate the overall preference score if player were to swap to each of the preferences' teams or preference swaps into their team.
#swap player into the team that makes the best change to overall preference
#check if the swap has increased the OVERALL preference rating - need overall pref function
#if swap made, resort list and start at the least happy team again
#if no good swaps, go to next player. if end of list reached with no swaps, stop.
p = 0
while p<len(players):
    player = players[p] #least happy player
    friend_swaps = []
    for friend in player.friends:
        #test both swaps for each friend and whichever is better, add the swap ID and score to temp friends list
        #print repr(friend.team), friend.board, repr(player.team), player.board
        #print player.friends, friend
        if friend.board != player.board and friend.team != player.team:
            #print True
            #test swap friend to player team (swap1)
            swap1_ID = (friend.team, friend, player.team, player.team.getPlayer(friend.board), friend.board)
            swap1_score = testSwap(*swap1_ID)
            #test swap player to friend team (swap2)
            swap2_ID = (player.team, player, friend.team, friend.team.getPlayer(player.board), player.board)
            swap2_score = testSwap(*swap2_ID)
            #print max((swap1_score, swap1_ID),(swap2_score, swap2_ID))
            friend_swaps.append(max((swap1_score, swap1_ID),(swap2_score, swap2_ID)))
    friend_swaps.sort()
    if friend_swaps and friend_swaps[-1][0] > 0:
        swapPlayers(*(friend_swaps[-1][1]))
        print friend_swaps[-1]
        updatePref()
        updateSort()
        p = 0
    else:
        p += 1

for player in players:
    player.setReqMet()
#add rating balancing at the end to swap players with no preference
#order teams by average rating and swap an unwanted player from one to the other, if not possible, go in one team on one end
for team in teams:
    print team
"""
total = 0
for player in players:
    if player.friends and not set(player.friends).intersection(set(player.team.boards)):
        total += 1
        print player
print total
total = 0
for player in players:
    if player.friends:
        total += 1
print total
total = 0
for team in teams:
    print team
    total += 1
print total
total = 0
req = 0
for team in teams:
    total += team.team_pref_score
print total
for player in players:
    req += len(player.friends)
print req
for team in teams:
    print team
"""
