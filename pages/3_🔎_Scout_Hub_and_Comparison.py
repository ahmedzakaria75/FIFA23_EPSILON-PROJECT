import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, load_and_preprocess_data, render_sidebar_filters, get_player_image_bytes

st.set_page_config(
    page_title="FIFA 23 | Scout Hub & Player Comparison",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

# Custom CSS matching the user's requested card design
st.markdown("""
<style>
    .scout-badge-card {
        background-color: #1A2232;
        border: 2px solid #38BDF8;
        border-radius: 16px;
        padding: 24px;
        color: #E2E8F0;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .scout-title {
        text-align: center;
        color: #38BDF8;
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .scout-subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 0.88rem;
        font-weight: 500;
        margin-bottom: 16px;
    }
    .divider {
        border-top: 1px solid #2D3748;
        margin: 14px 0;
    }
    .scout-stats-row {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin-bottom: 8px;
    }
    .scout-stat-label {
        font-size: 0.68rem;
        color: #94A3B8;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .scout-stat-val {
        font-size: 1.75rem;
        font-weight: 800;
        margin-top: 2px;
    }
    .scout-details-list {
        font-size: 0.88rem;
        color: #CBD5E1;
        line-height: 2.0;
        padding-left: 4px;
    }
    .scout-details-list b {
        color: #94A3B8;
    }
    
    /* Small card styling for side-by-side comparison */
    .player-card-compact {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #2D3748;
        text-align: center;
    }
    .card-name-comp {
        font-size: 0.95rem;
        font-weight: 800;
        color: #F1F5F9;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-club-comp {
        font-size: 0.72rem;
        color: #64748B;
    }
    .card-badge-comp {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 700;
        background: rgba(56,189,248,0.12);
        color: #38BDF8;
        border: 1px solid rgba(56,189,248,0.3);
        margin: 2px;
    }
    .delta-better { color: #10B981; font-weight: 700; }
    .delta-worse  { color: #F87171; font-weight: 700; }
    .delta-equal  { color: #94A3B8; }
</style>
""", unsafe_allow_html=True)

df_full = load_and_preprocess_data()
df_filtered = render_sidebar_filters(df_full)

COLORS = ['#10B981', '#38BDF8', '#F59E0B', '#A78BFA']
FACE_STATS = ['PaceTotal', 'ShootingTotal', 'PassingTotal',
              'DribblingTotal', 'DefendingTotal', 'PhysicalityTotal']
FACE_LABELS = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physicality']

# =============================================================================
# HERO
# =============================================================================
st.markdown("""
<div class="page-hero">
    <h1>🔎 Scout Hub &amp; Player Comparison</h1>
    <p>Analyze individual player metrics or compare up to 4 players side-by-side with attribute fingerprints and performance deltas.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CHOOSE COMPARE COUNT & PLAYERS
# =============================================================================
all_names = sorted(df_filtered['FullName'].unique().tolist())
defaults = list(df_filtered['FullName'].head(4)) if len(df_filtered) >= 4 else list(df_filtered['FullName'])

col_opt1, col_opt2 = st.columns([3, 9])
with col_opt1:
    num_players = st.radio("Number of Players to Analyze:", [1, 2, 3, 4], index=0, horizontal=True)

selected = []
sel_cols = st.columns(num_players)

for i in range(num_players):
    with sel_cols[i]:
        default_idx = all_names.index(defaults[i]) + 1 if i < len(defaults) and defaults[i] in all_names else 0
        name = st.selectbox(f"👤 Player {i+1}", ["— select —"] + all_names, index=default_idx, key=f"sh_p{i+1}")
        if name != "— select —":
            rows = df_filtered[df_filtered['FullName'] == name]
            if not rows.empty:
                selected.append(rows.iloc[0])

if not selected:
    st.info("Please select at least one player to display details.")
    st.stop()

st.markdown("---")

# =============================================================================
# SINGLE PLAYER MODE (Detailed Profile Card & Single Radar)
# =============================================================================
if len(selected) == 1:
    p = selected[0]
    
    col_card, col_charts = st.columns([5, 7])
    
    with col_card:
        # Centered photo at the top
        img_bytes = get_player_image_bytes(p['PhotoUrl'])
        c_left, c_mid, c_right = st.columns([1, 1, 1])
        with c_mid:
            if img_bytes:
                st.image(img_bytes, width=130)
            else:
                st.markdown("<div style='font-size:5rem; text-align:center;'>👤</div>", unsafe_allow_html=True)
        
        val_fmt = f"€{p['ValueEUR']:,}"
        wage_fmt = f"€{p['WageEUR']:,}"
        rc_fmt = f"€{p['ReleaseClause']:,}" if p['ReleaseClause'] > 0 else "N/A"
        
        # Rounded box details matching the requested image layout
        html_card = (
            f'<div class="scout-badge-card" style="margin-top:-15px;">'
            f'<div class="scout-title">{p["FullName"]}</div>'
            f'<div class="scout-subtitle">{p["Club"]}<br>{p["Nationality"]}</div>'
            f'<div class="divider"></div>'
            f'<div class="scout-stats-row">'
            f'<div>'
            f'<span class="scout-stat-label">Overall</span>'
            f'<span class="scout-stat-val" style="color:#10B981;">{p["Overall"]}</span>'
            f'</div>'
            f'<div>'
            f'<span class="scout-stat-label">Potential</span>'
            f'<span class="scout-stat-val" style="color:#38BDF8;">{p["Potential"]}</span>'
            f'</div>'
            f'<div>'
            f'<span class="scout-stat-label">Growth</span>'
            f'<span class="scout-stat-val" style="color:#F59E0B;">+{p["Growth"]}</span>'
            f'</div>'
            f'</div>'
            f'<div class="divider"></div>'
            f'<div class="scout-details-list">'
            f'<b>Position:</b> {p["Positions"]} ({p["PositionGroup"]})<br>'
            f'<b>Age:</b> {p["Age"]} yrs<br>'
            f'<b>Height / Weight:</b> {p["Height"]} cm / {p["Weight"]} kg<br>'
            f'<b>BMI:</b> {p["BMI"]}<br>'
            f'<b>Preferred Foot:</b> {p["PreferredFoot"]}<br>'
            f'<b>Market Value:</b> {val_fmt}<br>'
            f'<b>Weekly Wage:</b> {wage_fmt}<br>'
            f'<b>Release Clause:</b> {rc_fmt}<br>'
            f'<b>Contract Until:</b> {p["ContractUntil"]}<br>'
            f'<b>National Team:</b> {p["NationalTeam"]}<br>'
            f'</div>'
            f'</div>'
        )
        st.markdown(html_card, unsafe_allow_html=True)

    with col_charts:
        st.markdown(f"### 📊 Performance Radar & Positional benchmark: {p['FullName']}")
        
        # Draw Player stats overlayed with his Position group benchmark
        fig_radar = go.Figure()
        
        # Player attributes
        vals = [p[c] for c in FACE_STATS]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=FACE_LABELS + [FACE_LABELS[0]],
            fill='toself',
            name=p['FullName'],
            line=dict(color='#38BDF8', width=2.5),
            fillcolor='rgba(56, 189, 248, 0.15)'
        ))
        
        # Benchmarks
        pg = p['PositionGroup']
        pos_df = df_filtered[df_filtered['PositionGroup'] == pg]
        if not pos_df.empty:
            avg_vals = [pos_df[c].mean() for c in FACE_STATS]
            fig_radar.add_trace(go.Scatterpolar(
                r=avg_vals + [avg_vals[0]],
                theta=FACE_LABELS + [FACE_LABELS[0]],
                fill='none',
                name=f"{pg} Position Average",
                line=dict(color='#10B981', width=1.5, dash='dot')
            ))
            
        fig_radar.update_layout(
            polar=dict(
                bgcolor='#111827',
                radialaxis=dict(visible=True, range=[0, 99], color='#475569', gridcolor='#1E293B'),
                angularaxis=dict(tickfont=dict(size=12, color='#CBD5E1'), gridcolor='#1E293B')
            ),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.15),
            template='plotly_dark',
            height=430,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Add basic bar chart of face attributes
        bar_df = pd.DataFrame({
            'Attribute': FACE_LABELS,
            'Value': [p[c] for c in FACE_STATS]
        })
        fig_bar = px.bar(
            bar_df, x='Attribute', y='Value',
            color='Value', color_continuous_scale='Blues',
            text='Value', template='plotly_dark',
            labels={'Value': 'Rating', 'Attribute': ''}
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            height=280, yaxis=dict(range=[0, 105]),
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# MULTI-PLAYER COMPARISON MODE (Side by Side)
# =============================================================================
else:
    st.markdown("### 👤 Selected Player Profiles")
    card_cols = st.columns(len(selected))
    
    for idx, (col, p) in enumerate(zip(card_cols, selected)):
        color = COLORS[idx]
        val_fmt  = f"€{p['ValueEUR']/1e6:.1f}M" if p['ValueEUR'] >= 1e6 else f"€{p['ValueEUR']:,.0f}"
        wage_fmt = f"€{p['WageEUR']:,}/wk"
        
        with col:
            img_bytes = get_player_image_bytes(p['PhotoUrl'])
            if img_bytes:
                st.image(img_bytes, width=90)
            else:
                st.markdown("<div style='font-size:3.5rem; text-align:center;'>👤</div>", unsafe_allow_html=True)
                
            html_card_comp = (
                f'<div class="player-card-compact" style="margin-top:-5px;">'
                f'<div class="card-name-comp">{p["FullName"]}</div>'
                f'<div class="card-club-comp">{p["Club"]} · {p["Nationality"]}</div>'
                f'<div>'
                f'<span class="card-badge-comp">{p["Positions"]}</span>'
                f'<span class="card-badge-comp" style="color:#94A3B8; background:none;">{p["PreferredFoot"]}</span>'
                f'</div>'
                f'<div class="divider" style="margin:8px 0;"></div>'
                f'<div style="display:flex; justify-content:space-around; font-size:0.75rem;">'
                f'<div>OVR: <b style="color:#10B981;">{p["Overall"]}</b></div>'
                f'<div>POT: <b style="color:#38BDF8;">{p["Potential"]}</b></div>'
                f'<div>AGE: <b>{p["Age"]}</b></div>'
                f'</div>'
                f'<div class="divider" style="margin:8px 0;"></div>'
                f'<div style="font-size:0.72rem; color:#64748B; line-height:1.7; text-align:left;">'
                f'💰 Value: <b style="color:#CBD5E1;">{val_fmt}</b><br>'
                f'💵 Wage: <b style="color:#CBD5E1;">{wage_fmt}</b><br>'
                f'📅 Contract: <b style="color:#CBD5E1;">{p["ContractUntil"]}</b>'
                f'</div>'
                f'</div>'
            )
            st.markdown(html_card_comp, unsafe_allow_html=True)

    st.markdown("---")
    
    # Graphs column layout
    radar_col, bar_col = st.columns([5, 7])
    
    with radar_col:
        st.markdown("### 📡 Comparison Radar Fingerprint")
        fig_radar = go.Figure()
        for idx, p in enumerate(selected):
            vals = [p[c] for c in FACE_STATS]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=FACE_LABELS + [FACE_LABELS[0]],
                fill='toself',
                name=p['FullName'],
                line=dict(color=COLORS[idx], width=2.5),
                fillcolor=f"rgba({int(COLORS[idx][1:3],16)},{int(COLORS[idx][3:5],16)},{int(COLORS[idx][5:7],16)},0.12)"
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='#111827',
                radialaxis=dict(visible=True, range=[0, 99], color='#475569', gridcolor='#1E293B'),
                angularaxis=dict(tickfont=dict(size=12, color='#CBD5E1'), gridcolor='#1E293B')
            ),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.18),
            template='plotly_dark',
            height=460,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=50)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with bar_col:
        st.markdown("### 📊 Attribute comparison")
        bar_data = []
        for idx, p in enumerate(selected):
            for stat, label in zip(FACE_STATS, FACE_LABELS):
                bar_data.append({
                    'Player': p['FullName'].split()[-1],
                    'Full Name': p['FullName'],
                    'Attribute': label,
                    'Value': p[stat]
                })
        bar_df = pd.DataFrame(bar_data)
        
        fig_bar = px.bar(
            bar_df, x='Attribute', y='Value', color='Full Name',
            barmode='group', template='plotly_dark',
            color_discrete_sequence=COLORS[:len(selected)],
            text='Value'
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            height=460, yaxis=dict(range=[0, 105]),
            legend=dict(orientation='h', yanchor='bottom', y=-0.22),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=50)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # Delta Table
    st.markdown("### 🔢 Attribute Delta Table")
    st.caption(f"Difference compared against reference player: **{selected[0]['FullName']}**")
    
    ref = selected[0]
    all_compare_stats = FACE_STATS + ['Overall', 'Potential', 'Growth', 'Age']
    all_compare_labels = FACE_LABELS + ['Overall', 'Potential', 'Growth', 'Age']
    
    table_rows = ""
    for stat, label in zip(all_compare_stats, all_compare_labels):
        ref_val = ref[stat]
        row_html = f"<tr><td style='padding:8px 12px; color:#94A3B8; font-weight:600;'>{label}</td>"
        row_html += f"<td style='padding:8px 12px; font-weight:700;'>{ref_val}</td>"
        for idx, p in enumerate(selected[1:], 1):
            val = p[stat]
            delta = val - ref_val
            if stat == 'Age':
                css = 'delta-better' if delta < 0 else ('delta-worse' if delta > 0 else 'delta-equal')
            else:
                css = 'delta-better' if delta > 0 else ('delta-worse' if delta < 0 else 'delta-equal')
            sign = '+' if delta > 0 else ''
            row_html += f"<td style='padding:8px 12px;'><b>{val}</b> <span class='{css}'>({sign}{delta})</span></td>"
        row_html += "</tr>"
        table_rows += row_html
        
    header = "<tr style='background:#1E293B;'><th style='padding:10px 12px; text-align:left; color:#38BDF8;'>Attribute</th>"
    header += f"<th style='padding:10px 12px; text-align:left; color:{COLORS[0]};'>{selected[0]['FullName'].split()[0]} (Baseline)</th>"
    for idx, p in enumerate(selected[1:], 1):
        header += f"<th style='padding:10px 12px; text-align:left; color:{COLORS[idx]};'>{p['FullName'].split()[0]} vs Baseline</th>"
    header += "</tr>"
    
    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.85rem; background:#0E1117; border-radius:12px; overflow:hidden;">
        <thead>{header}</thead>
        <tbody>{table_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
