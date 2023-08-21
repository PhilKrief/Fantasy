import pandas as pd
import nfl_data_py as nfl
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import numpy as np

st.set_page_config(page_title="Fantasy App", page_icon=":football:", layout='wide')
st.markdown("<h1 style='text-align: center;'>Fantasy App</h1>", unsafe_allow_html=True)
# Get the data

def get_weekly_data(year, save_data=False):
    data = nfl.import_weekly_data([year])
    if save_data:
        data.to_excel('data.xlsx')
    return data

def get_schedule(year, save_data=False):
    schedule = nfl.import_schedules([year]).reset_index()
    if save_data:
        schedule.to_excel('schedule.xlsx')
    return schedule 

def get_clean_schedule(schedule_data, weekly_data, save_data=False):
    schedule = pd.DataFrame(columns= ['season','week', 'team', 'opponent', 'home', 'away', 'score', 'opponent_score', 'win', 'loss'])
    for week in weekly_data.week.unique():
        home = 0
        away = 0
        score = 0
        opponent_score = 0
        win = 0
        loss = 0
        for team in weekly_data.recent_team.unique():
            #filter through the schedule to get the opponent
            for i in range(len(schedule_data)):
                if (schedule_data.loc[i,'week'] == week) & ((schedule_data.loc[i,'away_team'] == team)):
                    opponent = schedule_data.loc[i, 'home_team']
                    home = 0
                    away = 1
                    score = schedule_data.loc[i, 'away_score']
                    opponent_score = schedule_data.loc[i, 'home_score']
                    if score > opponent_score:
                        win = 1
                        loss = 0
                    else:
                        win = 0
                        loss = 1
                    row_dict = {'season': 2022, 'week': week, 'team': team, 'opponent': opponent, 'home': home, 'away': away, 'score': score, 'opponent_score': opponent_score, 'win': win, 'loss': loss}
                    new_row = pd.DataFrame([row_dict])
                    schedule = pd.concat([schedule, new_row], ignore_index=True)
                elif (schedule_data.loc[i,'week'] == week) & (schedule_data.loc[i,'home_team'] == team):
                    opponent =  schedule_data.loc[i, 'away_team']
                    home = 1
                    away = 0
                    score = schedule_data.loc[i, 'home_score']
                    opponent_score = schedule_data.loc[i, 'away_score']
                    if score > opponent_score:
                        win = 1
                        loss = 0
                    else:
                        win = 0
                        loss = 1
                    
                    row_dict = {'season': 2022, 'week': week, 'team': team, 'opponent': opponent, 'home': home, 'away': away, 'score': score, 'opponent_score': opponent_score, 'win': win, 'loss': loss}
                    new_row = pd.DataFrame([row_dict])
                    schedule = pd.concat([schedule, new_row], ignore_index=True)
                else:
                    pass

    if save_data:
        schedule.to_excel('schedule_cleaned.xlsx')
    return schedule

def calculate_FIL(row):
    if row['position_group'] == 'QB':
        return row['fantasy_points_half_ppr'] - 17
    else:
        return row['fantasy_points_half_ppr'] - 8

cols_to_keep = ['player_id', 'player_name', 'player_display_name', 'position',
       'position_group', 'headshot_url', 'recent_team', 'season', 'week',
       'season_type', 'completions', 'attempts', 'passing_yards',
       'passing_tds', 'interceptions', 'sacks', 'sack_yards', 'sack_fumbles',
       'sack_fumbles_lost', 'passing_2pt_conversions', 'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles','rushing_fumbles_lost', 'rushing_2pt_conversions', 'receptions', 'targets', 'receiving_yards','receiving_tds', 'receiving_fumbles', 'receiving_fumbles_lost', 'receiving_2pt_conversions', 'target_share',  'fantasy_points', 'fantasy_points_ppr']

QB_cols = ['player_id', 'player_name', 'player_display_name', 'position',
       'position_group', 'headshot_url', 'recent_team', 'season', 'week',
       'season_type', 'completions', 'attempts', 'passing_yards',
       'passing_tds', 'interceptions', 'sacks', 'sack_yards', 'sack_fumbles',
       'sack_fumbles_lost', 'passing_2pt_conversions', 'fantasy_points', 'fantasy_points_ppr']  

pos_cols = ['player_id', 'player_name', 'player_display_name', 'position',
       'position_group', 'headshot_url', 'recent_team', 'season', 'week',
       'season_type', 'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles','rushing_fumbles_lost', 'rushing_2pt_conversions', 'receptions', 'targets', 'receiving_yards','receiving_tds', 'receiving_fumbles', 'receiving_fumbles_lost', 'receiving_2pt_conversions', 'target_share',  'fantasy_points', 'fantasy_points_ppr']

stats_cols = ['completions', 'attempts', 'passing_yards',
       'passing_tds', 'interceptions', 'sacks', 'sack_yards', 'sack_fumbles',
       'sack_fumbles_lost', 'passing_2pt_conversions', 'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles','rushing_fumbles_lost', 'rushing_2pt_conversions', 'receptions', 'targets', 'receiving_yards','receiving_tds', 'receiving_fumbles', 'receiving_fumbles_lost', 'receiving_2pt_conversions', 'target_share',  'fantasy_points', 'fantasy_points_ppr']

def clean_weekly_data(weekly_data):
    weekly_data = weekly_data.merge(clean_schedule, left_on=['recent_team','season','week'], right_on=['team', 'season', 'week'], how='left')
    #clean D.J. to DJ for display names
    weekly_data['player_display_name'] = weekly_data['player_display_name'].str.replace('D.J.', 'DJ')    
    #match names from weekly data to values
    for name in weekly_data.player_display_name.unique():
        for i in range(len(values)):
            #check if string is in the name
        
            if name in values.loc[i, 'Name']:
                weekly_data.loc[weekly_data['player_display_name'] == name, 'value'] = values.loc[i, 'value']

    player_mapping = weekly_data[['player_id', 'player_name', 'player_display_name','position_group', 'value']].drop_duplicates()
    st.session_state.player_mapping = player_mapping
    # filter weekly data by position
    weekly_data = weekly_data[weekly_data['season_type'] == 'REG']  # Only regular season games
    # add a 0.5 per reception to fantasy points
    weekly_data['fantasy_points_half_ppr'] = weekly_data['fantasy_points'] + (0.5 * weekly_data['receptions'])
    return weekly_data


def calculate_table(weekly_data):
    data_count = weekly_data.groupby(['player_id'])[['fantasy_points_half_ppr']].count().reset_index().rename(columns={'fantasy_points_half_ppr': 'games_played'})
    data_mean = weekly_data.groupby(['player_id'])[['fantasy_points_half_ppr']].mean().reset_index()
    data_mean = pd.merge(data_mean, data_count, on='player_id', how='left')
    data_mean = pd.merge(data_mean, player_mapping, on='player_id', how='left')
    data_mean = data_mean[['player_display_name', 'games_played', 'fantasy_points_half_ppr', 'position_group', 'value']]
    # filter out players with less than 5 games played
    data_mean = data_mean[data_mean['games_played'] >= 5]
    #check if "WR", "TE", or "RB" is in the pos list
    # Create a new column based on the 'position' column
    data_mean = data_mean[data_mean['position_group'].isin(pos)]
    data_mean['FIL'] = data_mean.apply(calculate_FIL, axis=1)
    data_mean['FILR'] = data_mean['FIL'] / data_mean['value']
    #replace NaN with 0 and inf with 0 in FILR  
    data_mean = data_mean.replace([np.inf, -np.inf], np.nan).fillna(0)

    float_columns = data_mean.select_dtypes(include=['float64']).columns
    data_mean[float_columns] = data_mean[float_columns].apply(lambda x: round(x, 3))
    data_mean['Pick'] = False
    data_mean = data_mean[['Pick', 'player_display_name', 'position_group', 'FIL', 'FILR', 'value','games_played', 'fantasy_points_half_ppr']]
    return data_mean




# Get the data
weekly_data = pd.read_excel('data.xlsx')
schedule_data= pd.read_excel('schedule.xlsx')
clean_schedule = pd.read_excel('schedule_cleaned.xlsx')
values = pd.read_excel('Prices.xlsx')

if "player_mapping" not in st.session_state:
    st.session_state.player_mapping = False
if "weekly_data" not in st.session_state:
    weekly_data = pd.read_excel('data.xlsx')
    st.session_state.weekly_data = clean_weekly_data(weekly_data)
    
    
else:
    print("esle")
    weekly_data = st.session_state.weekly_data
    player_mapping = weekly_data[['player_id', 'player_name', 'player_display_name','position_group', 'value']].drop_duplicates()
    print(weekly_data)
    print(player_mapping)


if "schedule_data" not in st.session_state:
    st.session_state.schedule_data = pd.read_excel('schedule.xlsx')
if "clean_schedule" not in st.session_state:
    st.session_state.clean_schedule =   pd.read_excel('schedule_cleaned.xlsx')
if "values" not in st.session_state:
    st.session_state.values = pd.read_excel('Prices.xlsx')


pos = st.multiselect('Select a position', weekly_data.position_group.unique(), default=['QB', 'RB', 'WR', 'TE'])
#def calculate_df(pos, weekly_data)

data_mean = calculate_table(weekly_data)

df = st.data_editor(data_mean, hide_index=True)

for index, row in df.iterrows():
    weekly_data.loc[weekly_data['player_display_name'] == row['player_display_name'], 'value'] = row['value']

st.session_state.weekly_data = weekly_data  
team = df[df['Pick'] == True]
# add a total row for value and fantasy_points_half_ppr
team.loc['Total'] = team[['value', 'fantasy_points_half_ppr']].sum()
st.dataframe(team)
