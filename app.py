import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import inject_css

st.set_page_config(
    page_title="FIFA 23 Talent Intelligence Platform",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 20px 0;'>
        <span style='font-size:2.4rem;'>⚽</span>
        <div style='font-size:1.05rem; font-weight:800; color:#F1F5F9; margin-top:6px;'>FIFA 23 Intelligence</div>
        <div style='font-size:0.75rem; color:#64748B;'>Strategic Scouting Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

st.markdown("""
<div class="page-hero" style="text-align:center; padding: 60px 32px;">
    <h1>⚽ FIFA 23 Talent Intelligence Platform</h1>
    <p style="font-size:1.1rem; margin-top:10px;">
        Your strategic scouting hub — explore 18,000+ players, uncover wonderkids,
        compare tactical fingerprints, and track financial efficiency.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 👈 Select a page from the sidebar to begin")

c1, c2, c3, c4 = st.columns(4)
pages_info = [
    (c1, "📋", "Data Overview",         "Full dataset stats, column dictionary, and exploratory charts."),
    (c2, "🌟", "Wonderkid Radar",        "High-growth young players with the best long-term ROI potential."),
    (c3, "🔎", "Scout Hub & Comparison", "Detailed player profile cards, positional benchmarks, and multi-player comparisons."),
    (c4, "💰", "Financial Efficiency",   "Player wages, release clauses, bargain opportunities, and cost-performance audits."),
]
for col, icon, title, desc in pages_info:
    with col:
        st.markdown(f"""
        <div class="pos-card" style="padding:22px 14px; min-height:160px;">
            <div class="pos-emoji">{icon}</div>
            <div class="pos-label" style="font-size:0.82rem; margin-top:8px;">{title}</div>
            <div style="font-size:0.72rem; color:#64748B; margin-top:8px; line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
