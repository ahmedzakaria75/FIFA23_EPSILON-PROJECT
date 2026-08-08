import streamlit as st
import pandas as pd
import requests

# -----------------------------------------------------------------------------
# FETCH PLAYER IMAGE (bypasses hotlink blocks using headers)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_player_image_bytes(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Referer': 'https://sofifa.com/'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

# -----------------------------------------------------------------------------
# SHARED CSS — call inject_css() at the top of every page
# -----------------------------------------------------------------------------
def inject_css():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }

    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #162032 100%);
        border-radius: 14px;
        padding: 22px 18px;
        border: 1px solid #2D3748;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 12px;
        text-align: center;
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        margin-top: 6px;
        line-height: 1.1;
    }
    .metric-subtitle {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 6px;
    }

    .pos-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 18px 12px;
        border: 1px solid #2D3748;
        text-align: center;
    }
    .pos-emoji { font-size: 1.9rem; }
    .pos-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 6px;
    }
    .pos-count {
        font-size: 1.6rem;
        font-weight: 800;
    }

    .takeaway-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 16px 0;
    }
    .takeaway-title {
        font-weight: 700;
        color: #38BDF8;
        font-size: 1rem;
        margin-bottom: 5px;
    }

    .page-hero {
        background: linear-gradient(135deg, #0f2027, #1a3a4c, #0f2027);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        border: 1px solid #1E3A5F;
    }
    .page-hero h1 {
        font-size: 1.9rem;
        font-weight: 800;
        color: #F1F5F9;
        margin: 0 0 6px 0;
    }
    .page-hero p {
        color: #94A3B8;
        margin: 0;
        font-size: 0.95rem;
    }

    .col-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        margin-top: 10px;
    }
    .col-table th {
        background-color: #1E293B;
        color: #38BDF8;
        padding: 10px 14px;
        text-align: left;
        font-weight: 700;
        border-bottom: 2px solid #10B981;
    }
    .col-table td {
        padding: 9px 14px;
        border-bottom: 1px solid #1E293B;
        color: #CBD5E1;
    }
    .col-table tr:nth-child(even) td { background-color: #111827; }
    .col-table tr:hover td { background-color: #1E293B; }

    .scout-card {
        background-color: #1E293B;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #38BDF8;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }

    .stRadio > div > label[data-baseweb="radio"] {
        background: transparent;
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 10px 0;
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #38BDF8;
        color: #38BDF8;
        background-color: rgba(56,189,248,0.08);
    }

    .filter-open-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16,185,129,0.15);
        border: 1px solid #10B981;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #10B981;
        margin-bottom: 10px;
    }
    .filter-closed-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(100,116,139,0.15);
        border: 1px solid #475569;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA LOADING — cached so it runs only once across all pages
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_preprocess_data():
    import os
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players_fifa23.csv")
    df_raw = pd.read_csv(csv_path, encoding="utf-8")
    selected_columns = [
        'ID', 'FullName', 'PhotoUrl', 'Age', 'Height', 'Weight',
        'Nationality', 'Club', 'PreferredFoot', 'ValueEUR',
        'WageEUR', 'ReleaseClause', 'ContractUntil', 'ClubJoined',
        'Overall', 'Potential', 'Growth', 'Positions',
        'NationalTeam', 'AttackingWorkRate', 'DefensiveWorkRate',
        'PaceTotal', 'ShootingTotal', 'PassingTotal', 'DribblingTotal',
        'DefendingTotal', 'PhysicalityTotal'
    ]
    df = df_raw[selected_columns].copy()
    df.drop_duplicates(inplace=True)
    df['ContractUntil'] = df['ContractUntil'].fillna('unknown')
    df['BMI'] = (df['Weight'] / ((df['Height'] / 100) ** 2)).round(2)

    def get_position_group(pos_string):
        primary_pos = str(pos_string).split(',')[0].strip()
        if primary_pos == 'GK':
            return 'Goalkeeper'
        elif primary_pos in ['CB', 'LB', 'RB', 'LWB', 'RWB']:
            return 'Defender'
        elif primary_pos in ['CM', 'CDM', 'CAM', 'LM', 'RM']:
            return 'Midfielder'
        elif primary_pos in ['ST', 'CF', 'LW', 'RW']:
            return 'Forward'
        else:
            return 'Other'

    df['PositionGroup'] = df['Positions'].apply(get_position_group)
    df['IsNationalPlayer'] = df['NationalTeam'] != 'Not in team'
    df['ValuePerOverall'] = (df['ValueEUR'] / df['Overall']).round(2)
    return df


# -----------------------------------------------------------------------------
# SIDEBAR FILTERS — rendered on every analysis page
# -----------------------------------------------------------------------------
def render_sidebar_filters(df_full):
    """Render global filter panel in sidebar. Returns filtered DataFrame."""
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 12px 0 20px 0;'>
            <span style='font-size:2.4rem;'>⚽</span>
            <div style='font-size:1.05rem; font-weight:800; color:#F1F5F9; margin-top:6px;'>FIFA 23 Intelligence</div>
            <div style='font-size:0.75rem; color:#64748B;'>Strategic Scouting Platform</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.get('filters_open', False):
            st.markdown('<div class="filter-open-badge">🟢 Filters Active</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="filter-closed-badge">⚪ Showing All Data</div>', unsafe_allow_html=True)

        btn_label = "🔒 Close Filters & Reset" if st.session_state.get('filters_open', False) else "🔧 Open Filters"
        if st.button(btn_label, key="filter_toggle_btn", use_container_width=True):
            st.session_state['filters_open'] = not st.session_state.get('filters_open', False)
            st.rerun()

        if st.session_state.get('filters_open', False):
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            pos_filter = st.multiselect(
                "Position Group",
                options=['Forward', 'Midfielder', 'Defender', 'Goalkeeper'],
                default=['Forward', 'Midfielder', 'Defender', 'Goalkeeper'],
                key="pos_filter"
            )
            min_age, max_age = st.slider("Age Range", 16, 44, (16, 35), key="age_range")
            max_value_cap = st.number_input(
                "Max Market Value Cap (€)",
                min_value=0,
                max_value=int(df_full['ValueEUR'].max()),
                value=int(df_full['ValueEUR'].max()),
                step=1_000_000,
                key="value_cap"
            )
            min_overall = st.slider("Min Overall Rating", 47, 91, 60, key="min_overall")
            min_potential = st.slider("Min Potential Ceiling", 48, 95, 65, key="min_potential")
            foot_filter = st.radio("Preferred Foot", ['All', 'Left', 'Right'], key="foot_filter")
            st.caption("Showing filtered results across analysis pages.")

    # Apply filters
    if st.session_state.get('filters_open', False):
        _pos   = st.session_state.get('pos_filter', ['Forward', 'Midfielder', 'Defender', 'Goalkeeper'])
        _min_a = st.session_state.get('age_range', (16, 35))[0]
        _max_a = st.session_state.get('age_range', (16, 35))[1]
        _maxv  = st.session_state.get('value_cap', int(df_full['ValueEUR'].max()))
        _mino  = st.session_state.get('min_overall', 60)
        _minp  = st.session_state.get('min_potential', 65)
        _foot  = st.session_state.get('foot_filter', 'All')

        df_filtered = df_full[
            (df_full['PositionGroup'].isin(_pos)) &
            (df_full['Age'] >= _min_a) & (df_full['Age'] <= _max_a) &
            (df_full['ValueEUR'] <= _maxv) &
            (df_full['Overall'] >= _mino) &
            (df_full['Potential'] >= _minp)
        ].copy()
        if _foot != 'All':
            df_filtered = df_filtered[df_filtered['PreferredFoot'] == _foot]
    else:
        df_filtered = df_full.copy()

    return df_filtered
