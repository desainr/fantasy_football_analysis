import espnff as ff 
import requests as r 
import json
import pandas as pd 
import numpy as np
import sys
import argparse

league_id = '1271193'
year = 2018

swid = '{72206D48-3085-4FED-A06D-483085BFED52}'
s2 = 'AEBqvIGkUgNODsBXK7%2Fuunr1eKAs64cc4sD0YXntDYf75xmfUJzMMaRWwxnxjRA%2B2N%2FQtm%2BUGLUYjKpz4uJ6x3ZfaxA4%2FZgNcwWeo%2Bvmt9gEKl8sOAepOOe%2BHIV3vXa7UGe7vvd6QHyw2sOgBn%2BTjvWS7kaMJBntd9cNscc34Zcg%2Baed626JDxdI89c3HCrAUlJSGmiCCQKipcY9aah0mExsUj74TAkjrDizhi%2B0BU%2BYENEjCfatK6WKYAQoMCGNDqpiXAQAB90lbfi%2Byqv%2BJnT%2F'

slots = {0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE', 16: 'D/ST', 17: 'K', 20: 'BE', 23: 'FLEX'}

sbs = {}
bss = {}

print('Week', end=' ')

for week in range(1,18):
    print(week, end=' .. ')

    sb = r.get('http://games.espn.com/ffl/api/v2/scoreboard', params={'leagueId': league_id, 'seasonId': year, 'matchupPeriodId': week})
    sb = sb.json()
    sbs[week] = sb
    bss[week] = {}

    # loop through matchups that week
    for match in range(len(sb['scoreboard']['matchups'])):
        homeId = sb['scoreboard']['matchups'][match]['teams'][0]['team']['teamId']
    
        box = r.get('http://games.espn.com/ffl/api/v2/boxscore', params={'leagueId': league_id, 'seasonId': year, 'teamId': homeId, 'matchupPeriodId': week}, cookies={'SWID': swid, 'espn_s2': s2})
        boxscore = box.json()
        bss[week][match] = boxscore

df = pd.DataFrame(columns=['playerName', 'matchupPeriodId', 
                        'slotId', 'position', 'bye', 'weekly_pts', 'weekly_projected',
                        'teamAbbrev', 'wonMatchup'])
            
for week in range(1, 8):
    for match in range(len(sbs[week]['scoreboard']['matchups'])):
        homeId = sbs[week]['scoreboard']['matchups'][match]['teams'][0]['team']['teamId']
        winner = sbs[week]['scoreboard']['matchups'][match]['winner']
    
        # loop through home (0) and away (1)
        for team in range(2):
            # boolean for who won this matchup
            winb = False
            if (winner=='away' and team==1) or (winner=='home' and team==0):
                winb = True
        
            # fantasy team info (dict)
            tinfo = bss[week][match]['boxscore']['teams'][team]['team']
        
            # all players on that team info (array of dicts)
            ps = bss[week][match]['boxscore']['teams'][team]['slots']
        
            # loop through players
            for k,p in enumerate(ps):
                # players on bye/injured won't have this entry
                try:
                    pts = p['currentPeriodRealStats']['appliedStatTotal']
                    proj_pts = p['currentPeriodProjectedStats']['appliedStatTotal']
                except KeyError:
                    pts = 0
                    proj_pts = 0
                # there is some messiness in the json so just skip
                try:
                    # get player's position. this is a bit hacky...
                    pos = p['player']['eligibleSlotCategoryIds']
                    for s in [20, 23]:
                        if pos.count(s) > 0:
                            pos.remove(s)
                    pos = slots[pos[0]]
                
                    # add it all to the DataFrame
                    df = df.append({'playerName': p['player']['firstName'] + ' ' + p['player']['lastName'],
                                'matchupPeriodId': week,
                                'slotId': slots[p['slotCategoryId']],
                                'position': pos,
                                'bye': True if p['opponentProTeamId']==-1 else False,
                                'weekly_pts': pts,
                                'weekly_projected': proj_pts,
                                'teamAbbrev': tinfo['teamAbbrev'],
                                'wonMatchup': winb},
                                ignore_index=True)
                except KeyError:
                    continue

df.to_csv("2018_ff_stats.csv")
# stats_by_pos = df.groupby(['teamAbbrev', 'slotId'])['weekly_pts'].agg(np.mean)

# stats_df = stats_by_pos.to_frame()

# stats_df.columns.Name = None

# stats_df = stats_df.reset_index()

# stats_df = stats_df.pivot(index='teamAbbrev', columns='slotId', values='weekly_pts').reset_index()

# stats_df['Total'] = stats_df.drop(['BE', 'WR', 'RB'], axis=1).sum(axis=1)

# stats_df['Total'] += ((stats_df.WR * 2) + (stats_df.RB * 2))

# print(stats_df)


