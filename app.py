import streamlit as st
import pandas as pd
import plotly.express as px

import preprocessor
import helper

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Olympics Dashboard',
    page_icon='🏅',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ── Custom CSS – Olympic palette ───────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background: #0b0c1a; color: #f0f0f0; }
    section[data-testid="stSidebar"] { background: #12132a; }

    /* Olympic ring header */
    .olympic-header {
        display: flex; align-items: center; gap: 12px;
        padding: 18px 0 8px 0;
    }
    .ring { width: 38px; height: 38px; border-radius: 50%;
            border: 5px solid; display: inline-block; }
    .r-blue   { border-color: #0085C7; }
    .r-yellow { border-color: #F4C300; }
    .r-green  { border-color: #009F3D; }
    .r-red    { border-color: #DF0024; }
    .r-black  { border-color: #f0f0f0; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1b3a 0%, #12132a 100%);
        border: 1px solid #2a2b4a;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 800; color: #F4C300; }
    .metric-label { font-size: 0.85rem; color: #aaaacc; margin-top: 4px; }

    /* Section titles */
    h2, h3 { color: #e0e0ff !important; }

    /* Sidebar radio pills */
    div[data-testid="stRadio"] label {
        color: #ccccee; font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return preprocessor.load_data()

df = get_data()
years, countries = preprocessor.country_year_list(df)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="olympic-header">
      <span class="ring r-blue"></span>
      <span class="ring r-yellow"></span>
      <span class="ring r-green"></span>
      <span class="ring r-red"></span>
      <span class="ring r-black"></span>
    </div>
    """, unsafe_allow_html=True)
    st.title('🏅 Olympics Dashboard')
    st.caption('120 Years of Olympic History')
    st.divider()

    menu = st.radio('Navigate to', [
        '🌍 Overall Analysis',
        '🥇 Medal Tally',
        '🏳️ Country-wise Analysis',
        '🏃 Athlete Performance',
        '⚽ Sport-wise Analysis',
        '📈 Year Trends',
    ])

# ══════════════════════════════════════════════════════════════════════════
# 1. OVERALL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
if menu == '🌍 Overall Analysis':
    st.title('🌍 Overall Olympic Analysis')
    editions, cities, sports, events, athletes, nations = helper.overall_stats(df)

    cols = st.columns(6)
    for col, val, lbl in zip(cols,
            [editions, cities, sports, events, athletes, nations],
            ['Editions', 'Host Cities', 'Sports', 'Events', 'Athletes', 'Nations']):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val:,}</div>
            <div class="metric-label">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('---')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(helper.participating_nations_over_time(df), use_container_width=True)
    with c2:
        st.plotly_chart(helper.events_over_time(df), use_container_width=True)

    st.plotly_chart(helper.athletes_over_time(df), use_container_width=True)

    st.subheader('🔥 Sports Events Heatmap')
    st.plotly_chart(helper.sport_heatmap(df), use_container_width=True)

    st.subheader('👫 Gender Participation Over Time')
    st.plotly_chart(helper.men_vs_women_over_time(df), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# 2. MEDAL TALLY
# ══════════════════════════════════════════════════════════════════════════
elif menu == '🥇 Medal Tally':
    st.title('🥇 Medal Tally')

    c1, c2 = st.columns(2)
    with c1:
        year_sel = st.selectbox('Select Year', ['Overall'] + [str(y) for y in years])
    with c2:
        country_sel = st.selectbox('Select Country', ['Overall'] + countries)

    tally = preprocessor.fetch_medal_tally(df, year_sel, country_sel)
    st.dataframe(
        tally[['region', 'Gold', 'Silver', 'Bronze', 'Total']].rename(columns={'region': 'Country'}),
        use_container_width=True, height=400
    )
    st.plotly_chart(helper.medal_tally_chart(tally, top_n=20), use_container_width=True)

    # Choropleth
    st.subheader('🗺️ World Medal Map')
    country_medals = (df[df['Medal'] != 'No Medal']
                      .groupby('region')['Medal'].count().reset_index())
    country_medals.columns = ['Country', 'Total_Medals']
    fig_map = px.choropleth(country_medals, locations='Country',
                            locationmode='country names', color='Total_Medals',
                            title='Total Olympic Medals by Country (All Time)',
                            color_continuous_scale='YlOrRd')
    fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# 3. COUNTRY-WISE
# ══════════════════════════════════════════════════════════════════════════
elif menu == '🏳️ Country-wise Analysis':
    st.title('🏳️ Country-wise Analysis')

    country_sel = st.selectbox('Select Country', countries)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(helper.country_medals_over_time(df, country_sel),
                        use_container_width=True)
    with c2:
        st.plotly_chart(helper.top_athletes_country(df, country_sel),
                        use_container_width=True)

    hm = helper.country_medal_heatmap(df, country_sel)
    if hm:
        st.plotly_chart(hm, use_container_width=True)
    else:
        st.info(f'No medal data available for {country_sel}.')

    # Medal breakdown pie
    temp_c = df[(df['region'] == country_sel) & (df['Medal'] != 'No Medal')]
    if not temp_c.empty:
        pie_data = temp_c['Medal'].value_counts().reset_index()
        pie_data.columns = ['Medal', 'Count']
        fig_pie = px.pie(pie_data, names='Medal', values='Count',
                         title=f'{country_sel} – Medal Breakdown',
                         color='Medal',
                         color_discrete_map=helper.MEDAL_COLORS)
        st.plotly_chart(fig_pie, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# 4. ATHLETE PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════
elif menu == '🏃 Athlete Performance':
    st.title('🏃 Athlete Performance Analysis')

    st.plotly_chart(helper.top_athletes_overall(df), use_container_width=True)
    st.plotly_chart(helper.men_vs_women_over_time(df), use_container_width=True)

    st.subheader('Height vs Weight by Sport')
    sport_sel = st.selectbox('Select Sport', sorted(df['Sport'].unique()))
    st.plotly_chart(helper.weight_height_scatter(df, sport_sel), use_container_width=True)

    # Age distribution of medal winners
    st.subheader('Age Distribution of Medal Winners')
    age_df = df[df['Medal'] != 'No Medal']
    fig_age = px.histogram(age_df, x='Age', color='Medal', nbins=35,
                           barmode='overlay', opacity=0.75,
                           title='Age Distribution of All Medal Winners',
                           color_discrete_map=helper.MEDAL_COLORS)
    fig_age.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_age, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# 5. SPORT-WISE
# ══════════════════════════════════════════════════════════════════════════
elif menu == '⚽ Sport-wise Analysis':
    st.title('⚽ Sport-wise Analysis')

    sport_sel = st.selectbox('Select Sport', sorted(df['Sport'].unique()))

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(helper.sport_medal_distribution(df, sport_sel),
                        use_container_width=True)
    with c2:
        st.plotly_chart(helper.sport_age_distribution(df, sport_sel),
                        use_container_width=True)

    # Top athletes in that sport
    sport_top = (df[(df['Sport'] == sport_sel) & (df['Medal'] != 'No Medal')]
                 .groupby(['Name', 'region'])['Medal'].count()
                 .sort_values(ascending=False).head(10).reset_index())
    sport_top.columns = ['Athlete', 'Country', 'Medals']
    st.subheader(f'Top Athletes in {sport_sel}')
    fig_st = px.bar(sport_top, x='Medals', y='Athlete', color='Country',
                    orientation='h', color_discrete_sequence=helper.OLYMPIC_5)
    fig_st.update_layout(yaxis={'categoryorder': 'total ascending'},
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_st, use_container_width=True)

    # Events in sport over years
    events_sport = df[df['Sport'] == sport_sel].groupby('Year')['Event'].nunique().reset_index()
    fig_ev = px.bar(events_sport, x='Year', y='Event',
                    title=f'{sport_sel} – Number of Events Over the Years',
                    color='Event', color_continuous_scale=[helper.BLUE, helper.RED])
    fig_ev.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_ev, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# 6. YEAR TRENDS
# ══════════════════════════════════════════════════════════════════════════
elif menu == '📈 Year Trends':
    st.title('📈 Year / Edition Trends')

    st.plotly_chart(helper.participating_nations_over_time(df), use_container_width=True)
    st.plotly_chart(helper.events_over_time(df), use_container_width=True)
    st.plotly_chart(helper.athletes_over_time(df), use_container_width=True)

    st.subheader('🏁 Country Medal Race')
    selected = st.multiselect(
        'Select Countries to Compare',
        options=countries,
        default=['USA', 'Russia', 'China', 'Germany', 'UK']
    )
    if selected:
        st.plotly_chart(helper.country_race_over_time(df, selected), use_container_width=True)
    else:
        st.info('Select at least one country to see the race.')

    # Summer vs Winter athlete counts over years
    st.subheader('☀️❄️ Summer vs Winter Athletes')
    sv = df.groupby(['Year', 'Season'])['ID'].nunique().reset_index()
    sv.columns = ['Year', 'Season', 'Athletes']
    fig_sv = px.line(sv, x='Year', y='Athletes', color='Season', markers=True,
                     color_discrete_map={'Summer': helper.YELLOW, 'Winter': helper.BLUE})
    fig_sv.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_sv, use_container_width=True)
