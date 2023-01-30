import requests
import time
from time import strftime, gmtime
import pandas as pd
from stqdm import stqdm
import streamlit as st


def get_puuid(summoner_name, region, api_key):
    # TODOC: need doc
    api_url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
        summoner_name +
        "?api_key=" +
        api_key
    )

    resp = requests.get(api_url)
    player_info = resp.json()
    puuid = player_info['puuid']
    return puuid


def get_match_ids(puuid, mass_region, no_games, queue_id, api_key):
    # NOTE: write note
    api_url = (
        "https://" +
        mass_region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid +
        "/ids?start=0" +
        "&count=" +
        str(no_games) +
        "&queue=" +
        str(queue_id) +
        "&api_key=" +
        api_key
    )

    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids


def get_match_data(match_id, mass_region, api_key):
    api_url = (
        "https://" +
        mass_region +
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id +
        "?api_key=" +
        api_key
    )

    # we need to add this "while" statement so that we continuously loop until it's successful
    while True:
        resp = requests.get(api_url)

        # whenever we see a 429, we sleep for 10 seconds and then restart from the top of the "while" loop
        if resp.status_code == 429:
            print("Rate Limit hit, sleeping for 10 seconds")
            time.sleep(10)
            # continue means start the loop again
            continue

        # if resp.status_code isn't 429, then we carry on to the end of the function and return the data
        match_data = resp.json()
        return match_data


def find_player_data(match_data, puuid):
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data


def get_total_kills(match_data, teamid):
    participants = match_data['info']['participants']
    kills = 0
    for participant in participants:
        if participant['teamId'] == teamid:
            kills += participant['kills']
    return kills


def get_recent_played_with(match_data, puuid, teamId):
    """
    Get data of recent played with summoner
    """
    play_with = []
    participants = match_data['info']['participants']
    for participant in participants:
        if participant['puuid'] != puuid and participant['teamId'] == teamId:
            play_with.append(participant['summonerName'])
    return play_with


def is_remake(match_data):
    participants = match_data['info']['participants']
    for participant in participants:
        if participant['teamEarlySurrendered'] == True:
            return True
    return False


def gather_all_data(puuid, match_ids, mass_region, api_key):

    data = {
        'champion': [],
        'champ_exp': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': [],
        'dmg_min': [],
        'dmg_total': [],
        'gold_min': [],
        'vision': [],
        'cs': [],
        'time': [],
        'first_blood': [],
        'team_kills': [],
        'play_with': []
    }

    if not match_ids:
        return None

    for match_id in stqdm(match_ids):

        # run the two functions to get the player data from the match ID
        match_data = get_match_data(match_id, mass_region, api_key)
        player_data = find_player_data(match_data, puuid)
        total_kills = get_total_kills(match_data, player_data['teamId'])
        play_with = get_recent_played_with(
            match_data, puuid, player_data['teamId'])

        # assign the variables we're interested in
        champion = player_data['championName']
        champ_exp = player_data['champExperience']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        if is_remake(match_data):
            win = None
        else:
            win = player_data['win']
        dmg_min = player_data['challenges']['damagePerMinute']
        dmg_total = player_data['totalDamageDealtToChampions']
        gold_min = player_data['challenges']['goldPerMinute']
        vision = player_data['visionScore']
        cs = player_data['totalMinionsKilled']
        time = player_data['timePlayed']
        first_blood = player_data['firstBloodKill']

        # add them to our dataset
        data['champion'].append(champion)
        data['champ_exp'].append(champ_exp)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)
        data['dmg_min'].append(dmg_min)
        data['dmg_total'].append(dmg_total)
        data['gold_min'].append(gold_min)
        data['vision'].append(vision)
        data['cs'].append(cs)
        data['time'].append(time)
        data['first_blood'].append(first_blood)
        data['team_kills'].append(total_kills)
        data['play_with'].append(play_with)

    df = pd.DataFrame(data)
    st.success(f"Extracted {len(df)} matches from your league!", icon="✅")

    return df


def master_function(summoner_name, region, mass_region, no_games, queue_id, api_key):
    puuid = get_puuid(summoner_name, region, api_key)
    match_ids = get_match_ids(puuid, mass_region, no_games, queue_id, api_key)
    df = gather_all_data(puuid, match_ids, mass_region, api_key)
    df.to_csv("df.csv", index=False)
    return df

# TODO: Statistics functionality


def basic(df):
    k = round(df['kills'].mean(), 1)
    d = round(df['deaths'].mean(), 1)
    a = round(df['assists'].mean(), 1)
    kda = round((k+a)/d, 2)

    team_kills = df['team_kills'].mean()
    p_kill = int(((k+a)/team_kills)*100)
    return k, d, a, kda, p_kill


def overview(df):
    winrate = str(int(df['win'].mean()*100)) + "%"

    df['dmg_min'] = df['dmg_min'].astype(int)
    dmg_min = round(df['dmg_min'].mean(), 1)

    df['gold_min'] = df['gold_min'].astype(int)
    gold_min = round(df['gold_min'].mean(), 1)

    k = df['kills'].mean()
    d = df['deaths'].mean()
    a = df['assists'].mean()
    kda = round((k+a)/d, 1)

    return winrate, kda, dmg_min, gold_min


def statistics(df):
    time = df['time'].mean()
    avg_time = strftime("%M:%S", gmtime(time))

    vision = round(df['vision'].mean(), 1)
    cs = df['cs'].mean()
    cs_per_min = round(cs/time, 1)

    first_blood = round(df['first_blood'].mean(), 1)

    return avg_time, vision, cs_per_min, first_blood


def champ_df(df):
    df['count'] = 1
    champ_df = df.groupby('champion').agg(
        {'kills': 'mean', 'deaths': 'mean', 'assists': 'mean', 'win': 'mean', 'count': 'sum'})
    champ_df.reset_index(inplace=True)

    champ_df['kda'] = round(
        (champ_df['kills'] + champ_df['assists']) / champ_df['deaths'], 2)
    champ_df['win'] = round(champ_df['win'], 2)*100
    return champ_df


def get_champ_pool(champ_df):
    return champ_df.sort_values('count', ascending=False)[:5]['champion'].to_list()
