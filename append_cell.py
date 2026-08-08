import json

notebook_path = "FIFA_EDA.ipynb"
with open(notebook_path, "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Markdown cell
markdown_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Data Cleaning & Streamlit Export\n",
        "\n",
        "The following cell performs the complete cleaning and feature engineering process on the raw dataset and outputs a reduced, preprocessed file `cleaned_data.csv` for the Streamlit dashboard."
    ]
}

# Code cell
code_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import pandas as pd\n",
        "\n",
        "# 1. Load raw dataset\n",
        "df_raw = pd.read_csv('players_fifa23.csv', encoding='utf-8')\n",
        "\n",
        "# 2. Select columns of interest for the scouting dashboard\n",
        "selected_columns = [\n",
        "    'ID', 'FullName', 'PhotoUrl', 'Age', 'Height', 'Weight',\n",
        "    'Nationality', 'Club', 'PreferredFoot', 'ValueEUR',\n",
        "    'WageEUR', 'ReleaseClause', 'ContractUntil', 'ClubJoined',\n",
        "    'Overall', 'Potential', 'Growth', 'Positions',\n",
        "    'NationalTeam', 'AttackingWorkRate', 'DefensiveWorkRate',\n",
        "    'PaceTotal', 'ShootingTotal', 'PassingTotal', 'DribblingTotal',\n",
        "    'DefendingTotal', 'PhysicalityTotal'\n",
        "]\n",
        "df = df_raw[selected_columns].copy()\n",
        "\n",
        "# 3. Remove duplicates\n",
        "df.drop_duplicates(inplace=True)\n",
        "\n",
        "# 4. Impute missing contract values\n",
        "df['ContractUntil'] = df['ContractUntil'].fillna('unknown')\n",
        "\n",
        "# 5. Engineer metrics (BMI, general position role, value efficiency, national status)\n",
        "df['BMI'] = (df['Weight'] / ((df['Height'] / 100) ** 2)).round(2)\n",
        "\n",
        "def get_position_group(pos_string):\n",
        "    primary_pos = str(pos_string).split(',')[0].strip()\n",
        "    if primary_pos == 'GK':\n",
        "        return 'Goalkeeper'\n",
        "    elif primary_pos in ['CB', 'LB', 'RB', 'LWB', 'RWB']:\n",
        "        return 'Defender'\n",
        "    elif primary_pos in ['CM', 'CDM', 'CAM', 'LM', 'RM']:\n",
        "        return 'Midfielder'\n",
        "    elif primary_pos in ['ST', 'CF', 'LW', 'RW']:\n",
        "        return 'Forward'\n",
        "    else:\n",
        "        return 'Other'\n",
        "\n",
        "df['PositionGroup'] = df['Positions'].apply(get_position_group)\n",
        "df['IsNationalPlayer'] = df['NationalTeam'] != 'Not in team'\n",
        "df['ValuePerOverall'] = (df['ValueEUR'] / df['Overall']).round(2)\n",
        "\n",
        "# 6. Export to CSV for the Streamlit dashboard\n",
        "df.to_csv('cleaned_data.csv', index=False, encoding='utf-8')\n",
        "print('Successfully exported cleaned_data.csv!')"
    ]
}

notebook["cells"].append(markdown_cell)
notebook["cells"].append(code_cell)

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)
