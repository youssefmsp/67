import streamlit as st
import yfinance as yf
import random

# Configuration de la page
st.set_page_config(page_title="Trading Quest 📈", page_icon="⚡", layout="centered")

# --- INITIALISATION DE L'ÉTAT (SESSION STATE) ---
if "solde" not in st.session_state:
    st.session_state.solde = 1000.0
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "portefeuille" not in st.session_state:
    st.session_state.portefeuille = {}  # { "AAPL": {"quantite": 2, "prix_moyen": 150.0} }
if "bonus_reclame" not in st.session_state:
    st.session_state.bonus_reclame = False

# Calcul du niveau
niveau = (st.session_state.xp // 100) + 1
titres = {1: "🟢 Novice des Marchés", 2: "🔵 Trader Averti", 3: "🟣 Analyste Senior", 4: "👑 Loup de Wall Street"}
rang = titres.get(niveau, "🔥 Demi-Dieu de la Finance")

# --- EN-TÊTE DU SITE ---
st.title("⚡ Trading Quest")
st.caption("Débloque des niveaux, tente ta chance et bâtis ton empire !")

# Barre de niveau & XP
col_lvl, col_xp = st.columns([1, 2])
with col_lvl:
    st.subheader(f"Niveau {niveau}")
    st.caption(rang)
with col_xp:
    progression = (st.session_state.xp % 100) / 100
    st.progress(progression, text=f"XP : {st.session_state.xp % 100} / 100")

# Métriques Solde & Portefeuille
valeur_actions = 0.0
for sym, data in st.session_state.portefeuille.items():
    try:
        p_actuel = yf.Ticker(sym).history(period="1d")["Close"].iloc[-1]
        valeur_actions += p_actuel * data["quantite"]
    except:
        valeur_actions += data["prix_moyen"] * data["quantite"]

total_patrimoine = st.session_state.solde + valeur_actions

c1, c2, c3 = st.columns(3)
c1.metric("Cash disponible", f"{st.session_state.solde:.2f} $")
c2.metric("Valeur actions", f"{valeur_actions:.2f} $")
c3.metric("Patrimoine total", f"{total_patrimoine:.2f} $", delta=f"{(total_patrimoine - 1000.0):.2f} $")

st.divider()

# --- MODULE DOPAMINE : RÉCOMPENSE ALÉATOIRE QUOTIDIENNE ---
st.subheader("🎁 Bonus de Connexion Quotidien")
if not st.session_state.bonus_reclame:
    if st.button("🎰 Ouvrir mon Coffre Mystère", use_container_width=True):
        gain = random.choice([50, 100, 200, 500, 1000])
        st.session_state.solde += gain
        st.session_state.xp += 30
        st.session_state.bonus_reclame = True
        st.balloons()
        st.success(f"🎉 RENAISSANCE ! Tu as gagné un bonus mystère de **+{gain} $** et **+30 XP** !")
        st.rerun()
else:
    st.info("✅ Coffre réclamé ! Reviens plus tard pour un autre tirage.")

st.divider()

# --- ESPACE TRADING INTERACTIF ---
st.subheader("🛒 Salle des Marchés")

actions_populaires = {"Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Amazon": "AMZN", "Bitcoin (ETF)": "IBIT"}
choix = st.selectbox("Entreprise star :", list(actions_populaires.keys()))
symbole = actions_populaires[choix]

# Récupération en direct
try:
    ticker = yf.Ticker(symbole)
    df_hist = ticker.history(period="1mo")
    prix_actuel = df_hist["Close"].iloc[-1]
    
    col_sym, col_pr = st.columns(2)
    col_sym.write(f"### {symbole}")
    col_pr.subheader(f"{prix_actuel:.2f} $")

    # Graphique interactif
    st.line_chart(df_hist["Close"])

    # Acheter
    quantite = st.number_input("Quantité d'actions :", min_value=1, value=1, step=1)
    cout_total = prix_actuel * quantite

    if st.button(f"🚀 Acheter ({cout_total:.2f} $)", use_container_width=True):
        if cout_total <= st.session_state.solde:
            st.session_state.solde -= cout_total
            st.session_state.xp += 20 * quantite
            
            # Mise à jour du portefeuille
            if symbole in st.session_state.portefeuille:
                anc_qte = st.session_state.portefeuille[symbole]["quantite"]
                st.session_state.portefeuille[symbole]["quantite"] += quantite
            else:
                st.session_state.portefeuille[symbole] = {"quantite": quantite, "prix_moyen": prix_actuel}
                
            st.balloons()
            st.success(f"💥 ACHAT SENSATIONNEL ! {quantite} action(s) {symbole} ajoutée(s). **+20 XP**")
            st.rerun()
        else:
            st.error("❌ Fonds insuffisants ! Tente ta chance au coffre mystère.")
            
except Exception as e:
    st.error("Erreur lors de la récupération des cours du marché.")

st.divider()

# --- MON PORTEFEUILLE D'ACTIFS ---
st.subheader("💼 Mon Empire Financier")
if st.session_state.portefeuille:
    for sym, details in st.session_state.portefeuille.items():
        st.write(f"- **{sym}** : `{details['quantite']}` action(s)")
else:
    st.write("Aucune action possédée pour l'instant.")
