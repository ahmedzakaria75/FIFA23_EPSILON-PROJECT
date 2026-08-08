import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, load_and_preprocess_data, render_sidebar_filters

st.set_page_config(
    page_title="FIFA 23 | Wonderkid Radar",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

df_full = load_and_preprocess_data()
df_filtered = render_sidebar_filters(df_full)

# =============================================================================
# WONDERKID CRITERIA CONTROLS
# =============================================================================
st.markdown("""
<div class="page-hero">
    <h1>🌟 Wonderkid &amp; Future Star Intelligence</h1>
    <p>Deep-dive analysis of the next generation — scout score rankings, hidden gems, club academies, and ROI mapping.</p>
</div>
""", unsafe_allow_html=True)

# Inline threshold controls
with st.expander("⚙️ Adjust Wonderkid Criteria", expanded=False):
    cr1, cr2, cr3 = st.columns(3)
    with cr1:
        max_age = st.slider("Max Age", 16, 25, 21, key="wk_age")
    with cr2:
        min_potential = st.slider("Min Potential", 70, 90, 80, key="wk_pot")
    with cr3:
        min_growth = st.slider("Min Growth Headroom", 5, 20, 10, key="wk_growth")

wonderkids = df_filtered[
    (df_filtered['Age'] <= max_age) &
    (df_filtered['Potential'] >= min_potential) &
    (df_filtered['Growth'] >= min_growth)
].copy()

# ── Scout Score: composite metric ────────────────────────────────────────────
# Score = Potential * 0.45 + Growth * 1.5 + (22 - Age) * 1.2 + Overall * 0.1
# Normalised to 0–100
if not wonderkids.empty:
    wonderkids['ScoutScore'] = (
        wonderkids['Potential'] * 0.45 +
        wonderkids['Growth'] * 1.5 +
        (22 - wonderkids['Age'].clip(upper=22)) * 1.2 +
        wonderkids['Overall'] * 0.1
    )
    _min, _max = wonderkids['ScoutScore'].min(), wonderkids['ScoutScore'].max()
    if _max > _min:
        wonderkids['ScoutScore'] = ((wonderkids['ScoutScore'] - _min) / (_max - _min) * 100).round(1)
    else:
        wonderkids['ScoutScore'] = 100.0
    wonderkids = wonderkids.sort_values('ScoutScore', ascending=False)

    # Value per potential point (ROI metric — lower is better)
    wonderkids['ValuePerPotential'] = (wonderkids['ValueEUR'] / wonderkids['Potential']).round(0)

# =============================================================================
# KPI CARDS
# =============================================================================
if wonderkids.empty:
    st.warning("No wonderkids match the current criteria. Try adjusting the thresholds above.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "🌟", "Wonderkids Found",     f"{len(wonderkids):,}",                         "#10B981"),
    (k2, "📈", "Avg Potential",         f"{wonderkids['Potential'].mean():.1f}",          "#38BDF8"),
    (k3, "⚡", "Avg Growth Headroom",   f"+{wonderkids['Growth'].mean():.1f}",            "#F59E0B"),
    (k4, "🎂", "Avg Age",               f"{wonderkids['Age'].mean():.1f} yrs",            "#A78BFA"),
    (k5, "💰", "Median Value",          f"€{wonderkids['ValueEUR'].median()/1e6:.1f}M",   "#F87171"),
]
for col, icon, label, value, color in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem;">{icon}</div>
            <div class="metric-title" style="margin-top:6px;">{label}</div>
            <div class="metric-value" style="color:{color}; font-size:1.6rem;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# ROW 1 — Scout Score Leaderboard  +  Hidden Gems Quadrant
# =============================================================================
row1_l, row1_r = st.columns([6, 6])

with row1_l:
    st.markdown("#### 🏅 Top 20 by Scout Score")
    st.caption("Composite score: Potential × 0.45 + Growth × 1.5 + Youth Bonus × 1.2 + Overall × 0.1 → normalised 0–100")
    top20 = wonderkids.head(20).copy()
    colors = px.colors.sample_colorscale("Viridis", [i/19 for i in range(20)])
    fig_ss = go.Figure(go.Bar(
        x=top20['ScoutScore'],
        y=top20['FullName'],
        orientation='h',
        marker=dict(color=top20['ScoutScore'], colorscale='Viridis', showscale=False),
        text=top20['ScoutScore'].apply(lambda v: f"{v:.1f}"),
        textposition='outside',
        customdata=top20[['Age', 'Potential', 'Growth', 'PositionGroup', 'Club']].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Scout Score: %{x:.1f}<br>"
            "Age: %{customdata[0]}<br>"
            "Potential: %{customdata[1]}<br>"
            "Growth: +%{customdata[2]}<br>"
            "Position: %{customdata[3]}<br>"
            "Club: %{customdata[4]}<extra></extra>"
        )
    ))
    fig_ss.update_layout(
        height=560,
        xaxis=dict(range=[0, 115], title="Scout Score"),
        yaxis=dict(autorange='reversed', tickfont=dict(size=11)),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=60, t=20, b=20)
    )
    st.plotly_chart(fig_ss, use_container_width=True)

with row1_r:
    st.markdown("#### 💎 Hidden Gems Quadrant — High Potential, Low Cost")
    st.caption("Players in the top-left are the highest-value scouting opportunities (high potential, cheap to acquire)")

    # Add quadrant lines at medians
    med_val = wonderkids['ValueEUR'].median()
    med_pot = wonderkids['Potential'].median()

    fig_gems = px.scatter(
        wonderkids, x='ValueEUR', y='Potential',
        size='Growth', color='PositionGroup',
        hover_name='FullName',
        hover_data={'Club': True, 'Age': True, 'Overall': True, 'Growth': True,
                    'ScoutScore': True, 'ValueEUR': ':,.0f'},
        template='plotly_dark',
        color_discrete_map={
            'Forward': '#F59E0B', 'Midfielder': '#10B981',
            'Defender': '#38BDF8', 'Goalkeeper': '#A78BFA', 'Other': '#94A3B8'
        },
        size_max=30,
        labels={'ValueEUR': 'Market Value (€)', 'Potential': 'Potential Rating'}
    )
    # Quadrant shading
    fig_gems.add_vrect(x0=0, x1=med_val, fillcolor='rgba(16,185,129,0.05)',
                       layer='below', line_width=0)
    fig_gems.add_hline(y=med_pot, line_dash='dot', line_color='#475569',
                       annotation_text="Median Potential", annotation_position="right")
    fig_gems.add_vline(x=med_val, line_dash='dot', line_color='#475569',
                       annotation_text="Median Value", annotation_position="top right")
    # Label annotation
    fig_gems.add_annotation(x=med_val*0.1, y=wonderkids['Potential'].max()-0.5,
                             text="💎 Hidden Gems", font=dict(color='#10B981', size=12),
                             showarrow=False)
    fig_gems.update_layout(
        height=560,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_gems, use_container_width=True)

st.markdown("---")

# =============================================================================
# ROW 2 — Age Distribution  +  Position Breakdown  +  Value vs ROI
# =============================================================================
row2_l, row2_m, row2_r = st.columns([4, 3, 5])

with row2_l:
    st.markdown("#### 🎂 Age Distribution of Wonderkids")
    age_counts = wonderkids['Age'].value_counts().sort_index().reset_index()
    age_counts.columns = ['Age', 'Count']
    fig_age = px.bar(
        age_counts, x='Age', y='Count',
        color='Count', color_continuous_scale='Teal',
        template='plotly_dark',
        text='Count',
        labels={'Age': 'Player Age', 'Count': 'Number of Wonderkids'}
    )
    fig_age.update_traces(textposition='outside')
    fig_age.update_layout(
        height=340, showlegend=False, coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=20)
    )
    st.plotly_chart(fig_age, use_container_width=True)

with row2_m:
    st.markdown("#### 🎯 Position Breakdown")
    pos_counts = wonderkids['PositionGroup'].value_counts().reset_index()
    pos_counts.columns = ['Position', 'Count']
    fig_pos = px.pie(
        pos_counts, values='Count', names='Position',
        color_discrete_sequence=['#F59E0B', '#10B981', '#38BDF8', '#A78BFA'],
        template='plotly_dark', hole=0.55
    )
    fig_pos.update_traces(textinfo='percent+label', textfont_size=12,
                          pull=[0.05]*len(pos_counts))
    fig_pos.update_layout(
        height=340,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=20)
    )
    st.plotly_chart(fig_pos, use_container_width=True)

with row2_r:
    st.markdown("#### 📉 ROI Efficiency — Potential vs Cost per Potential Point")
    st.caption("Bottom-right = high potential, low cost per point = best ROI")
    top_roi = wonderkids.nsmallest(40, 'ValuePerPotential')
    fig_roi = px.scatter(
        top_roi, x='ValuePerPotential', y='Potential',
        color='PositionGroup', hover_name='FullName',
        size='Growth', size_max=22,
        hover_data={'Club': True, 'Age': True, 'ValueEUR': ':,.0f', 'Growth': True},
        template='plotly_dark',
        color_discrete_map={
            'Forward': '#F59E0B', 'Midfielder': '#10B981',
            'Defender': '#38BDF8', 'Goalkeeper': '#A78BFA', 'Other': '#94A3B8'
        },
        labels={'ValuePerPotential': 'Value per Potential Point (€)', 'Potential': 'Potential Rating'}
    )
    fig_roi.update_layout(
        height=340,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=10))
    )
    st.plotly_chart(fig_roi, use_container_width=True)

st.markdown("---")

# =============================================================================
# ROW 3 — Top Nations  +  Top Club Academies
# =============================================================================
row3_l, row3_r = st.columns(2)

with row3_l:
    st.markdown("#### 🌍 Top 15 Nations Producing Wonderkids")
    nation_counts = wonderkids['Nationality'].value_counts().head(15).reset_index()
    nation_counts.columns = ['Nationality', 'Count']
    nation_avg_pot = wonderkids.groupby('Nationality')['Potential'].mean().round(1)
    nation_counts['Avg Potential'] = nation_counts['Nationality'].map(nation_avg_pot)

    fig_nations = px.bar(
        nation_counts, x='Count', y='Nationality', orientation='h',
        color='Avg Potential', color_continuous_scale='Plasma',
        template='plotly_dark', text='Count',
        hover_data={'Avg Potential': True},
        labels={'Count': 'Wonderkid Count', 'Avg Potential': 'Avg Potential'}
    )
    fig_nations.update_traces(textposition='outside')
    fig_nations.update_layout(
        height=420, yaxis={'categoryorder': 'total ascending'},
        coloraxis_colorbar=dict(title='Avg Pot', thickness=12, len=0.7),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_nations, use_container_width=True)

with row3_r:
    st.markdown("#### 🏟️ Top 15 Club Academies by Wonderkid Count")
    club_wk = wonderkids[wonderkids['Club'] != 'Free agent'].groupby('Club').agg(
        Count=('FullName', 'count'),
        Avg_Potential=('Potential', 'mean'),
        Avg_Scout=('ScoutScore', 'mean')
    ).reset_index().sort_values('Count', ascending=False).head(15)
    club_wk.columns = ['Club', 'Count', 'Avg Potential', 'Avg Scout Score']

    fig_clubs = px.bar(
        club_wk, x='Count', y='Club', orientation='h',
        color='Avg Scout Score', color_continuous_scale='Turbo',
        template='plotly_dark', text='Count',
        hover_data={'Avg Potential': ':.1f', 'Avg Scout Score': ':.1f'},
        labels={'Count': 'Wonderkid Count', 'Avg Scout Score': 'Avg Scout Score'}
    )
    fig_clubs.update_traces(textposition='outside')
    fig_clubs.update_layout(
        height=420, yaxis={'categoryorder': 'total ascending'},
        coloraxis_colorbar=dict(title='Scout Score', thickness=12, len=0.7),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_clubs, use_container_width=True)

st.markdown("---")

# =============================================================================
# FULL LEADERBOARD TABLE
# =============================================================================
st.markdown("#### 📋 Full Wonderkid Leaderboard")

display_wk = wonderkids[[
    'FullName', 'Age', 'Nationality', 'Club', 'PositionGroup',
    'Overall', 'Potential', 'Growth', 'ScoutScore',
    'ValueEUR', 'WageEUR', 'ValuePerPotential'
]].rename(columns={
    'FullName': 'Player', 'PositionGroup': 'Position',
    'ScoutScore': 'Scout Score', 'ValueEUR': 'Value (€)',
    'WageEUR': 'Wage (€/wk)', 'ValuePerPotential': '€ per Potential Pt'
}).reset_index(drop=True)

st.dataframe(
    display_wk.style.background_gradient(subset=['Scout Score'], cmap='Greens')
                    .background_gradient(subset=['Potential'], cmap='Blues')
                    .background_gradient(subset=['Growth'], cmap='YlOrRd')
                    .format({'Value (€)': '€{:,.0f}', 'Wage (€/wk)': '€{:,.0f}',
                             '€ per Potential Pt': '€{:,.0f}', 'Scout Score': '{:.1f}'}),
    use_container_width=True,
    hide_index=True,
    height=420
)

st.markdown("""
<div class="takeaway-box">
    <div class="takeaway-title">💡 Scouting Intelligence Summary</div>
    The <b>Scout Score</b> ranks players by a composite of Potential (45%), Growth Headroom (30%), Youth Bonus (25%), and Current Rating (10%).
    Focus on the <b>Hidden Gems quadrant</b> (high potential, low value) for budget scouting.
    Track <b>Club Academies</b> to build pipeline relationships with top youth producers.
</div>
""", unsafe_allow_html=True)
