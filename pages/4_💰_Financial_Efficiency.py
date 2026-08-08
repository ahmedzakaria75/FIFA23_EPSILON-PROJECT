import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, load_and_preprocess_data, render_sidebar_filters, get_player_image_bytes

st.set_page_config(
    page_title="FIFA 23 | Financial Efficiency Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

df_full = load_and_preprocess_data()
df_filtered = render_sidebar_filters(df_full)

# =============================================================================
# HERO BANNER
# =============================================================================
st.markdown("""
<div class="page-hero">
    <h1>💰 Financial Efficiency &amp; Asset Value Dashboard</h1>
    <p>Compare top player contracts, salary structures, release clauses, and the relationship between player ratings and financial cost.</p>
</div>
""", unsafe_allow_html=True)

# Clean dataset from zero values for better financial insights
df_valid_fin = df_filtered[(df_filtered['ValueEUR'] > 0) & (df_filtered['WageEUR'] > 0)].copy()

# =============================================================================
# METRIC CARDS (Top Financial Values in Current Filtered Dataset)
# =============================================================================
k1, k2, k3, k4 = st.columns(4)

if not df_valid_fin.empty:
    highest_wage_row = df_valid_fin.loc[df_valid_fin['WageEUR'].idxmax()]
    highest_val_row = df_valid_fin.loc[df_valid_fin['ValueEUR'].idxmax()]
    
    # Filter out players with zero release clause to find the max valid release clause
    df_rc = df_valid_fin[df_valid_fin['ReleaseClause'] > 0]
    highest_rc_row = df_rc.loc[df_rc['ReleaseClause'].idxmax()] if not df_rc.empty else highest_val_row
    
    avg_wage_val = df_valid_fin['WageEUR'].mean()
else:
    highest_wage_row = {'FullName': 'N/A', 'WageEUR': 0, 'Club': 'N/A'}
    highest_val_row = {'FullName': 'N/A', 'ValueEUR': 0, 'Club': 'N/A'}
    highest_rc_row = {'FullName': 'N/A', 'ReleaseClause': 0, 'Club': 'N/A'}
    avg_wage_val = 0

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.6rem;">💸</div>
        <div class="metric-title" style="margin-top:6px;">Highest Weekly Earner</div>
        <div class="metric-value" style="color:#F59E0B; font-size:1.4rem;">{highest_wage_row['FullName']}</div>
        <div class="metric-subtitle">€{highest_wage_row['WageEUR']:,}/wk · {highest_wage_row['Club']}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.6rem;">💎</div>
        <div class="metric-title" style="margin-top:6px;">Highest Market Value</div>
        <div class="metric-value" style="color:#10B981; font-size:1.4rem;">{highest_val_row['FullName']}</div>
        <div class="metric-subtitle">€{highest_val_row['ValueEUR']/1e6:.1f}M · {highest_val_row['Club']}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.6rem;">🔓</div>
        <div class="metric-title" style="margin-top:6px;">Biggest Release Clause</div>
        <div class="metric-value" style="color:#38BDF8; font-size:1.4rem;">{highest_rc_row['FullName']}</div>
        <div class="metric-subtitle">€{highest_rc_row['ReleaseClause']/1e6:.1f}M · {highest_rc_row['Club']}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.6rem;">📊</div>
        <div class="metric-title" style="margin-top:6px;">Average Weekly Wage</div>
        <div class="metric-value" style="color:#A78BFA; font-size:1.5rem;">€{avg_wage_val:,.0f}</div>
        <div class="metric-subtitle">Across filtered player pool</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# ROW 1: TOP EARNERS & LARGEST RELEASE CLAUSES
# =============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💸 Top 15 Players Taking the Most Money (Weekly Wages)")
    st.caption("Top earners in the selected player dataset ranked by weekly wage (EUR).")
    
    if not df_valid_fin.empty:
        top_wages = df_valid_fin.sort_values(by='WageEUR', ascending=False).head(15)
        fig_wages = px.bar(
            top_wages, x='WageEUR', y='FullName',
            color='WageEUR', color_continuous_scale='YlOrBr',
            orientation='h', template='plotly_dark',
            text=top_wages['WageEUR'].apply(lambda w: f"€{w:,}/wk"),
            hover_data=['Club', 'Overall', 'ValueEUR'],
            labels={'WageEUR': 'Weekly Wage (€)', 'FullName': 'Player'}
        )
        fig_wages.update_traces(textposition='outside')
        fig_wages.update_layout(
            height=500, yaxis={'categoryorder': 'total ascending'},
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=60, t=10, b=10)
        )
        st.plotly_chart(fig_wages, use_container_width=True)
    else:
        st.info("No players matching parameters.")

with col2:
    st.markdown("### 🔓 Top 15 Largest Contract Release Clauses")
    st.caption("Players with the biggest buyout release clauses in the selected dataset.")
    
    df_rc_valid = df_valid_fin[df_valid_fin['ReleaseClause'] > 0]
    if not df_rc_valid.empty:
        top_rc = df_rc_valid.sort_values(by='ReleaseClause', ascending=False).head(15)
        fig_rc = px.bar(
            top_rc, x='ReleaseClause', y='FullName',
            color='ReleaseClause', color_continuous_scale='Blues',
            orientation='h', template='plotly_dark',
            text=top_rc['ReleaseClause'].apply(lambda r: f"€{r/1e6:.1f}M"),
            hover_data=['Club', 'Overall', 'ValueEUR'],
            labels={'ReleaseClause': 'Release Clause Buyout (€)', 'FullName': 'Player'}
        )
        fig_rc.update_traces(textposition='outside')
        fig_rc.update_layout(
            height=500, yaxis={'categoryorder': 'total ascending'},
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=60, t=10, b=10)
        )
        st.plotly_chart(fig_rc, use_container_width=True)
    else:
        st.info("No release clauses available for selection.")

st.markdown("---")

# =============================================================================
# ROW 2: PERFORMANCE/RATING VS FINANCIAL COST (SCATTER PLOT)
# =============================================================================
st.markdown("### ⚖️ Overall Player Performance Rating vs Financial Cost")
st.caption("Evaluate how much money players take relative to their actual performance (Overall Rating). Bottom-right represents bargains.")

sc1, sc2 = st.columns([3, 9])

with sc1:
    st.markdown("#### Analysis Parameters")
    cost_metric = st.radio(
        "Select Cost Metric for Y-Axis:",
        ["Weekly Wage (EUR)", "Market Value (EUR)"],
        index=0
    )
    st.markdown("""
    💡 **How to Analyze:**
    - **Bottom-Right Quadrant:** High-performing players (high overall rating) taking less money. These are cost-efficient players.
    - **Top-Left Quadrant:** Players with lower ratings taking high salaries. These represent potential financial inefficiencies.
    - **Baseline Curve:** Shows the standard pricing relationship for players.
    """)

y_column = 'WageEUR' if cost_metric == "Weekly Wage (EUR)" else 'ValueEUR'
y_label = 'Weekly Wage (€)' if cost_metric == "Weekly Wage (EUR)" else 'Market Value (€)'

with sc2:
    if not df_valid_fin.empty:
        fig_scatter = px.scatter(
            df_valid_fin, x='Overall', y=y_column,
            color='PositionGroup', size='Potential',
            hover_name='FullName',
            hover_data=['Club', 'Age', 'ValueEUR', 'WageEUR', 'ReleaseClause'],
            template='plotly_dark',
            labels={'Overall': 'Overall Performance Rating', y_column: y_label},
            color_discrete_map={
                'Forward': '#F59E0B', 'Midfielder': '#10B981',
                'Defender': '#38BDF8', 'Goalkeeper': '#A78BFA', 'Other': '#94A3B8'
            }
        )
        
        # Add regression trendline trend (exponential growth is common for wages/values in soccer)
        overall_vals = sorted(df_valid_fin['Overall'].unique())
        if len(overall_vals) > 2:
            # Simple exponential fit: y = a * e^(b * x)
            try:
                x = df_valid_fin['Overall']
                y = df_valid_fin[y_column]
                log_y = np.log(y)
                fit = np.polyfit(x, log_y, 1)
                fit_y = np.exp(fit[1]) * np.exp(fit[0] * np.array(overall_vals))
                
                fig_scatter.add_trace(go.Scatter(
                    x=overall_vals, y=fit_y, mode='lines', name='Market Baseline',
                    line=dict(color='#E2E8F0', dash='dash', width=2)
                ))
            except Exception:
                pass
                
        fig_scatter.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No data matches current parameters.")

st.markdown("---")

# =============================================================================
# SUMMARY INSIGHTS TABLE
# =============================================================================
st.markdown("### 📋 Detailed Financial breakdown (Sorted by Highest Cost)")
if not df_valid_fin.empty:
    top_table = df_valid_fin.sort_values(by=y_column, ascending=False).head(20).copy()
    
    # Formats
    top_table['Value_Fmt'] = top_table['ValueEUR'].apply(lambda v: f"€{v/1e6:.1f}M" if v >= 1e6 else f"€{v:,}")
    top_table['Wage_Fmt'] = top_table['WageEUR'].apply(lambda w: f"€{w:,}/wk")
    top_table['RC_Fmt'] = top_table['ReleaseClause'].apply(lambda r: f"€{r/1e6:.1f}M" if r >= 1e6 else f"€{r:,}")
    
    st.dataframe(
        top_table[['FullName', 'Club', 'Age', 'Overall', 'Potential', 'PositionGroup', 'Value_Fmt', 'Wage_Fmt', 'RC_Fmt']].rename(columns={
            'FullName': 'Player', 'PositionGroup': 'Position', 'Value_Fmt': 'Market Value', 'Wage_Fmt': 'Weekly Wage', 'RC_Fmt': 'Release Clause'
        }),
        use_container_width=True, hide_index=True
    )
else:
    st.info("No data available.")
