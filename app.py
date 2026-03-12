import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import os
from scipy.spatial import ConvexHull

# --- 1. CONFIGURATIE ---
QUALITEITEN = {
    "1.1": {"naam": "Mobiliseren van actoren", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.2": {"naam": "Integratie van kennis", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.3": {"naam": "Benadrukken van kleine successen", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.4": {"naam": "Concretiseren van ambities", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.5": {"naam": "Framen van innovatie in context", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "2.1": {"naam": "Verifiëren waarde in pilot", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.2": {"naam": "Verifiëren waarde contexten", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.3": {"naam": "Testen beheersbaarheid", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.4": {"naam": "Overzicht bewaren", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.5": {"naam": "Momentum creëren ecosysteem", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.6": {"naam": "Leren van algemene lessen", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.7": {"naam": "Iteratief leren in innovatie", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "3.1": {"naam": "Coördinatie adaptie", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.2": {"naam": "Aanpassen routines", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.3": {"naam": "Creëer ondersteunend beleid", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.4": {"naam": "Verzeker gelijk speelveld", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.5": {"naam": "Vergaar waarde lange tijd", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"}
}

WERKVORM_LABELS = ["Alleen operationeel", "Lichtelijk tactisch/voornamelijk operationeel", "Voornamelijk tactisch/lichtelijk operationeel", "Strategisch/tactisch/operationeel", "Lichtelijk strategisch/voornamelijk tactisch", "Voornamelijk strategisch/lichtelijk tactisch", "Alleen strategisch"]
WERKAANPAK_LABELS = ["Alleen hiërarchisch", "Voornamelijk hiërarchisch", "Lichtelijk hiërarchisch", "Evenveel hiërarchisch als netwerk", "Lichtelijk netwerk", "Voornamelijk netwerk", "Alleen netwerk"]

DATA_FILE = "survey_data.json"

# --- 2. FUNCTIES ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def apply_jitter(df, amount=0.15):
    """Zorgt dat balletjes op exact dezelfde plek naast elkaar komen te staan."""
    df = df.copy()
    for i in range(len(df)):
        mask = (df['x'] == df.iloc[i]['x']) & (df['y'] == df.iloc[i]['y'])
        if mask.sum() > 1:
            df.loc[mask, 'x'] += np.random.uniform(-amount, amount, mask.sum())
            df.loc[mask, 'y'] += np.random.uniform(-amount, amount, mask.sum())
    return df

# --- 3. UI ---
st.set_page_config(page_title="Team Innovatie Dashboard", layout="wide")
st.title("Team Kwaliteiten Mapping")

# Sidebar Survey (compact)
with st.sidebar:
    st.header("Vul Survey in")
    with st.form("survey_form"):
        team_code = st.text_input("Teamcode:").strip().upper()
        y_val = st.select_slider("Werkvorm (Y)", options=range(1, 8), format_func=lambda x: WERKVORM_LABELS[x-1])
        x_val = st.select_slider("Werkaanpak (X)", options=range(1, 8), format_func=lambda x: WERKAANPAK_LABELS[x-1])
        
        bezit = st.multiselect("Jouw kwaliteiten:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        gemist = st.multiselect("Gemist in team:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        gezien = st.multiselect("Gezien bij collega's:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        
        if st.form_submit_button("Opslaan"):
            data = load_data()
            data.append({
                "team": team_code, "x": x_val, "y": y_val,
                "bezit": [s.split(":")[0] for s in bezit],
                "gemist": [s.split(":")[0] for s in gemist],
                "gezien": [s.split(":")[0] for s in gezien]
            })
            save_data(data)
            st.success("Opgeslagen!")
            st.rerun()

# --- 4. VISUALISATIE ---
kijk_team = st.text_input("Bekijk Team Resultaten:", value="INNO-2026").strip().upper()
team_responses = [r for r in load_data() if r['team'] == kijk_team]

if team_responses:
    # Data prep
    qual_stats = []
    all_points_per_group = {"Absorptief": [], "Adoptief": [], "Adaptief": []}
    
    # Tel totalen voor styling
    gemist_counts = {}
    gezien_counts = {}
    for r in team_responses:
        for q in r['gemist']: gemist_counts[q] = gemist_counts.get(q, 0) + 1
        for q in r['gezien']: gezien_counts[q] = gezien_counts.get(q, 0) + 1

    # Bereken posities
    for q_id, info in QUALITEITEN.items():
        relevant = [r for r in team_responses if q_id in r['bezit']]
        if relevant:
            avg_x = sum(r['x'] for r in relevant) / len(relevant)
            avg_y = sum(r['y'] for r in relevant) / len(relevant)
            qual_stats.append({
                "id": q_id, "naam": info['naam'], "groep": info['groep'],
                "x": avg_x, "y": avg_y, "count": len(relevant),
                "kleur": info['kleur']
            })
            all_points_per_group[info['groep']].append([avg_x, avg_y])

    df = apply_jitter(pd.DataFrame(qual_stats))
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Individuele Kwaliteiten (Interactief)")
        fig1 = go.Figure()

        for _, row in df.iterrows():
            is_gemist = (row['id'] in gemist_counts and gemist_counts[row['id']] == max(gemist_counts.values()))
            is_gezien = (row['id'] in gezien_counts and gezien_counts[row['id']] == max(gezien_counts.values()))
            
            fig1.add_trace(go.Scatter(
                x=[row['x']], y=[row['y']],
                mode='markers+text',
                marker=dict(
                    size=row['count']*15, color=row['kleur'],
                    line=dict(width=3 if is_gezien else 0, color='black')
                ),
                text=[row['id']],
                textfont=dict(color='white' if is_gemist else 'black', size=10),
                name=row['groep'],
                hovertemplate=f"<b>{row['id']}: {row['naam']}</b><br>Aantal: {row['count']}<br>Groep: {row['groep']}<extra></extra>"
            ))

        fig1.update_layout(
            xaxis=dict(tickvals=list(range(1,8)), ticktext=WERKAANPAK_LABELS, range=[0.5, 7.5]),
            yaxis=dict(tickvals=list(range(1,8)), ticktext=WERKVORM_LABELS, range=[0.5, 7.5]),
            showlegend=False, height=600, margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Team DNA (Overlap per groep)")
        fig2 = go.Figure()
        
        groep_kleuren = {"Absorptief": "orange", "Adoptief": "royalblue", "Adaptief": "gold"}
        
        for groep, points in all_points_per_group.items():
            if len(points) >= 3:
                points = np.array(points)
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]
                # Sluit de vorm
                hull_points = np.vstack((hull_points, hull_points[0]))
                
                fig2.add_trace(go.Scatter(
                    x=hull_points[:,0], y=hull_points[:,1],
                    fill="toself",
                    fillcolor=groep_kleuren[groep],
                    opacity=0.3,
                    line=dict(color=groep_kleuren[groep], width=2),
                    name=groep
                ))
            elif len(points) > 0: # Te weinig punten voor een vlak, teken stipjes
                pts = np.array(points)
                fig2.add_trace(go.Scatter(x=pts[:,0], y=pts[:,1], mode='markers', marker=dict(color=groep_kleuren[groep])))

        fig2.update_layout(
            xaxis=dict(tickvals=list(range(1,8)), ticktext=WERKAANPAK_LABELS, range=[0.5, 7.5]),
            yaxis=dict(tickvals=list(range(1,8)), ticktext=WERKVORM_LABELS, range=[0.5, 7.5]),
            height=600, margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

# Admin sectie
with st.expander("Beheer"):
    if st.text_input("Reset code", type="password") == "Ingrid_Bolier":
        if st.button("Wis alle team data"):
            save_data([])
            st.rerun()