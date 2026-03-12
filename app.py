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

# --- 2. DATA FUNCTIES ---
def init_data():
    if not os.path.exists(DATA_FILE):
        # De 23 testpersonen voor team INNO-2026
        start_data = [
            {"team": "INNO-2026", "y": 1, "x": 3, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 7, "x": 3, "bezit": ["1.1", "1.4", "3.5"], "gemist": ["2.4", "3.5"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["2.1", "2.4", "3.5"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 6, "x": 2, "bezit": ["1.2", "1.3"], "gemist": ["2.1"], "gezien": ["3.1"]},
            {"team": "INNO-2026", "y": 5, "x": 4, "bezit": ["3.1", "3.3", "1.5"], "gemist": ["2.6"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 6, "bezit": ["2.2", "2.3", "2.7"], "gemist": ["1.1"], "gezien": ["3.5"]},
            {"team": "INNO-2026", "y": 3, "x": 5, "bezit": ["1.4", "2.5", "3.4"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["1.1", "3.2"], "gemist": ["2.4"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 7, "x": 7, "bezit": ["3.5", "1.5"], "gemist": ["1.2"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 1, "x": 1, "bezit": ["2.6"], "gemist": ["3.3"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.1", "1.3", "2.1"], "gemist": ["3.5"], "gezien": ["3.2"]},
            {"team": "INNO-2026", "y": 6, "x": 4, "bezit": ["3.1", "3.5"], "gemist": ["2.7"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 6, "bezit": ["2.4", "2.5"], "gemist": ["1.1"], "gezien": ["3.5"]},
            {"team": "INNO-2026", "y": 3, "x": 2, "bezit": ["1.2", "3.4"], "gemist": ["3.5"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 3, "bezit": ["2.1", "2.2"], "gemist": ["1.4"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 5, "x": 5, "bezit": ["1.1", "3.3"], "gemist": ["2.4"], "gezien": ["3.1"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["2.7", "3.5"], "gemist": ["1.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 6, "x": 6, "bezit": ["1.4", "2.4"], "gemist": ["3.5"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 7, "x": 2, "bezit": ["3.1", "3.2"], "gemist": ["2.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 3, "x": 7, "bezit": ["1.5", "2.6"], "gemist": ["3.5"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 4, "bezit": ["1.1", "2.3"], "gemist": ["3.4"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["3.5", "2.4"], "gemist": ["1.1"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.3", "2.1", "3.1"], "gemist": ["3.5"], "gezien": ["1.1"]}
        ]
        with open(DATA_FILE, "w") as f:
            json.dump(start_data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def apply_jitter(df, amount=0.18):
    """Zorgt dat balletjes op exact dezelfde plek naast elkaar komen te staan."""
    df = df.copy()
    for i in range(len(df)):
        mask = (df['x'] == df.iloc[i]['x']) & (df['y'] == df.iloc[i]['y'])
        if mask.sum() > 1:
            df.loc[mask, 'x'] += np.random.uniform(-amount, amount, mask.sum())
            df.loc[mask, 'y'] += np.random.uniform(-amount, amount, mask.sum())
    return df

init_data()

# --- 3. UI OPBOUW ---
st.set_page_config(page_title="Team Innovatie Dashboard", layout="wide")
st.title("Team Kwaliteiten Mapping")

# Sidebar Survey
with st.sidebar:
    st.header("📝 Vul Survey in")
    with st.form("survey_form"):
        team_code = st.text_input("Teamcode:").strip().upper()
        y_val = st.select_slider("Werkvorm (Y-as)", options=range(1, 8), format_func=lambda x: WERKVORM_LABELS[x-1])
        x_val = st.select_slider("Werkaanpak (X-as)", options=range(1, 8), format_func=lambda x: WERKAANPAK_LABELS[x-1])
        
        bezit = st.multiselect("Jouw kwaliteiten:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        gemist = st.multiselect("Gemist in team:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        gezien = st.multiselect("Gezien bij collega's:", [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()])
        
        if st.form_submit_button("Sla mijn resultaten op"):
            if not team_code:
                st.error("Vul een teamcode in!")
            else:
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

# --- 4. DATA VERWERKING ---
st.markdown("### Bekijk Team Resultaten")
kijk_team = st.text_input("Voer teamcode in:", value="INNO-2026").strip().upper()
team_responses = [r for r in load_data() if r['team'] == kijk_team]

if team_responses:
    qual_stats = []
    all_points_per_group = {"Absorptief": [], "Adoptief": [], "Adaptief": []}
    
    # Tel totalen voor styling (dikke randen en witte tekst)
    gemist_counts = {}
    gezien_counts = {}
    for r in team_responses:
        for q in r['gemist']: gemist_counts[q] = gemist_counts.get(q, 0) + 1
        for q in r['gezien']: gezien_counts[q] = gezien_counts.get(q, 0) + 1

    # Maxima bepalen
    max_g_v = max(gemist_counts.values()) if gemist_counts else 0
    max_z_v = max(gezien_counts.values()) if gezien_counts else 0

    # Bereken gemiddelde posities per kwaliteit
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

    # Voorkom overlap
    df = apply_jitter(pd.DataFrame(qual_stats))
    
    col1, col2 = st.columns(2)

    # --- GRAFIEK 1: DE INTERACTIEVE MAPPING ---
    with col1:
        st.subheader("Individuele Kwaliteiten Mapping")
        fig1 = go.Figure()

        for _, row in df.iterrows():
            is_meest_gemist = (row['id'] in gemist_counts and gemist_counts[row['id']] == max_g_v and max_g_v > 0)
            is_meest_gezien = (row['id'] in gezien_counts and gezien_counts[row['id']] == max_z_v and max_z_v > 0)
            
            fig1.add_trace(go.Scatter(
                x=[row['x']], y=[row['y']],
                mode='markers+text',
                marker=dict(
                    size=row['count']*12 + 15, # Schalen op basis van aantal
                    color=row['kleur'],
                    line=dict(width=4 if is_meest_gezien else 0, color='black')
                ),
                text=[row['id']],
                textfont=dict(color='white' if is_meest_gemist else 'black', size=11, family="Arial Black"),
                name=row['groep'],
                hovertemplate=f"<b>Kwaliteit {row['id']}</b><br>{row['naam']}<br>Aanwezig bij: {row['count']} personen<extra></extra>"
            ))

        fig1.update_layout(
            xaxis=dict(tickvals=list(range(1,8)), ticktext=WERKAANPAK_LABELS, range=[0.5, 7.5], title="Werkaanpak (Management)"),
            yaxis=dict(tickvals=list(range(1,8)), ticktext=WERKVORM_LABELS, range=[0.5, 7.5], title="Werkvorm (Niveau)"),
            showlegend=False, height=700, margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --- GRAFIEK 2: TEAM DNA (GEKLEURDE VLAKKEN) ---
    with col2:
        st.subheader("Team DNA (Expertise Overlap)")
        fig2 = go.Figure()
        
        groep_config = {
            "Absorptief": "orange", 
            "Adoptief": "royalblue", 
            "Adaptief": "gold"
        }
        
        for groep, points in all_points_per_group.items():
            if len(points) >= 3:
                points_arr = np.array(points)
                try:
                    hull = ConvexHull(points_arr)
                    hull_points = points_arr[hull.vertices]
                    hull_points = np.vstack((hull_points, hull_points[0])) # Sluit de polygoon
                    
                    fig2.add_trace(go.Scatter(
                        x=hull_points[:,0], y=hull_points[:,1],
                        fill="toself",
                        fillcolor=groep_config[groep],
                        opacity=0.35,
                        line=dict(color=groep_config[groep], width=2),
                        name=groep,
                        hoverinfo='name'
                    ))
                except:
                    # Als punten op één lijn liggen kan ConvexHull falen, teken dan een dikke lijn
                    pts = np.array(points)
                    fig2.add_trace(go.Scatter(x=pts[:,0], y=pts[:,1], mode='lines+markers', line=dict(width=5), name=groep))
            elif len(points) > 0:
                pts = np.array(points)
                fig2.add_trace(go.Scatter(x=pts[:,0], y=pts[:,1], mode='markers', marker=dict(size=12, color=groep_config[groep]), name=groep))

        fig2.update_layout(
            xaxis=dict(tickvals=list(range(1,8)), ticktext=WERKAANPAK_LABELS, range=[0.5, 7.5], title="Werkaanpak"),
            yaxis=dict(tickvals=list(range(1,8)), ticktext=WERKVORM_LABELS, range=[0.5, 7.5], title="Werkvorm"),
            height=700, margin=dict(l=0, r=0, b=0, t=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.info("💡 **Tip:** Beweeg je muis over de cirkels in de linker grafiek om de volledige namen van de sub-kwaliteiten te zien.")

# --- 5. ADMIN RESET ---
st.divider()
with st.expander("⚙️ Beheer & Reset"):
    reset_target = st.text_input("Welk team wil je resetten?").strip().upper()
    admin_code = st.text_input("Wachtwoord:", type="password")
    if st.button("Reset team data"):
        if admin_code == "Ingrid_Bolier":
            huidige_data = load_data()
            nieuwe_data = [r for r in huidige_data if r['team'] != reset_target]
            save_data(nieuwe_data)
            st.success(f"Team {reset_target} is gereset.")
            st.rerun()
        else:
            st.error("Wachtwoord onjuist.")