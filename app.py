import streamlit as st
from mailjet_rest import Client

# ---------------------------------------------------------
# CONFIG STREAMLIT
# ---------------------------------------------------------
st.set_page_config(page_title="Partenaires Billetterie", layout="centered")

# ---------------------------------------------------------
# CONFIG MAILJET (via Secrets Streamlit)
# ---------------------------------------------------------
MAILJET_API_KEY = st.secrets["MAILJET_API_KEY"]
MAILJET_SECRET_KEY = st.secrets["MAILJET_SECRET_KEY"]

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3.1')

EMAIL_RECEIVERS = [
    "crmt.maxence@gmail.com",
    "lapalador2022@gmail.com"
]

def send_email(body):
    data = {
        'Messages': [
            {
                "From": {"Email": "crmt.maxence@gmail.com"},
                "To": [{"Email": email} for email in EMAIL_RECEIVERS],
                "Subject": "Nouvelle réponse partenaire",
                "TextPart": body
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code == 200

# ---------------------------------------------------------
# DONNÉES PACKS & ÉVÉNEMENTS
# ---------------------------------------------------------
PACKS = {
    "Partenaire Simple (300€)": 3,
    "Partenaire Fer (600€)": 5,
    "Partenaire Bronze (1200€)": 10,
    "Partenaire Argent (3000€)": 20,
    "Partenaire Or (6000€)": 40,
}

EVENTS = [
    "7 Mai – St Geours de Maremne - 19H",
    "5 Juin – Hossegor - 19H30",
    "17 Juillet – Bayonne - 11H",
    "7 Août – Seignosse - 19H",
    "4 Septembre – Biarritz - 19H",
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
    st.title("🔐 Administration – Historique des réponses")
    st.info("Les réponses sont envoyées par email via Mailjet.")
    st.write("Destinataires :")
    st.write("- crmt.maxence@gmail.com")
    st.write("- lapalador2022@gmail.com")
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
        # Construire l'email
        email_body = f"""
Nouvelle réponse partenaire :

Nom du partenaire : {nom}
Pack choisi : {pack}
Nombre de billets : {max_billets}

Répartition :
{chr(10).join([f"- {event} : {qte}" for event, qte in billets_selection.items()])}
"""

        if send_email(email_body):
            st.success("Formulaire envoyé avec succès !")
        else:
            st.error("Erreur lors de l'envoi de l'email.")
