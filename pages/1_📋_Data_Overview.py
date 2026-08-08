import streamlit as st
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, load_and_preprocess_data

st.set_page_config(
    page_title="FIFA 23 | Data Overview",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

df_full = load_and_preprocess_data()

TOTAL_PLAYERS = len(df_full)
FWD_COUNT     = int((df_full['PositionGroup'] == 'Forward').sum())
MID_COUNT     = int((df_full['PositionGroup'] == 'Midfielder').sum())
DEF_COUNT     = int((df_full['PositionGroup'] == 'Defender').sum())
GK_COUNT      = int((df_full['PositionGroup'] == 'Goalkeeper').sum())

# Sidebar branding only (no filters on Overview)
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 20px 0;'>
        <span style='font-size:2.4rem;'>⚽</span>
        <div style='font-size:1.05rem; font-weight:800; color:#F1F5F9; margin-top:6px;'>FIFA 23 Intelligence</div>
        <div style='font-size:0.75rem; color:#64748B;'>Strategic Scouting Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("Use the sidebar pages above to navigate to analysis tabs.")

# =============================================================================
# PAGE CONTENT: DATA OVERVIEW
# =============================================================================
st.markdown("""
<div class="page-hero">
    <h1>📋 FIFA 23 Dataset Overview</h1>
    <p>A complete summary of the dataset: player counts, position breakdowns, column definitions, and exploratory charts.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Dataset at a Glance")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Players</div>
        <div class="metric-value" style="color:#10B981;">{TOTAL_PLAYERS:,}</div>
        <div class="metric-subtitle">After deduplication (18,539 raw)</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Nationalities</div>
        <div class="metric-value" style="color:#38BDF8;">{df_full['Nationality'].nunique()}</div>
        <div class="metric-subtitle">Countries represented</div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Clubs</div>
        <div class="metric-value" style="color:#F59E0B;">{df_full['Club'].nunique()}</div>
        <div class="metric-subtitle">Teams in the dataset</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("#### Players by Position Group")
p1, p2, p3, p4 = st.columns(4)
cards = [
    (p1, "⚡", "Forwards",    FWD_COUNT, "#F59E0B"),
    (p2, "🎯", "Midfielders", MID_COUNT, "#10B981"),
    (p3, "🛡️", "Defenders",  DEF_COUNT, "#38BDF8"),
    (p4, "🧤", "Goalkeepers", GK_COUNT,  "#A78BFA"),
]
for col, emoji, label, count, color in cards:
    with col:
        st.markdown(f"""
        <div class="pos-card">
            <div class="pos-emoji">{emoji}</div>
            <div class="pos-label">{label}</div>
            <div class="pos-count" style="color:{color};">{count:,}</div>
            <div class="metric-subtitle">{count/TOTAL_PLAYERS*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

st.subheader("📄 Data Preview (First 10 rows)")
display_cols = ['FullName', 'Age', 'Nationality', 'Club', 'Overall', 'Potential',
                'Growth', 'PositionGroup', 'ValueEUR', 'WageEUR', 'PreferredFoot']
st.dataframe(df_full[display_cols].head(10), use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader("📚 Column Dictionary")
col_descriptions = [
    ("ID",                 "Numeric",     "Unique FIFA player identifier"),
    ("FullName",           "Text",        "Player's full legal name"),
    ("PhotoUrl",           "Text (URL)",  "Link to the player's profile photo"),
    ("Age",                "Numeric",     "Player's current age in years"),
    ("Height",             "Numeric (cm)","Player's height in centimetres"),
    ("Weight",             "Numeric (kg)","Player's weight in kilograms"),
    ("Nationality",        "Categorical", "Player's country of nationality"),
    ("Club",               "Categorical", "Current club team"),
    ("PreferredFoot",      "Categorical", "Dominant foot: Left or Right"),
    ("ValueEUR",           "Numeric (€)", "Transfer market value in Euros"),
    ("WageEUR",            "Numeric (€)", "Weekly wage in Euros"),
    ("ReleaseClause",      "Numeric (€)", "Contract release clause value in Euros"),
    ("ContractUntil",      "Numeric/Text","Year the current contract expires (or 'unknown')"),
    ("ClubJoined",         "Numeric",     "Year the player joined their current club"),
    ("Overall",            "Numeric",     "Current overall ability rating (47 – 91)"),
    ("Potential",          "Numeric",     "Maximum potential rating the player can reach (48 – 95)"),
    ("Growth",             "Numeric",     "Remaining growth headroom = Potential − Overall"),
    ("Positions",          "Text",        "All playable positions (comma-separated, e.g. 'CM,CDM')"),
    ("NationalTeam",       "Categorical", "National team the player represents ('Not in team' if none)"),
    ("AttackingWorkRate",  "Categorical", "Offensive effort rate: High / Medium / Low"),
    ("DefensiveWorkRate",  "Categorical", "Defensive effort rate: High / Medium / Low"),
    ("PaceTotal",          "Numeric",     "Composite pace score (Acceleration + Sprint Speed)"),
    ("ShootingTotal",      "Numeric",     "Composite shooting score"),
    ("PassingTotal",       "Numeric",     "Composite passing score"),
    ("DribblingTotal",     "Numeric",     "Composite dribbling score"),
    ("DefendingTotal",     "Numeric",     "Composite defending score"),
    ("PhysicalityTotal",   "Numeric",     "Composite physicality score"),
    ("BMI",                "Numeric",     "Body Mass Index = Weight / (Height/100)² [engineered]"),
    ("PositionGroup",      "Categorical", "Broad position role: Forward / Midfielder / Defender / Goalkeeper [engineered]"),
    ("IsNationalPlayer",   "Boolean",     "True if player represents a national team [engineered]"),
    ("ValuePerOverall",    "Numeric (€)", "Market value ÷ Overall rating — measures cost-per-quality [engineered]"),
]
table_rows = "".join([
    f"<tr><td><code>{c}</code></td><td>{t}</td><td>{d}</td></tr>"
    for c, t, d in col_descriptions
])
st.markdown(f"""
<table class="col-table">
    <thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead>
    <tbody>{table_rows}</tbody>
</table>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader("📊 Exploratory Charts")
ch1, ch2 = st.columns(2)
with ch1:
    st.markdown("##### Player Count by Overall Rating")
    rating_counts = df_full['Overall'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Overall Rating', 'Player Count']
    fig_rating = px.bar(rating_counts, x='Overall Rating', y='Player Count',
        color='Player Count', color_continuous_scale='Viridis', template='plotly_dark')
    fig_rating.update_layout(height=360, showlegend=False, coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_rating, use_container_width=True)

with ch2:
    st.markdown("##### Player Count by Age")
    age_counts = df_full['Age'].value_counts().sort_index().reset_index()
    age_counts.columns = ['Age', 'Player Count']
    fig_age = px.bar(age_counts, x='Age', y='Player Count',
        color='Player Count', color_continuous_scale='Sunset', template='plotly_dark')
    fig_age.update_layout(height=360, showlegend=False, coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_age, use_container_width=True)

ch3, ch4 = st.columns(2)
with ch3:
    st.markdown("##### Preferred Foot Distribution")
    foot_counts = df_full['PreferredFoot'].value_counts().reset_index()
    foot_counts.columns = ['Foot', 'Count']
    fig_foot = px.pie(foot_counts, values='Count', names='Foot',
        color_discrete_sequence=['#10B981', '#38BDF8'], template='plotly_dark', hole=0.45)
    fig_foot.update_layout(height=360, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_foot.update_traces(textinfo='percent+label', textfont_size=14)
    st.plotly_chart(fig_foot, use_container_width=True)

with ch4:
    st.markdown("##### Players per Position Group")
    pos_counts = df_full['PositionGroup'].value_counts().reset_index()
    pos_counts.columns = ['Position', 'Count']
    fig_pos = px.pie(pos_counts, values='Count', names='Position',
        color_discrete_sequence=['#F59E0B', '#10B981', '#38BDF8', '#A78BFA'],
        template='plotly_dark', hole=0.45)
    fig_pos.update_layout(height=360, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_pos.update_traces(textinfo='percent+label', textfont_size=14)
    st.plotly_chart(fig_pos, use_container_width=True)

st.markdown("""
<div class="takeaway-box">
    <div class="takeaway-title">💡 Dataset Takeaway</div>
    The dataset covers <b>18,420 players</b> across <b>160 nationalities</b> and <b>679 clubs</b>.
    Most players are aged <b>21–28</b>, with Midfielders being the most represented position group.
    Right-footed players account for approximately <b>76%</b> of all footballers in the game.
</div>
""", unsafe_allow_html=True)
