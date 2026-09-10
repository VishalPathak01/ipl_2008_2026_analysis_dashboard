import numpy as np 
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go 
import streamlit as st  
from pathlib import Path
st.set_page_config(page_title="IPL Dashboard", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_ROOT = BASE_DIR / "data"
DATA_DIR = DATA_ROOT / "ipl_dataset_2008-2026"

st.title('IPL 2008-2026 Analysis Dashboard ')
st.caption('Data displayed here is solely based on third party datasets publically available on Kaggle and used for educational and learning purpose only. please refer to the official sites for accurate and reliable information')

def fill_toss_decision(x):
    if pd.isna(x['toss_decision']):
        if not (pd.isna(x['win_by_runs']) & pd.isna(x['win_by_wickets'])):
            if x['toss_winner_won'] == 1:
                if pd.isna(x['win_by_runs']): # win by wickets
                    x['toss_decision'] = 'field'
                else : # win by runs 
                    x['toss_decision'] = 'bat'
            else :
                if pd.isna(x['win_by_runs']): # win by runs
                    x['toss_decision'] = 'bat'
                else : # win by wickets 
                    x['toss_decision'] = 'field'
        else :
            x['toss_decision'] = 'Not available'
    return x['toss_decision']

@st.cache_data
def load_matches(teams_data, players_data):
    matches = pd.read_csv(DATA_DIR / 'ipl_matches_data.csv', parse_dates=['match_date'])
    matches = matches.drop(columns=['gender', 'event_name', 'match_type', 'format', 'overs', 'team_type', 'match_number', 'season_id', 'balls_per_over'])
    
    # type Conversion
    matches['season'] = matches['season'].astype('string').str[:4].astype(np.int32)
    matches['bat_first_won'] = (matches['win_by_runs'] > 0).astype(int)
    matches["toss_winner_won"] = (matches["toss_winner"] == matches["match_winner"]).astype(int)
    matches['player_of_match'] = matches['player_of_match'].astype('Int32')
    matches['city'] = matches['city'].astype('string')
    matches['venue'] = matches['venue'].astype('category')
    matches['toss_decision'] = matches['toss_decision'].astype('category')
    matches['result'] = matches['result'].astype('category')
    
    # find toss_decision by result of the match
    matches['toss_decision'] = matches.apply(fill_toss_decision, axis=1).astype('category')
    
    # fill missng values
    matches['city'] = matches['city'].fillna('Unknown City')
    matches['player_of_match'] = matches['player_of_match'].fillna(-1)
    
    # Fix Unknown City
    matches.loc[(matches['match_date'] == '2020-09-20') & (matches['city'] == 'Unknown City'), 'city'] = 'Dubai'
    matches.loc[(matches['match_date'] == '2020-09-28') & (matches['city'] == 'Unknown City'), 'city'] = 'Dubai'
    matches.loc[(matches['match_date'] == '2020-10-18') & (matches['city'] == 'Unknown City') & (matches['team1'] == 'Mumbai Indians'), 'city'] = 'Dubai'

    # tie matches winner fixing
    matches.loc[(matches['match_date'] == '2009-04-23') & (matches['venue'] == 'Cape Town'), 'match_winner'] = 134
    matches.loc[(matches['match_date'] == '2010-03-21') & (matches['venue'] == 'Chennai'), 'match_winner'] = 494
    matches.loc[(matches['match_date'] == '2013-04-07') & (matches['venue'] == 'Hyderabad'), 'match_winner'] = 2
    matches.loc[(matches['match_date'] == '2013-04-16') & (matches['venue'] == 'Bangalore'), 'match_winner'] = 1
    matches.loc[(matches['match_date'] == '2014-04-29') & (matches['venue'] == 'Abu Dhabi'), 'match_winner'] = 134
    matches.loc[(matches['match_date'] == '2015-04-21') & (matches['venue'] == 'Ahmedabad'), 'match_winner'] = 494
    matches.loc[(matches['match_date'] == '2017-04-29') & (matches['venue'] == 'Rajkot'), 'match_winner'] = 3
    matches.loc[(matches['match_date'] == '2019-03-30') & (matches['venue'] == 'Delhi'), 'match_winner'] = 252
    matches.loc[(matches['match_date'] == '2019-05-02') & (matches['venue'] == 'Mumbai'), 'match_winner'] = 3
    matches.loc[(matches['match_date'] == '2020-09-20'), 'match_winner'] = 252
    matches.loc[(matches['match_date'] == '2020-09-28'), 'match_winner'] = 1
    matches.loc[(matches['match_date'] == '2020-10-18') & (matches['venue'] == 'Abu Dhabi'), 'match_winner'] = 6
    matches.loc[(matches['match_date'] == '2020-10-18') & (matches['venue'].str.contains('Dubai', na=False)), 'match_winner'] = 494
    matches.loc[(matches['match_date'] == '2021-04-25') & (matches['venue'] == 'Chennai'), 'match_winner'] = 252
    matches.loc[(matches['match_date'] == '2025-04-16'), 'match_winner'] = 252
    matches.loc[(matches['match_date'] == '2026-04-26'), 'match_winner'] = 6
    
    # load ipl 2026 matches data
    matches_2026 = pd.read_csv(DATA_ROOT / 'ipl_matches.csv', parse_dates=['start_date'])
    matches = matches[~(matches['match_date'].dt.year == 2026)] # delete the data of ipl 2026
    
    # mimic the original matches data
    matches_2026 = matches_2026[['match_id', 'city', 'start_date', 'season', 'venue', 'toss_winner', 'team1', 'team2', 'toss_decision', 'winner', 'win_by_runs', 'win_by_wickets', 'result', 'player_of_match']].rename(columns={'start_date':'match_date', 'winner':'match_winner'})
    
    # correct and convert the 'season'
    matches_2026['season'] = matches_2026['season'].str.strip().str[:4]
    matches_2026['season'] = matches_2026['season'].astype(int)
    
    #select only 2026 matches
    matches_2026 = matches_2026[matches_2026['season']==2026]
    # correct wrong info
    matches_2026.loc[(matches_2026['match_id'] == 1529281), 'match_winner'] = 'Kolkata Knight Riders'
    matches_2026.loc[(matches_2026['match_id'] == 1529281), 'result'] = 'Win'
    # filling missing values
    matches_2026['result'] = matches_2026['result'].fillna('win')
    matches_2026['player_of_match'] = matches_2026['player_of_match'].fillna('None')
    matches_2026['match_winner'] = matches_2026['match_winner'].fillna('No Winner(Match Abandoned)')
    
    # convert the type for merging with original data
    matches_2026['season'] = matches_2026['season'].astype('string').str[:4].astype(np.int32)
    matches_2026['bat_first_won'] = (matches_2026['win_by_runs'] > 0).astype(int)
    matches_2026["toss_winner_won"] = (matches_2026["toss_winner"] == matches_2026["match_winner"]).astype(int)
    matches_2026['player_of_match'] = matches_2026['player_of_match'].astype('string')
    matches_2026['city'] = matches_2026['city'].astype('string')
    matches_2026['toss_winner'] = matches_2026['toss_winner'].astype('string')
    matches_2026['team1'] = matches_2026['team1'].astype('string')
    matches_2026['team2'] = matches_2026['team2'].astype('string')
    matches_2026['match_winner'] = matches_2026['match_winner'].astype('string')
    matches_2026['venue'] = matches_2026['venue'].astype('category')
    matches_2026['toss_decision'] = matches_2026['toss_decision'].astype('category')
    matches_2026['result'] = matches_2026['result'].astype('category')
    
    # mergings to ensure names instead of plaeyers_id or team_id
    matches = matches.merge(teams_data, left_on='toss_winner', right_on='team_id', how='left').drop(columns=['team_id', 'toss_winner']).rename(columns={'team_name':'toss_winner'})
    matches = matches.merge(teams_data, left_on='team1', right_on='team_id', how='left').drop(columns=['team_id', 'team1']).rename(columns={'team_name':'team1'})
    matches = matches.merge(teams_data, left_on='team2', right_on='team_id', how='left').drop(columns=['team_id', 'team2']).rename(columns={'team_name':'team2'})
    matches = matches.merge(teams_data, left_on='match_winner', right_on='team_id', how='left').drop(columns=['team_id', 'match_winner']).rename(columns={'team_name':'match_winner'})
    matches = matches.merge(players_data, left_on='player_of_match', right_on='player_id', how='left').drop(columns=['player_id', 'player_of_match', 'bat_style', 'bowl_style', 'field_pos', 'player_full_name']).rename(columns={'player_name':'player_of_match'})
    
    # correct the format
    matches = matches[['match_id', 'city', 'match_date', 'season', 'venue', 'toss_winner', 'team1', 'team2', 'toss_decision', 'match_winner', 'win_by_runs', 'win_by_wickets', 'result', 'player_of_match', 'bat_first_won', 'toss_winner_won']]
    matches = pd.concat([matches, matches_2026])
    matches = matches.reset_index(drop=True)
    mask = (matches['match_date'].dt.year >= 2008) & (matches['match_date'].dt.year <= 2012)
    matches.loc[mask] = matches[mask].replace(to_replace='Sunrisers Hyderabad', value='Deccan Chargers')
    return matches 

@st.cache_data
def load_ballbyball():
    bbb = pd.read_csv(DATA_DIR / 'ball_by_ball_data.csv')
    
    # make innings_legal_balls
    bbb['is_legal_ball'] = (~bbb['is_wide_ball']) & (~bbb['is_no_ball'])
    bbb['is_legal_ball'] = bbb['is_legal_ball'].astype(int)
    temp_series = pd.Series([])
    for name, group in bbb.groupby(['match_id', 'innings']):
        temp_series = pd.concat([temp_series, group['is_legal_ball'].cumsum()])
    bbb['innings_legal_balls'] = temp_series
    
    # add 'is_dot' and 'is_boundary'
    bbb['is_dot'] = np.where((bbb['total_runs'] == 0), 1, 0)
    bbb['is_boundary'] = bbb.apply(lambda x: 1 if (x['batter_runs'] == 4 or x['batter_runs'] == 6) else 0, axis=1)
    
    # take out the necessary data only
    bbb = bbb.rename(columns={'season_id':'season', 'wicket_kind':'dismissal_kind'})
    bbb = bbb[['season', 'match_id', 'batter', 'bowler', 'non_striker', 'team_batting', 'team_bowling', 'over_number', 'ball_number', 'batter_runs', 'extras', 'total_runs', 'player_out', 'fielders_involved', 'is_wicket', 'is_boundary', 'is_dot', 'dismissal_kind', 'innings', 'innings_legal_balls']]
    
    # filling missing values
    bbb['player_out']        = bbb['player_out'].fillna('No One')
    bbb['fielders_involved'] = bbb['fielders_involved'].fillna('No One')

    # convert types
    bbb['batter']       = bbb['batter'].astype('string')
    bbb['bowler']       = bbb['bowler'].astype('string')
    bbb['non_striker']  = bbb['non_striker'].astype('string')
    bbb['player_out']   = bbb['player_out'].astype('string')
    
    bbb_2026 = pd.read_csv(DATA_ROOT / 'ipl_ballbyball_2026_sample.csv', parse_dates=['start_date'])
    bbb = bbb[~(bbb['season'] == 2026)] # delete data for 2026
    
    # miminc the original format
    bbb_2026 = bbb_2026[['season', 'match_id', 'batter', 'bowler', 'non_striker', 'batting_team', 'bowling_team', 'over', 'ball_in_over', 'runs_batter', 'runs_extras', 'runs_total', 'player_dismissed', 'fielders', 'is_wicket', 'is_boundary', 'is_dot', 'dismissal_kind', 'innings', 'innings_legal_balls']].rename(columns={'batting_team':'team_batting', 'bowling_team':'team_bowling', 'over':'over_number', 'ball_in_over':'ball_number', 'runs_batter':'batter_runs', 'runs_extras':'extras', 'runs_total':'total_runs', 'player_dismissed':'player_out', 'fielders':'fielders_involved'})
    
    #fill miss values
    bbb_2026['player_out']        = bbb_2026['player_out'].fillna('No One')
    bbb_2026['fielders_involved'] = bbb_2026['fielders_involved'].fillna('No One')
    
    # corection of names of team_batting and team_bowling
    bbb = bbb.merge(teams_data, left_on='team_batting', right_on='team_id', how='left').drop(columns=['team_batting', 'team_id']).rename(columns={'team_name':'team_batting'})
    bbb = bbb.merge(teams_data, left_on='team_bowling', right_on='team_id', how='left').drop(columns=['team_bowling', 'team_id']).rename(columns={'team_name':'team_bowling'})
    bbb['over_number'] = bbb['over_number']+1
    bbb['ball_number'] = bbb['ball_number']+1
    bbb = pd.concat([bbb, bbb_2026])
    bbb['phase'] = bbb.apply(lambda x: "PowerPlay" if x['over_number'] > 0 and x['over_number'] < 7 else "Death" if x['over_number'] >= 16 else "Middle", axis=1)
    
    bbb['batter'] = bbb['batter'].astype('string')
    bbb['bowler'] = bbb['bowler'].astype('string')
    bbb['non_striker'] = bbb['non_striker'].astype('string')
    bbb['player_out'] = bbb['player_out'].astype('string')
    bbb['dismissal_kind'] = bbb['dismissal_kind'].astype('category')
    bbb['team_batting'] = bbb['team_batting'].astype('string')
    bbb['team_bowling'] = bbb['team_bowling'].astype('string')
    bbb['phase'] = bbb['phase'].astype('category')
    return bbb
    
@st.cache_data
def load_players_data():
    players_data = pd.read_csv(DATA_DIR / 'players-data-updated.csv')
    
    # false entry for player name "Unknown"
    players_data.loc[len(players_data)] = [-1, 'Unknown','Unknown', 'Unknown', 'Unknown', 'Unknown'] 
    
    # fill Unknown for ' ' entries 
    players_data.loc[(players_data['bowl_style'] == ' '), 'bowl_style'] = 'Unknown'
    players_data.loc[(players_data['field_pos'] == ' '), 'field_pos'] = 'Unknown'

    # filling missing values
    players_data['bowl_style'] = players_data['bowl_style'].fillna('Unknown') 
    players_data['field_pos']  = players_data['field_pos'].fillna('Unknown') 

    # convert types 
    players_data['player_id'] = players_data['player_id'].astype(int)
    players_data['player_name'] = players_data['player_name'].astype('string')
    players_data['player_full_name'] = players_data['player_full_name'].astype('string') 
    players_data['field_pos'] = players_data['field_pos'].astype('category') 
    players_data['bowl_style'] = players_data['bowl_style'].astype('category') 
    players_data['bat_style'] = players_data['bat_style'].astype('category') 

    # fix duplicated  entries
    players_data.loc[players_data['bowl_style'] == 'Right arm Fast medium', 'bowl_style'] = 'Right arm Fast Medium'

    return players_data

@st.cache_data
def load_team_aliases():
    team_aliases = pd.read_csv(DATA_DIR / 'team_aliases.csv')
    team_aliases['alias_name'] = team_aliases['alias_name'].astype('string') # covert type 
    return team_aliases

@st.cache_data
def load_teams_data():
    teams_data = pd.read_csv(DATA_DIR / 'teams_data.csv')
    teams_data['team_name'] = teams_data['team_name'].astype('string')
    return teams_data

@st.cache_data
def get_finals(matches):
    idx = matches.groupby('season')['match_date'].idxmax()
    finals = matches.loc[idx].sort_values('season', ascending=False).reset_index()
    return finals

@st.cache_data
def load_player_match():
    pm = pd.read_csv(DATA_DIR / "players_matches_stat.csv", parse_dates=["match_date"])
    pm["fantasy_points"] = (
        pm["bat_runs"].fillna(0)
        + pm["bat_fours"].fillna(0)
        + 2 * pm["bat_sixes"].fillna(0)
        + 25 * pm["bowl_wickets"].fillna(0)
        + 8 * pm["catches"].fillna(0)
    )
    return pm

players_data = load_players_data()
teams_data = load_teams_data()
bbb = load_ballbyball()
matches = load_matches(teams_data, players_data)
finals = get_finals(matches)
team_aliases = load_team_aliases()
pm = load_player_match()

PAGES = [
    "Overview",
    "Match Profile",
    "Team Profile",
    "Player Profile",
    "Phase Analysis",
    "Fantasy Points",
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = PAGES[0]
if "jump_match_id" not in st.session_state:
    st.session_state.jump_match_id = None

def jump_to_match(match_id):
    st.session_state.jump_match_id = match_id
    st.session_state.nav_page = "Match Profile"
    
st.sidebar.title("IPL Analysis Dashboard ")
st.sidebar.caption(f"{len(matches)} matches | {matches['season'].nunique()} seasons | 2008-2026")
page = st.sidebar.radio("Navigate", PAGES, key="nav_page")
st.sidebar.divider()
st.title(page)

# OVERVIEW PAGE 
def render_overview():
    matches_comp = matches[matches["match_winner"].notna()]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(" Matches ", f"{len(matches):,}")
    c2.metric(" Seasons ", matches["season"].nunique())
    c3.metric(" Teams ", len(set(matches["team1"]) | set(matches["team2"])))
    c4.metric(" Venues ", matches["venue"].nunique())
    top_potm = matches["player_of_match"].value_counts()
    c5.metric("Most POTM Awards", top_potm.index[0], f"{top_potm.iloc[0]} awards")
        

    st.subheader("Matches per Season")
    season_counts = matches["season"].value_counts().sort_index()
    st.plotly_chart(px.bar(x=season_counts.index, y=season_counts.values,
                            labels={"x": "Season", "y": "Matches"}),
                     use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top 10 All Time High Win %")
        played = pd.concat([matches_comp["team1"], matches_comp["team2"]]).value_counts()
        won = matches_comp["match_winner"].value_counts()

        win_pct = (won / played * 100).round(1).sort_values(ascending=False)
        win_pct.name = "Win%"
        win_pct = win_pct.reset_index()
        win_pct.columns = ["Team", "Win%"]
        win_pct = win_pct.head(10)

        st.plotly_chart(
            px.bar(win_pct, x="Team", y="Win%"),
            use_container_width=True
        )
    with c2:
        st.subheader("Toss Win Match Win %")
        toss_pct = matches.groupby("season")["toss_winner_won"].mean() * 100
        fig = px.line(x=toss_pct.index, y=toss_pct.values, markers=True,
                       labels={"x": "Season", "y": "Toss winner won %"})
        fig.add_hline(y=50, line_dash="dash", annotation_text="coin-flip baseline")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("All Time Player of the Match Leaderboard")
        st.plotly_chart(px.bar(x=top_potm.head(10).index, y=top_potm.head(10).values,labels={"x": "Player", "y": "Player of the Match Awards"}),
                         use_container_width=True)
    with c2:
        st.subheader("Batting First vs Chasing")
        bat_first = int(matches_comp["bat_first_won"].sum())
        chase = len(matches_comp) - bat_first
        st.plotly_chart(px.pie(values=[bat_first, chase], names=["Batted First Won", "Chasing Won"]), use_container_width=True)

    st.subheader("Most Used Venues")
    venue_counts = matches["venue"].value_counts().sort_values(ascending=False).head(10)
    st.plotly_chart(px.bar(x=venue_counts.values, y=venue_counts.index, orientation="h",
                            labels={"x": "Matches", "y": "Venue"}),
                     use_container_width=True)

    st.subheader("All Finals")
    finals_display = finals.copy()
    finals_display["margin"] = finals_display.apply(
        lambda r: f"{int(r['win_by_runs'])} runs" if pd.notna(r["win_by_runs"]) and r["win_by_runs"] > 0
        else (f"{int(r['win_by_wickets'])} wickets" if pd.notna(r["win_by_wickets"]) else "N/A"),
        axis=1,
    )
    st.dataframe(
        finals_display[["season", "match_date", "team1", "team2", "match_winner", "margin", "venue", "player_of_match"]],
        use_container_width=True,
    )

    st.markdown("**Jump straight to a final's full match profile:**")
    finals_labels = finals_display.apply(
        lambda r: f"{r['team1']} vs {r['team2']} {r['season']}", axis=1
    )
    label_id_map = dict(zip(finals_labels, finals_display["match_id"]))
    label = st.selectbox("Select a final", finals_labels)
    st.button("View This Match", on_click=jump_to_match, args=(label_id_map[label],), key="jump_final")

    st.subheader("Overall Scoring Heatmap — Avg Runs by Over & Ball") 
    pivot = bbb.pivot_table(index="over_number", columns="ball_number", values="total_runs", aggfunc="mean").round(2)
    fig = px.imshow(pivot, text_auto=True, color_continuous_scale="YlOrRd", aspect="auto",
                     labels={'x':"Ball in Over", 'y':"Over", 'color':"Avg Runs"})
    st.plotly_chart(fig, use_container_width=True)
    ipl_winners = finals['match_winner'].value_counts().sort_values(ascending=True).reset_index()
    st.subheader("IPL Winners ")
    st.plotly_chart(px.bar(ipl_winners, x="count", y="match_winner", orientation='h', labels={'match_winner':'Winner', 'count':'Count'}))

# MATCH PROFILE PAGE
def render_innings(inn: pd.DataFrame, innings_num, batting_team, bowling_team):
    st.subheader(f"Innings {innings_num}:    {batting_team} batting    vs    {bowling_team} bowling")

    total_runs = int(inn["total_runs"].sum())
    wickets = int(inn["is_wicket"].sum())
    legal_balls = int(inn["innings_legal_balls"].max())
    overs_str = f"{legal_balls // 6}.{legal_balls % 6}"
    fours = int((inn["batter_runs"] == 4).sum())
    sixes = int((inn["batter_runs"] == 6).sum())
    run_rate = round(total_runs / (legal_balls / 6), 2) if legal_balls else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Runs", total_runs)
    c2.metric("Wickets", wickets)
    c3.metric("Overs", overs_str)
    c4.metric("Run Rate", run_rate)
    c5.metric("Fours", fours)
    c6.metric("Sixes", sixes)

    # --- heatmap: over * ball, runs, wickets marked with X  ---
    runs = inn.pivot_table(index="over_number", columns="ball_number", values="total_runs", aggfunc="sum")
    batters = inn.pivot(index='over_number', columns='ball_number', values="batter")
    bowlers = inn.pivot(index='over_number', columns='ball_number', values="bowler")
    customdata = np.dstack((batters, bowlers))
    wicket_balls = inn[inn["is_wicket"] == 1][["over_number", "ball_number"]]

    fig = go.Figure(data=go.Heatmap(
        z=runs.values, x=[str(c) for c in runs.columns], y=[str(i) for i in runs.index],
        colorscale="YlOrRd", text=runs.values, texttemplate="%{text}", showscale=True, customdata=customdata, hovertemplate=(
            "Over: %{y}<br>"+
            "Ball: %{x}<br>"+
            "batter: %{customdata[0]}<br>"+
            "bowler: %{customdata[1]}<br>"
        )
    ))
    if len(wicket_balls):
        fig.add_trace(go.Scatter(
            x=[str(v) for v in wicket_balls["ball_number"]],
            y=[str(v) for v in wicket_balls["over_number"]],
            mode="markers", marker=dict(symbol="x", size=10, color="black", line=dict(width=1)),
            name="Wicket", 
        ))
    fig.update_layout(title="Runs per Ball", xaxis_title="Ball in Over", yaxis_title="Over", height=650)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        category = inn["batter_runs"].apply(
            lambda r: "Dot" if r == 0 else ("Four" if r == 4 else ("Six" if r == 6 else f"{int(r)} run(s)"))
        )
        cat_counts = category.value_counts()
        st.plotly_chart(px.pie(values=cat_counts.values, names=cat_counts.index,
                                title=f"{batting_team} — Ball Outcomes"),
                         use_container_width=True)
    with c2:
        dismissals = inn[inn["is_wicket"] == 1]["dismissal_kind"].cat.remove_unused_categories().value_counts()
        if len(dismissals):
            st.plotly_chart(px.pie(values=dismissals.values, names=dismissals.index, title=f"{bowling_team} — Dismissal Types"), use_container_width=True)
        else:
            st.info("No wickets fell this innings.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Batting Scorecard**")
        bat = inn.groupby("batter").agg(
            runs=("batter_runs", "sum"),
            balls=("ball_number", "count"),
            fours=("batter_runs", lambda s: int((s == 4).sum())),
            sixes=("batter_runs", lambda s: int((s == 6).sum())),
        )
        bat["SR"] = (bat["runs"] / bat["balls"] * 100).round(1)
        st.dataframe(bat.sort_values("runs", ascending=False), use_container_width=True)
    with c2:
        st.markdown("**Bowling Figures**")
        bowl = inn.groupby("bowler").agg(
            balls=("ball_number", "count"),
            runs_conceded=("total_runs", "sum"),
            wickets=("is_wicket", "sum"),
        )
        bowl["economy"] = (bowl["runs_conceded"] / (bowl["balls"] / 6)).round(2)
        st.dataframe(bowl.sort_values("wickets", ascending=False), use_container_width=True)

def render_match_details(match_id):
    row = matches[matches["match_id"] == match_id]
    
    if row.empty:
        st.error("Match not found.")
        return
    row = row.iloc[0]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Winner", row["match_winner"] if pd.notna(row["match_winner"]) else "No Result")
    c2.metric("Toss Winner", f"{row['toss_winner']} ({row['toss_decision']})")
    c3.metric("Player of Match", row["player_of_match"] if pd.notna(row["player_of_match"]) else "N/A")
    c4.metric("City", row["city"] if pd.notna(row["city"]) else "N/A")
    c5.metric("Venue", row["venue"])

    match_bbb = bbb[bbb["match_id"] == match_id]
    if match_bbb.empty:
        st.info(
            "Ball-by-ball breakdown isn't available for this match — only the 2026 season "
            "has ball-by-ball data. This match is from an earlier season, so only the summary above is shown."
        )
        return

    for inn_num in sorted(match_bbb["innings"].unique()):
        inn = match_bbb[match_bbb["innings"] == inn_num]
        render_innings(inn, inn_num, inn["team_batting"].iloc[0], inn["team_bowling"].iloc[0])
        st.divider()
        
        
    ######################################################
    #@#####################################################
    st.subheader("Match Progression")
    progression_t = match_bbb.groupby(['innings', 'over_number'])['total_runs'].sum().reset_index()

    progression = pd.DataFrame()
    for name, group in progression_t.groupby('innings'):
        group['innings_runs'] = group['total_runs'].cumsum()
        progression = pd.concat([progression, group])
        
    progression["innings"] = progression["innings"].astype(str)
    st.plotly_chart(
        px.line(progression, x="over_number", y="innings_runs", color="innings", markers=True,
                title="Run Progression ", labels={"innings_runs": "Cumulative Runs", 'over_number':'over'}),
        use_container_width=True,
    )

    rpo = match_bbb.groupby(["innings", "over_number"])["total_runs"].sum().reset_index()
    rpo["innings"] = rpo["innings"].astype(str)
    st.plotly_chart(
        px.bar(rpo, x="over_number", y="total_runs", color="innings", barmode="group",
               title="Runs per Over", labels={"total_runs": "Runs", 'over_number':'over'}),
        use_container_width=True,
    )

def render_match_profile():
    if st.session_state.jump_match_id is not None:
        st.success("Showing the match you selected. Click below to search for a different one instead.")
        if st.button(" Search a different match"):
            st.session_state.jump_match_id = None
            st.rerun()
        render_match_details(st.session_state.jump_match_id)
        return

    st.markdown("Find a match: pick a season, then both teams, then the exact date.")
    c1, c2, c3 = st.columns(3)
    with c1:
        season = st.selectbox("Season", sorted(matches["season"].unique(), reverse=True))
    season_matches = matches[matches["season"] == season]
    teams_in_season = sorted(set(season_matches["team1"]) | set(season_matches["team2"]))
    with c2:
        team1 = st.selectbox("Team 1", teams_in_season)
    team2_options = [t for t in teams_in_season if t != team1]
    with c3:
        team2 = st.selectbox("Team 2", team2_options)

    pair_matches = season_matches[
        ((season_matches["team1"] == team1) & (season_matches["team2"] == team2))
        | ((season_matches["team1"] == team2) & (season_matches["team2"] == team1))
    ]

    if pair_matches.empty:
        st.warning(f"{team1} and {team2} didn't play each other in {season}.")
        return

    date_options = sorted(pair_matches["match_date"].dt.date.unique())
    date = st.selectbox("Match Date", date_options)
    chosen = pair_matches[pair_matches["match_date"].dt.date == date].iloc[0]

    st.divider()
    render_match_details(chosen["match_id"])


# TEAM PROFILE
def render_team_profile():
    all_teams = sorted(set(matches["team1"]) | set(matches["team2"]))
    default_idx = all_teams.index("Mumbai Indians") if "Mumbai Indians" in all_teams else 0
    team = st.selectbox("Select a team", all_teams, index=default_idx)

    team_matches = matches[(matches["team1"] == team) | (matches["team2"] == team)]
    team_comp = team_matches[team_matches["match_winner"].notna()]
    wins = int((team_comp["match_winner"] == team).sum())
    losses = len(team_comp) - wins
    titles = int((finals["match_winner"] == team).sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Matches Played", len(team_matches))
    c2.metric("Wins", wins)
    c3.metric("Losses", losses)
    c4.metric("Win %", f"{round(wins / len(team_comp) * 100, 1)}%" if len(team_comp) else "N/A")
    c5.metric("Titles Won", titles)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"{team} — Win % by Season")
        season_record = team_comp.groupby("season").apply( # type: ignore
            lambda g: round((g["match_winner"] == team).mean() * 100, 1), include_groups=False # type: ignore
        ) # type: ignore
        st.plotly_chart(px.line(x=season_record.index, y=season_record.values, markers=True,
                                 labels={"x": "Season", "y": "Win %"}),
                         use_container_width=True)
    with c2:
        st.subheader(f"{team} — Toss Decision ")
        toss_won = team_matches[team_matches["toss_winner"] == team]
        decision_counts = toss_won["toss_decision"].value_counts()
        if len(decision_counts):
            st.plotly_chart(px.pie(values=decision_counts.values, names=decision_counts.index),
                             use_container_width=True)
        else:
            st.info("No toss data available.")

    st.subheader("Head-to-Head")
    opponents = sorted(set(all_teams) - {team})
    opponent = st.selectbox("Select an opponent", opponents)
    h2h = team_comp[(team_comp["team1"] == opponent) | (team_comp["team2"] == opponent)]
    h2h_wins = int((h2h["match_winner"] == team).sum())
    h2h_losses = len(h2h) - h2h_wins
    c1, c2, c3 = st.columns(3)
    c1.metric(f"{team} wins", h2h_wins)
    c2.metric(f"{opponent} wins", h2h_losses)
    c3.metric("Total encounters", len(h2h))

    st.subheader(f"{team} — Venue Records ")
    venue_record = team_comp.groupby("venue").apply(  # type: ignore
        lambda g: pd.Series({"matches": len(g), "win_pct": round((g["match_winner"] == team).mean() * 100, 1)}),
        include_groups=False, # type: ignore
    )
    venue_record = venue_record[venue_record["matches"] >= 3].sort_values("win_pct", ascending=False)
    if len(venue_record):
        c1, c2 = st.columns(2)
        c1.metric("Best Venue", venue_record.index[0], f"{venue_record.iloc[0]['win_pct']}% win rate")
        c2.metric("Worst Venue", venue_record.index[-1], f"{venue_record.iloc[-1]['win_pct']}% win rate")
    st.dataframe(venue_record, use_container_width=True)

    st.subheader(f"All {team} Matches")
    search_season = st.multiselect("Filter by season", sorted(team_matches["season"].unique(), reverse=True))
    display = team_matches if not search_season else team_matches[team_matches["season"].isin(search_season)]
    def fill(x):
        if pd.isna(x['win_by_runs']) & pd.isna(x['win_by_wickets']):
            return "N/A"
        elif pd.isna(x['win_by_runs']):
            return str(int(x['win_by_wickets'])) + " Wickets"
        else:
            return str(int(x['win_by_runs'])) + " Runs"
    display["margin"] = display.apply(fill, axis=1)
    st.dataframe(
        display[["season", "match_date", "team1", "team2", "match_winner", "venue", "city", "player_of_match", "margin"]].sort_values("match_date", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )
    st.divider()
    st.subheader(f"{team}'s Players")
    
    team_data_batting = bbb[(bbb['season'] > 2025) & (bbb['team_batting'] == team)]
    team_data_bowling = bbb[(bbb['season'] > 2025) & (bbb['team_bowling'] == team)]
    all_players1 = team_data_batting['batter'].value_counts().reset_index()
    all_players2 = team_data_bowling['bowler'].value_counts().reset_index()

    all_players = all_players1.merge(all_players2, left_on='batter', right_on='bowler', how='outer')
    all_players['player'] = np.where(all_players['batter'].isna(), all_players['bowler'], all_players['batter'])
    all_players['count'] = all_players['count_x'].fillna(0) + all_players['count_y'].fillna(0)
    all_players = all_players.drop(columns=['count_x', 'count_y', 'batter', 'bowler'])
    all_players = all_players.sort_values('count', ascending=False)
    all_players = all_players.merge(pm[['player', 'estimated_role']], on='player', how='inner').drop_duplicates(subset=['player', 'count'])
    all_players = all_players.sort_values(by=['estimated_role', 'count'], ascending=False).reset_index(drop=True)
    batting_players = all_players[all_players['estimated_role'] == "Batsman"]
    bowling_players = all_players[all_players['estimated_role'] == "Bowler"]
    all_rounder_players = all_players[all_players['estimated_role'] == "All Rounder"]
    bowling_players = bowling_players.merge(pm[['player', 'bowl_style', 'player_full_name']], on='player', how='left').drop_duplicates(subset=['player', 'count'])
    batting_players = batting_players.merge(pm[['player', 'bat_style', 'player_full_name']], on='player', how='left').drop_duplicates(subset=['player', 'count'])
    all_rounder_players = all_rounder_players.merge(pm[['player', 'bat_style', 'bowl_style', 'player_full_name']], on='player', how='left').drop_duplicates(subset=['player', 'count'])
    batting_players = batting_players.iloc[:7, :]
    bowling_players = bowling_players.iloc[:7, :]
    all_rounder_players = all_rounder_players.iloc[:5, :]
    
    if batting_players.shape[0] > 0:
        st.subheader("Current leading batsman")
        for col, i in zip(st.columns(batting_players.shape[0]), range(batting_players.shape[0])):
            with col:
                st.image(
                    DATA_ROOT / "images" / "batsman_image_icon.webp",
                    caption=f"{batting_players.iloc[i, :]['player']} \n\n {batting_players.iloc[i, :]['bat_style']}",
                    width=150
                )
                
    if all_rounder_players.shape[0] > 0:
        st.subheader("Current leading All Rounders")
        for col, i in zip(st.columns(all_rounder_players.shape[0]), range(all_rounder_players.shape[0])):
            with col:
                st.image(
                    DATA_ROOT / "images" / "all_rounder_image_icon.jpg",
                    caption=f"{all_rounder_players.iloc[i, :]['player']} \n\n {all_rounder_players.iloc[i, :]['bat_style']} \n\n {all_rounder_players.iloc[i, :]['bowl_style']}",
                    width=150
                )    
                
    if bowling_players.shape[0] > 0:
        st.subheader("Current leading bowler")
        for col, i in zip(st.columns(bowling_players.shape[0]), range(bowling_players.shape[0])):
            with col:
                st.image(
                    DATA_ROOT / "images" / "bowling_image_icon.jpg",
                    caption=f"{bowling_players.iloc[i, :]['player']} \n\n {bowling_players.iloc[i, :]['bowl_style']}",
                    width=150
                )
    

# PLAYER PROFILE
def player_summary(player):
    p_data = pm[pm["player"] == player].sort_values("match_date")
    role = p_data['estimated_role'].iloc[0]
    return p_data, role

def render_player_profile():
    all_players = sorted(pm["player"].unique())
    player = st.selectbox("Select a player", all_players)
    p_data, role = player_summary(player)

    st.subheader(f"Player --    {p_data['player_full_name'].iloc[0]}")
    c0, c1, c2, c3, c4, = st.columns(5)
    c0.metric("Estimated Role ", role)
    c1.metric("Matches", p_data["match_id"].nunique())
    c2.metric("Runs", int(p_data["bat_runs"].sum()))
    c3.metric("Wickets", int(p_data["bowl_wickets"].sum()))
    c4.metric("Catches", int(p_data["catches"].sum()))
    
    if role == 'Batsman':
        st.subheader("Batting — Match by Match")
        bat_data = p_data[p_data['bat_balls'] > 0]
        st.plotly_chart(
            px.bar(bat_data, x="match_date", y="bat_runs", hover_data=["opponent", "bat_strike_rate"],
                   labels={"match_date": "Match Date", "bat_runs": "Runs"}),
            use_container_width=True,
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Highest runs", int(bat_data["bat_runs"].max()))
        c2.metric("Avg runs", round(bat_data["bat_runs"].mean(), 1))
        avg_sr = bat_data["bat_strike_rate"].mean()
        c3.metric("Avg Strike Rate", round(avg_sr, 1) if pd.notna(avg_sr) else "N/A")
        c4.metric("50s", int(p_data["half_century"].sum()))
        c5.metric("100s", int(p_data["century"].sum()))

        # ball-outcome pie from ball-by-ball, if this player appears as a batter there
        batter_balls = bbb[bbb["batter"] == player]
        if len(batter_balls):
            category = batter_balls["batter_runs"].apply(
                lambda r: "Dot" if r == 0 else ("Four" if r == 4 else ("Six" if r == 6 else f"{int(r)} run"))
            )
            st.plotly_chart(px.pie(values=category.value_counts().values, names=category.value_counts().index,
                                    title=f"{player} — Batting Run Distribution "),
                             use_container_width=True)

    elif role == 'Bowler':
        st.subheader("Bowling — Match by Match")
        bowl_data = p_data[p_data["bowl_balls"] > 0]
        st.plotly_chart(
            px.bar(bowl_data, x="match_date", y="bowl_wickets", hover_data=["opponent", "bowl_economy"],
                   labels={"match_date": "Match Date", "bowl_wickets": "Wickets"}),
            use_container_width=True,
        )
        c1, c2 = st.columns(2)
        c1.metric("Best Bowling", int(bowl_data["bowl_wickets"].max()) if len(bowl_data) else "N/A")
        c2.metric("Avg Economy", round(bowl_data["bowl_economy"].mean(), 2) if len(bowl_data) else "N/A")
        
        # ball-outcome pie from ball-by-ball, if this player appears as a batter there
        bowler_balls = bbb[bbb["bowler"] == player]
        if len(bowler_balls):
            category = bowler_balls["total_runs"].apply(
                lambda r: "Dot" if r == 0 else ("Four" if r == 4 else ("Six" if r == 6 else f"{int(r)} run"))
            )
            st.plotly_chart(px.pie(values=category.value_counts().values,names=category.value_counts().index,
            title=f"{player} — Bowling Run Distribution "),use_container_width=True)
    
    elif role == "All Rounder":
        # batting performance
        st.subheader("Batting — Match by Match")
        bat_data = p_data[p_data['bat_balls'] > 0]
        st.plotly_chart(
            px.bar(bat_data, x="match_date", y="bat_runs", hover_data=["opponent", "bat_strike_rate"],
                    labels={"match_date": "Match Date", "bat_runs": "Runs"}),
            use_container_width=True,
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Highest runs", int(bat_data["bat_runs"].max()))
        c2.metric("Avg runs", round(bat_data["bat_runs"].mean(), 1))
        avg_sr = bat_data["bat_strike_rate"].mean()
        c3.metric("Avg Strike Rate", round(avg_sr, 1) if pd.notna(avg_sr) else "N/A")
        c4.metric("50s", int(p_data["half_century"].sum()))
        c5.metric("100s", int(p_data["century"].sum()))
        
        # bowling performance
        st.subheader("Bowling — Match by Match")
        bowl_data = p_data[p_data["bowl_balls"] > 0]
        st.plotly_chart(
            px.bar(
                bowl_data, x="match_date", y="bowl_wickets", hover_data=["opponent", "bowl_economy"], labels={"match_date": "Match Date", "bowl_wickets": "Wickets"}
            ),
            use_container_width=True,
        )
        c1, c2 = st.columns(2)
        c1.metric("Best Bowling", int(bowl_data["bowl_wickets"].max()) if len(bowl_data) else "N/A")
        c2.metric("Avg Economy", round(bowl_data["bowl_economy"].mean(), 2) if len(bowl_data) else "N/A")
        
        # ball-outcome pie from ball-by-ball, if this player appears as batter there
        c1, c2 = st.columns(2)
        with c1:
            batter_balls = bbb[bbb["batter"] == player]
            if len(batter_balls):
                category = batter_balls["batter_runs"].apply(
                    lambda r: "Dot" if r == 0 else ("Four" if r == 4 else("Six" if r == 6 else f"{int(r)} run"))
                )
                st.plotly_chart(px.pie(values=category.value_counts().values, names=category.value_counts().    index, title=f"{player} — Batting RuDistribution "),
                use_container_width=True)
        
        # ball-outcome pie from ball-by-ball, if this player appears as a batter there
        with c2:
            bowler_balls = bbb[bbb["bowler"] == player]
            if len(bowler_balls):
                category = bowler_balls["total_runs"].apply(
                    lambda r: "Dot" if r == 0 else ("Four" if r == 4 else ("Six" if r == 6 else f"{int(r)} run"))
                )
                st.plotly_chart(px.pie(values=category.value_counts().values,names=category.value_counts().index, title=f"{player} — Bowling Run Distribution "),use_container_width=True)
            

    st.subheader("Performance vs Each Opponent")
    vs_team = p_data.groupby("opponent").agg(
        matches=("match_id", "nunique"), runs=("bat_runs", "sum"), wickets=("bowl_wickets", "sum"),
        Half_Century=('half_century', 'sum'),
        Century=('century', 'sum')
    ).sort_values("runs", ascending=False)
    st.dataframe(vs_team, use_container_width=True)

    st.subheader("All Matches")
    st.dataframe(
        p_data[["match_date", "team", "opponent", "bat_runs", "bat_balls", "bowl_wickets",
                "bowl_economy", "catches", "fantasy_points"]],
        use_container_width=True,
    )

    st.divider()
    st.subheader("Compare Two Players")
    c1, c2 = st.columns(2)
    with c1:
        player_a = st.selectbox("Player A", all_players, index=all_players.index(player), key="cmp_a")
    with c2:
        player_b = st.selectbox("Player B", all_players, index=(all_players.index(player) + 1) % len(all_players), key="cmp_b")

    players = set([player_a, player_b])
    players_data = pm[pm['player'].isin(players)]

    players_data = players_data.groupby('player').agg(
        Matches=('match_id', 'count'),
        Runs=('bat_runs', 'sum'),
        Avg_Runs=('bat_runs', 'mean'),
        Avg_Strike_Rate=('bat_strike_rate', 'mean'),
        Highest_Runs=('bat_runs', 'max'),
        Wickets=('bowl_wickets', 'sum'),
        Avg_Wickets_Per_Match=('bowl_wickets', 'mean'),
        Avg_Bowl_Econ=('bowl_economy', 'mean'),
        Best_bowling_w=('bowl_wickets', 'max'),
        Best_bowling_e=('bowl_economy', 'min'),
        Catches=('catches', 'sum')
    )
    
    players_data['best_bowling'] = (players_data['Best_bowling_w'].astype('string') + "/" + players_data['Best_bowling_e'].astype('string'))

    players_data['Avg_Bowl_Econ'] = np.round(players_data['Avg_Bowl_Econ'], 2)
    players_data['Avg_Runs'] = np.round(players_data['Avg_Runs'], 2)
    players_data['Avg_Strike_Rate'] = np.round(players_data['Avg_Strike_Rate'], 2)
    players_data['Avg_Wickets_Per_Match'] = np.round(players_data['Avg_Wickets_Per_Match'], 2)

    players_data = players_data.reset_index().drop(columns=['Best_bowling_w', 'Best_bowling_e'])
    temp = players_data[['player', 'Matches', 'Runs', 'Wickets', 'Catches']].melt(id_vars='player').sort_values(by='variable')

    st.plotly_chart((px.bar(temp, x='variable', y='value', barmode='group',
                        color='player', category_orders={
                            'variable':['Matches', 'Runs', 'Wickets','Catches']
                    })
    ),use_container_width=True)
    players_data = players_data.set_index('player').stack().swaplevel(0).unstack()
    players_data.index.name='Parameters'
    st.dataframe(players_data, use_container_width=True)

    allPlayersOverall = pm.groupby(['player', 'estimated_role']).agg(
        strike_rate=("bat_strike_rate", "mean"),
        avg_runs=("bat_runs", "mean"),
        experience=('match_id', 'count'),
        player_name=('player_full_name', 'first')
    ).reset_index()
    allPlayersOverall = allPlayersOverall[allPlayersOverall['experience'] > 5]
    st.plotly_chart(px.scatter(allPlayersOverall, x="strike_rate", y="avg_runs", hover_name="player_name", color="estimated_role", size="experience"), use_container_width=True)
    st.info('players having played matches less than 5 were excluded')

# PHASE PROFILE 
def render_phase_analysis():
    
    phase_stats = bbb.groupby("phase").agg(
        balls=("innings_legal_balls", "count"), runs=("total_runs", "sum"), wickets=("is_wicket", "sum"),
        boundary_pct=("is_boundary", "mean"), dot_pct=("is_dot", "mean"),
    )
    phase_stats["run_rate"] = (phase_stats["runs"] / (phase_stats["balls"] / 6)).round(2)
    phase_stats["boundary_pct"] = (phase_stats["boundary_pct"] * 100).round(1)
    phase_stats["dot_pct"] = (phase_stats["dot_pct"] * 100).round(1)
    phase_stats = phase_stats.reindex(["PowerPlay", "Middle", "Death"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Run Rate by Phase")
        st.plotly_chart(px.bar(x=phase_stats.index, y=phase_stats["run_rate"],
                                labels={"x": "Phase", "y": "Run Rate"}),
                         use_container_width=True)
    with c2:
        st.subheader("Boundary % vs Dot %")
        fig = go.Figure()
        fig.add_bar(x=phase_stats.index, y=phase_stats["boundary_pct"], name="Boundary %")
        fig.add_bar(x=phase_stats.index, y=phase_stats["dot_pct"], name="Dot %")
        fig.update_layout(barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(phase_stats, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("A Batter's Phase-wise Strike Rate")
        batters = sorted(bbb["batter"].dropna().unique())
        batter = st.selectbox("Select a batter", batters, key="phase_batter")
        b_data = bbb[bbb["batter"] == batter]
        b_phase = b_data.groupby("phase").agg(balls=("innings_legal_balls", "count"), runs=("batter_runs", "sum"))
        b_phase["strike_rate"] = (b_phase["runs"] / b_phase["balls"] * 100).round(1)
        b_phase = b_phase.reindex([p for p in ["PowerPlay", "Middle", "Death"] if p in b_phase.index])
        st.plotly_chart(px.bar(x=b_phase.index, y=b_phase["strike_rate"],
                                labels={"x": "Phase", "y": "Strike Rate"}),
                         use_container_width=True)
        st.dataframe(b_phase, use_container_width=True)
    with c2:
        st.subheader("A Bowler's Phase-wise Economy")
        bowlers = sorted(bbb["bowler"].dropna().unique())
        bowler = st.selectbox("Select a bowler", bowlers, key="phase_bowler")
        bo_data = bbb[bbb["bowler"] == bowler]
        bo_phase = bo_data.groupby("phase").agg(balls=("innings_legal_balls", "count"), runs_conceded=("total_runs", "sum"), wickets=("is_wicket", "sum"))
        bo_phase["economy"] = (bo_phase["runs_conceded"] / (bo_phase["balls"] / 6)).round(2)
        bo_phase = bo_phase.reindex([p for p in ["PowerPlay", "Middle", "Death"] if p in bo_phase.index])
        st.plotly_chart(px.bar(x=bo_phase.index, y=bo_phase["economy"],
                                labels={"x": "Phase", "y": "Economy"}),
                         use_container_width=True)
        st.dataframe(bo_phase, use_container_width=True)

    st.subheader("A Team's Phase-wise Profile")
    teams = sorted(bbb["team_batting"].dropna().unique())
    team = st.selectbox("Select a team", teams, key="phase_team")
    team_bat = bbb[bbb["team_batting"] == team]
    team_bowl = bbb[bbb["team_bowling"] == team]
    c1, c2 = st.columns(2)
    with c1:
        tb_phase = team_bat.groupby("phase").agg(balls=("innings_legal_balls", "count"), runs=("total_runs", "sum"))
        tb_phase["run_rate"] = (tb_phase["runs"] / (tb_phase["balls"] / 6)).round(2)
        tb_phase = tb_phase.reindex([p for p in ["PowerPlay", "Middle", "Death"] if p in tb_phase.index])
        st.plotly_chart(px.bar(x=tb_phase.index, y=tb_phase["run_rate"], title=f"{team} — Batting Run Rate by Phase",
                                labels={"x": "Phase", "y": "Run Rate"}),
                         use_container_width=True)
    with c2:
        tw_phase = team_bowl.groupby("phase").agg(balls=("innings_legal_balls", "count"), runs_conceded=("total_runs", "sum"))
        tw_phase["economy"] = (tw_phase["runs_conceded"] / (tw_phase["balls"] / 6)).round(2)
        tw_phase = tw_phase.reindex([p for p in ["PowerPlay", "Middle", "Death"] if p in tw_phase.index])
        st.plotly_chart(px.bar(x=tw_phase.index, y=tw_phase["economy"], title=f"{team} — Bowling Economy by Phase",
                                labels={"x": "Phase", "y": "Economy"}),
                         use_container_width=True)


# FANTASY PROFILE
def render_fantasy_points():

    n = st.slider("Show top N players", 5, 30, 10)
    st.subheader("Select Season ")
    seasons = set(pm['season'].unique()) | set(("all",))
    ssn = st.selectbox('See top players of any season', seasons)
    if ssn == "all":
        top_fantasy = pm.groupby("player")["fantasy_points"].sum().sort_values(ascending=False).head(n)
        st.plotly_chart(px.bar(x=top_fantasy.index, y=top_fantasy.values,
                            labels={"x": "Player", "y": "Fantasy Points"}),
                     use_container_width=True)
    else :
        pm_season = pm[pm['season'] == ssn]
        top_fantasy = pm_season.groupby("player")["fantasy_points"].sum().sort_values(ascending=False).head(n)
        
        st.plotly_chart(px.bar(x=top_fantasy.index, y=top_fantasy.values,
                                    labels={"x": "Player", "y": "Fantasy Points"}),
                             use_container_width=True)
    st.subheader(" Top Intense / Closest Matches")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Closest matches decided by runs**")
        close_runs = matches[matches["win_by_runs"] > 0].nsmallest(n, "win_by_runs")
        st.dataframe(close_runs[["season", "match_date", "team1", "team2", "match_winner", "win_by_runs"]],
                     use_container_width=True)
    with c2:
        st.markdown("**Closest matches decided by wickets**")
        close_wkts = matches[matches["win_by_wickets"] > 0].nsmallest(n, "win_by_wickets")
        st.dataframe(close_wkts[["season", "match_date", "team1", "team2", "match_winner", "win_by_wickets"]],
                     use_container_width=True)

    st.subheader(" Top Bowlers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Most Wickets**")
        top_wickets = pm.groupby("player")["bowl_wickets"].sum().sort_values(ascending=False).head(n)
        st.plotly_chart(px.bar(x=top_wickets.index, y=top_wickets.values,
                                labels={"x": "Player", "y": "Wickets"}),
                         use_container_width=True)
    with c2:
        st.markdown("**Best Economy**")
        bowl_totals = pm.groupby("player").agg(balls=("bowl_balls", "sum"), runs=("bowl_runs_conceded", "sum"))
        bowl_totals = bowl_totals[bowl_totals["balls"] >= 60]
        bowl_totals["economy"] = (bowl_totals["runs"] / (bowl_totals["balls"] / 6)).round(2)
        best_economy = bowl_totals.sort_values("economy").head(n)
        st.dataframe(best_economy, use_container_width=True)

    st.subheader(" Captaincy Risk/Reward")
    st.caption('more size - more matches played')
    fc = pm.groupby("player")["fantasy_points"].agg(["count", "mean", "std"])
    fc = fc[fc["count"] >= 5]
    fc["cv"] = (fc["std"] / fc["mean"].replace(0, pd.NA)).round(2)
    fc = fc.rename(columns={"count": "matches", "mean": "avg_points"})
    st.plotly_chart(
        px.scatter(fc.reset_index(), x="cv", y="avg_points", hover_name="player", size="matches",
                   labels={"cv": "Volatility (lower = safer captain pick)", "avg_points": "Avg Fantasy Points"}),
        use_container_width=True,
    )

    st.subheader("All-Rounder - Dual-Threat Picks")
    vp = pm.groupby("player").agg(
        matches=("match_id", "nunique"), avg_bat_runs=("bat_runs", "mean"), avg_wickets=("bowl_wickets", "mean"),
        avg_fantasy_points=("fantasy_points", "mean"),
    )
    vp = vp[vp["matches"] >= 5]
    vp["dual_threat"] = (vp["avg_bat_runs"] >= 18) & (vp["avg_wickets"] >= 0.8)
    st.dataframe(vp[vp["dual_threat"]].sort_values("avg_fantasy_points", ascending=False), use_container_width=True)

    st.subheader("Search a Player")
    search = st.text_input("Player name")
    search = str(search).strip()
    if search:
        result = pm[pm["player"].str.contains(search, case=False, na=False)]
        st.dataframe(result, use_container_width=True)


    
# CONTROL PANEL
if page == "Overview":
    render_overview()
elif page == "Match Profile":
    render_match_profile()
elif page == "Team Profile":
    render_team_profile()
elif page == "Player Profile":
    render_player_profile()
elif page == "Phase Analysis":
    render_phase_analysis()
elif page == "Fantasy Points":
    render_fantasy_points()