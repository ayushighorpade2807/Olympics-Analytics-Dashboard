import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Olympic ring colours ───────────────────────────────────────────────────
BLUE   = '#0085C7'
YELLOW = '#F4C300'
GREEN  = '#009F3D'
RED    = '#DF0024'
BLACK  = '#1a1a2e'
GOLD   = '#FFD700'
SILVER = '#C0C0C0'
BRONZE = '#CD7F32'

OLYMPIC_5 = [BLUE, YELLOW, GREEN, RED, BLACK]
MEDAL_COLORS = {'Gold': GOLD, 'Silver': SILVER, 'Bronze': BRONZE}

# ── Overall stats ──────────────────────────────────────────────────────────

def overall_stats(df):
    editions   = df['Games'].nunique()
    cities     = df['City'].nunique()
    sports     = df['Sport'].nunique()
    events     = df['Event'].nunique()
    athletes   = df['ID'].nunique()
    nations    = df['region'].nunique()
    return editions, cities, sports, events, athletes, nations


def participating_nations_over_time(df):
    nations = df.groupby('Year')['region'].nunique().reset_index()
    nations.columns = ['Year', 'Nations']
    fig = px.line(nations, x='Year', y='Nations', markers=True,
                  title='Participating Nations Over the Years',
                  color_discrete_sequence=[BLUE])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def events_over_time(df):
    events = df.groupby('Year')['Event'].nunique().reset_index()
    events.columns = ['Year', 'Events']
    fig = px.line(events, x='Year', y='Events', markers=True,
                  title='Number of Events Over the Years',
                  color_discrete_sequence=[RED])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def athletes_over_time(df):
    athletes = df.groupby('Year')['ID'].nunique().reset_index()
    athletes.columns = ['Year', 'Athletes']
    fig = px.line(athletes, x='Year', y='Athletes', markers=True,
                  title='Athletes Participating Over the Years',
                  color_discrete_sequence=[GREEN])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def sport_heatmap(df):
    pivot = df.pivot_table(index='Sport', columns='Year',
                           values='Event', aggfunc='nunique').fillna(0)
    fig = px.imshow(pivot, aspect='auto',
                    title='Sports Events Heatmap Over the Years',
                    color_continuous_scale='YlOrRd')
    fig.update_layout(height=700)
    return fig


# ── Medal Tally ────────────────────────────────────────────────────────────

def medal_tally_chart(tally_df, top_n=20):
    df_plot = tally_df.head(top_n).copy()
    fig = go.Figure()
    for medal, color in [('Gold', GOLD), ('Silver', SILVER), ('Bronze', BRONZE)]:
        if medal in df_plot.columns:
            fig.add_trace(go.Bar(
                name=medal, x=df_plot['region'], y=df_plot[medal],
                marker_color=color))
    fig.update_layout(barmode='stack', title=f'Top {top_n} Countries – Medal Tally',
                      xaxis_tickangle=-40,
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ── Country-wise ───────────────────────────────────────────────────────────

def country_medal_heatmap(df, country):
    temp = df[(df['region'] == country) & (df['Medal'] != 'No Medal')]
    if temp.empty:
        return None
    pivot = temp.pivot_table(index='Sport', columns='Year',
                             values='Medal', aggfunc='count').fillna(0)
    fig = px.imshow(pivot, aspect='auto',
                    title=f'{country} – Medals Heatmap by Sport & Year',
                    color_continuous_scale='OrRd')
    fig.update_layout(height=600)
    return fig


def country_medals_over_time(df, country):
    temp = df[(df['region'] == country) & (df['Medal'] != 'No Medal')]
    year_medals = temp.groupby('Year')['Medal'].count().reset_index()
    year_medals.columns = ['Year', 'Medals']
    fig = px.line(year_medals, x='Year', y='Medals', markers=True,
                  title=f'{country} – Medals Over the Years',
                  color_discrete_sequence=[BLUE])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def top_athletes_country(df, country, top_n=10):
    temp = df[(df['region'] == country) & (df['Medal'] != 'No Medal')]
    top = (temp.groupby('Name')['Medal'].count()
               .sort_values(ascending=False).head(top_n).reset_index())
    top.columns = ['Athlete', 'Medals']
    fig = px.bar(top, x='Medals', y='Athlete', orientation='h',
                 title=f'Top {top_n} Athletes from {country}',
                 color='Medals', color_continuous_scale=[GREEN, YELLOW])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'},
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ── Athlete Performance ────────────────────────────────────────────────────

def weight_height_scatter(df, sport):
    temp = df[(df['Sport'] == sport)].dropna(subset=['Height', 'Weight'])
    fig = px.scatter(temp, x='Weight', y='Height', color='Medal',
                     symbol='Sex',
                     title=f'{sport} – Height vs Weight by Medal',
                     color_discrete_map={**MEDAL_COLORS, 'No Medal': '#cccccc'},
                     opacity=0.6,
                     hover_data=['Name', 'region', 'Year'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def men_vs_women_over_time(df):
    temp = df.groupby(['Year', 'Sex'])['ID'].nunique().reset_index()
    temp.columns = ['Year', 'Sex', 'Athletes']
    fig = px.line(temp, x='Year', y='Athletes', color='Sex', markers=True,
                  title='Male vs Female Athlete Participation Over the Years',
                  color_discrete_map={'M': BLUE, 'F': RED})
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def top_athletes_overall(df, top_n=15):
    top = (df[df['Medal'] != 'No Medal']
           .groupby(['Name', 'region'])['Medal'].count()
           .sort_values(ascending=False).head(top_n).reset_index())
    top.columns = ['Athlete', 'Country', 'Medals']
    fig = px.bar(top, x='Medals', y='Athlete', color='Country',
                 orientation='h',
                 title=f'Top {top_n} Most Decorated Athletes of All Time',
                 color_discrete_sequence=OLYMPIC_5)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'},
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ── Sport-wise ─────────────────────────────────────────────────────────────

def sport_medal_distribution(df, sport):
    temp = df[(df['Sport'] == sport) & (df['Medal'] != 'No Medal')]
    top_c = temp['region'].value_counts().head(10).reset_index()
    top_c.columns = ['Country', 'Medals']
    fig = px.bar(top_c, x='Country', y='Medals',
                 title=f'{sport} – Top 10 Countries',
                 color='Medals', color_continuous_scale=[BLUE, YELLOW])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


def sport_age_distribution(df, sport):
    temp = df[(df['Sport'] == sport) & (df['Medal'] != 'No Medal')]
    fig = px.histogram(temp, x='Age', color='Medal', nbins=30, barmode='overlay',
                       title=f'{sport} – Age Distribution of Medal Winners',
                       color_discrete_map=MEDAL_COLORS,
                       opacity=0.7)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ── Year Trends ────────────────────────────────────────────────────────────

def country_race_over_time(df, countries):
    temp = (df[(df['region'].isin(countries)) & (df['Medal'] != 'No Medal')]
            .groupby(['Year', 'region'])['Medal'].count().reset_index())
    temp.columns = ['Year', 'Country', 'Medals']
    fig = px.line(temp, x='Year', y='Medals', color='Country', markers=True,
                  title='Medal Race Over the Years',
                  color_discrete_sequence=OLYMPIC_5)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
