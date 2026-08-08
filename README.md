# ⚽ FIFA 23 Talent Intelligence Platform

A premium, interactive scouting and analytics platform built with Streamlit and Plotly for football managers, analysts, and scouts. The platform enables deep-dive exploratory data analysis, wonderkid discovery, multi-player tactical comparisons, and budget efficiency profiling across a database of over 18,000 players.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Installation
Clone this repository to your workspace and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Application
Launch the Streamlit server from the project root:
```bash
streamlit run app.py
```
The app will open automatically in your default browser at `http://localhost:8503`.

---

## 🛠️ Project Architecture

```
FIFA23_EPSILON PROJECT/
├── app.py                         # Welcome landing portal with tab overview
├── utils.py                       # Shared styles, cached data loading, image fetcher
├── requirements.txt               # Dependencies (Pandas, Streamlit, Plotly, etc.)
├── players_fifa23.csv             # Raw FIFA 23 dataset
├── FIFA_EDA.ipynb                 # Jupyter notebook for exploratory data analysis
└── pages/                         # Numbered multi-page app routes
    ├── 1_📋_Data_Overview.py       # Global database summary and exploratory charts
    ├── 2_🌟_Wonderkid_Radar.py     # High-growth prospect discovery dashboard
    ├── 3_🔎_Scout_Hub_and_Comparison.py # Individual player profile cards & player comparisons
    └── 4_💰_Financial_Efficiency.py # Wage-to-value matching & buyout audits
```

---

## 💡 Key Features & Modules

### 1. 📋 Data Overview
- Detailed overview of the database covering 18,420 players, 160 nationalities, and 679 clubs.
- Complete column dictionary mapping engineered parameters like BMI, Position Groups, and Value-to-Performance indices.
- Exploratory distributions covering age brackets, rating spreads, foot preferences, and outfield role counts.

### 2. 🌟 Wonderkid & Future Star Radar
- **Adjustable Scouting Criteria:** Tune Age (16-25), Potential ceiling, and Growth headroom to discover hidden talent.
- **Scout Score Composite Metric:** Ranks prospects using an engineered formula weighted on Potential (45%), Growth (30%), Youth Bonus (25%), and Current Rating (10%).
- **Hidden Gems Quadrant Scatter:** Instantly visualizes players matching high-potential/low-cost bands.
- **Club Academies & National Pipelines:** Identifies the top global producers of young talent.

### 3. 🔎 Scout Hub & Player Comparison
- **1-Player Mode (Detailed Profile Card):** Renders a structured scouting badge card including photo, current attributes, body metrics (height/weight/BMI), financial terms (wage/value/release clause), contract expiry, and a positional overlay radar.
- **2-4 Player Side-by-Side Comparison:** Compares profiles, overlapping radar attributes, grouped bar distributions, and a **coloured Delta Table** marking performance variances relative to Player 1.
- **CDN Hotlinking Bypass:** Automatically fetches player images server-side using customized headers, bypassing referer/hotlink blockages.

### 4. 💰 Financial Efficiency Dashboard
- **Top Financial Lists:** Tracks the highest weekly earners and biggest contract buyout release clauses.
- **Performance vs. Salary Scatter Plot:** Visualizes Overall rating vs. Weekly Wage/Market Value with a built-in exponential baseline curve to easily detect underpaid bargains or over-leveraged contracts.
- **Comprehensive Datagrids:** Sorts and filters detailed contract details.

---

## ⚡ Technical Optimizations

- **State Persistence:** Sidebar filters persist seamlessly across sub-pages utilizing Streamlit session state.
- **Performance Caching:** Preprocessing is cached via `@st.cache_data` for lightning-fast loads on large-scale operations.
- **Responsive Layout:** Responsive container styling with an elegant dark theme tailored for modern displays.
