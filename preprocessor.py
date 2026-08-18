import pandas as pd


def load_data():
    df = pd.read_csv('athlete_events.csv')
    regions = pd.read_csv('noc_regions.csv')
    df = df.merge(regions[['NOC', 'region']], on='NOC', how='left')
    df['Medal'].fillna('No Medal', inplace=True)
    df['Medal_Won'] = df['Medal'].apply(lambda x: 0 if x == 'No Medal' else 1)
    for col in ['Age', 'Height', 'Weight']:
        df[col].fillna(df[col].median(), inplace=True)
    df.drop_duplicates(inplace=True)
    return df


def medal_tally(df):
    medal_df = df[df['Medal'] != 'No Medal']
    tally = medal_df.groupby(['region', 'Medal']).size().unstack(fill_value=0).reset_index()
    tally.columns.name = None
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in tally.columns:
            tally[col] = 0
    tally['Total'] = tally['Gold'] + tally['Silver'] + tally['Bronze']
    tally = tally.sort_values('Total', ascending=False).reset_index(drop=True)
    tally.index += 1
    return tally


def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    countries = sorted(df['region'].dropna().unique().tolist())
    return years, countries


def fetch_medal_tally(df, year, country):
    tally = medal_tally(df)
    if year == 'Overall' and country == 'Overall':
        return tally
    if year != 'Overall' and country == 'Overall':
        temp = df[df['Year'] == int(year)]
    elif year == 'Overall' and country != 'Overall':
        temp = df[df['region'] == country]
    else:
        temp = df[(df['Year'] == int(year)) & (df['region'] == country)]

    temp = temp[temp['Medal'] != 'No Medal']
    t = temp.groupby(['region', 'Medal']).size().unstack(fill_value=0).reset_index()
    t.columns.name = None
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in t.columns:
            t[col] = 0
    t['Total'] = t['Gold'] + t['Silver'] + t['Bronze']
    t = t.sort_values('Total', ascending=False).reset_index(drop=True)
    t.index += 1
    return t
