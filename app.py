import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------------------------------------
# CONFIG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(page_title="Partenaires Billetterie", layout="centered")

# ---------------------------------------------------------
# GOOGLE SHEETS – Connexion
# ---------------------------------------------------------
def connect_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Partenaires Billets").sheet1
    return sheet

def save_to_google_sheets(data):
    sheet = connect_sheet()
    sheet.append_row(list(data.values()))

def load_google_sheet():
    sheet = connect_sheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# ---------------------------------------------------------
# DONNÉES PACKS & ÉVÉNEMENTS
# ---------------------------------------------------------
PACKS = {
    "Partenaire Simple (250€)": 3,
    "Partenaire Fer (500€)": 5,
    "Partenaire Bronze (1000€)": 10,
    "Partenaire Argent (2500€)": 20,
    "Partenaire Or (5000€)": 40,
}

EVENTS = [
    "7 Mai – St Geours de Maremne",
    "5 Juin – Hossegor",
    "17 Juillet – Bayonne",
    "7 Août – Seignosse",
    "4 Septembre – Biarritz",
]

# ---------------------------------------------------------
# DÉTECTION MODE ADMIN
# ---------------------------------------------------------
query_params = st.query_params
is_admin = query_params.get("admin", [""])[0] == "palamaxdandor"

# ---------------------------------------------------------
# PAGE ADMIN
# ---------------------------------------------------------
if is_admin:
    st.title("🔐 Administration – Liste des réponses")

    try:
        df = load_google_sheet()
        st.dataframe(df)
    except Exception as e:
        st.error("Impossible de charger les données Google Sheets.")
        st.code(str(e))

    st.stop()

# ---------------------------------------------------------
# PAGE FORMULAIRE PARTENAIRE
# ---------------------------------------------------------
st.title("🎟️ Formulaire Partenaire – Choix des billets")

# Nom du partenaire
nom = st.text_input("Nom du partenaire")

# Choix du pack
pack = st.selectbox("Choix du pack", list(PACKS.keys()))
max_billets = PACKS[pack]

st.markdown(f"### 🎫 Nombre de billets disponibles : **{max_billets}**")

# Sélection des billets par événement
st.markdown("### Sélection des billets par événement")

billets_selection = {}
total = 0

for event in EVENTS:
    nb = st.number_input(
        f"{event}",
        min_value=0,
        max_value=max_billets,
        step=1,
        key=event
    )
    billets_selection[event] = nb
    total += nb

# Vérification dépassement
if total > max_billets:
    st.error(f"Vous avez sélectionné **{total} billets**, mais le maximum est **{max_billets}**.")

# Bouton d’envoi
if st.button("Envoyer le formulaire"):
    if nom.strip() == "":
        st.error("Veuillez renseigner le nom du partenaire.")
    elif total != max_billets:
        st.warning(f"Vous devez sélectionner exactement **{max_billets} billets** (actuellement {total}).")
    else:
        try:
            save_to_google_sheets({
                "nom": nom,
                "pack": pack,
                "max_billets": max_billets,
                **billets_selection
            })
            st.success("Formulaire envoyé avec succès ! Merci.")
        except Exception as e:
            st.error("Erreur lors de l'enregistrement dans Google Sheets.")
            st.code(str(e))
