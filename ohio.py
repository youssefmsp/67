import streamlit as st
import yfinance as yf
import random

# Configuration de la page
st.set_page_config(page_title="Trading Quest 📈", page_icon="⚡", layout="centered")

# --- TRADUCTIONS (FR / EN) ---
TEXTS = {
    "FR": {
        "title": "⚡ Trading Quest",
        "subtitle": "Débloque des niveaux, tente ta chance et bâtis ton empire !",
        "level": "Niveau",
        "xp": "XP",
        "ranks": {1: "🟢 Novice des Marchés", 2: "🔵 Trader Averti", 3: "🟣 Analyste Senior", 4: "👑 Loup de Wall Street"},
        "high_rank": "🔥 Demi-Dieu de la Finance",
        "cash": "Cash disponible",
        "portfolio_val": "Valeur actions",
        "total_net": "Patrimoine total",
        "chest_title": "🎁 Coffre Mystère Quotidien",
        "chest_btn": "📦 OUVRIRE LE COFFRE MYSTÈRE 🔮",
        "chest_success": "🎉 INCROYABLE ! Tu as gagné un bonus mystère de **+{gain} $** et **+30 XP** !",
        "chest_claimed": "✅ Coffre déjà réclamé ! Reviens plus tard pour un autre tirage.",
        "market_title": "🛒 Salle des Marchés",
        "select_company": "Choisis une entreprise star :",
        "quantity": "Quantité d'actions :",
        "buy_btn": "🚀 ACHETER POUR {cost:.2f} $",
        "buy_success": "💥 ACHAT SENSATIONNEL ! {qty} action(s) {sym} ajoutée(s). **+{xp} XP**",
        "no_funds": "❌ Fonds insuffisants ! Tente ta chance au coffre mystère.",
        "error_fetch": "Erreur lors de la récupération des cours du marché.",
        "my_portfolio": "💼 Mon Empire Financier",
        "no_stocks": "Aucune action possédée pour l'instant.",
        "shares": "action(s)"
    },
    "EN": {
        "title": "⚡ Trading Quest",
        "subtitle": "Unlock levels, try your luck and build your empire!",
        "level": "Level",
        "xp": "XP",
        "ranks": {1: "🟢 Market Novice", 2: "🔵 Savvy Trader", 3: "🟣 Senior Analyst", 4: "👑 Wall Street Wolf"},
        "high_rank": "🔥 Financial Demigod",
        "cash": "Available Cash",
        "portfolio_val": "Portfolio Value",
        "total_net": "Total Net Worth",
        "chest_title": "🎁 Daily Mystery Chest",
        "chest_btn": "📦 OPEN MYSTERY CHEST 🔮",
        "chest_success": "🎉 INCREDIBLE! You won a mystery bonus of **+${gain}** and **+30 XP**!",
        "chest_claimed": "✅ Chest already claimed! Come back later for another draw.",
        "market_title": "🛒 Trading Floor",
        "select_company": "Select a top stock:",
        "quantity": "Share quantity:",
        "buy_btn": "🚀 BUY FOR ${cost:.2f}",
        "buy_success": "💥 EPIC PURCHASE! {qty} share(s) of {sym} added. **+{xp} XP**",
        "no_funds": "❌ Insufficient funds! Try your luck with the mystery chest.",
        "error_fetch": "Error fetching market data.",
        "my_portfolio": "💼 My Financial Empire",
        "no_stocks": "No stocks owned yet.",
        "shares": "share(s)"
    }
}

# --- BARRE LIATÉRALE : SÉLECTEUR DE LANGUE ---
st.sidebar.title("🌐 Settings / Paramètres")
langue = st.sidebar.selectbox("Language / Langue", ["FR 🇫🇷", "EN 🇬🇧"])
lang_code = "FR" if "FR" in langue else "EN"
t = TEXTS[lang_code]

# --- INITIALISATION DE L'ÉTAT (SESSION STATE) ---
if "solde" not in st.session_state:
    st.session_state.solde = 1000.0
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "portefeuille" not in st.session_state:
    st.session_state.portefeuille = {}
if "bonus_reclame" not in st.session_state:
    st.session_state.bonus_reclame = False

# Calcul du niveau
niveau = (st.session_state.xp // 100) + 1
rang = t["ranks"].get(niveau, t["high_rank"])

# --- EN-TÊTE DU SITE ---
st.title(t["title"])
st.caption(t["subtitle"])

# Barre de niveau & XP
col_lvl, col_xp = st.columns([1, 2])
with col_lvl:
    st.subheader(f"{t['level']} {niveau}")
    st.caption(rang)
with col_xp:
    progression = (st.session_state.xp % 100) / 100
    st.progress(progression, text=f"{t['xp']} : {st.session_state.xp % 100} / 100")

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
c1.metric(t["cash"], f"{st.session_state.solde:.2f} $")
c2.metric(t["portfolio_val"], f"{valeur_actions:.2f} $")
c3.metric(t["total_net"], f"{total_patrimoine:.2f} $", delta=f"{(total_patrimoine - 1000.0):.2f} $")

st.divider()

# --- MODULE COFFRE MYSTÈRE VISUEL ---
st.subheader(t["chest_title"])

if not st.session_state.bonus_reclame:
    col_img, col_btn = st.columns([1, 2])
    with col_img:
        st.markdown("### 🧰✨")
    with col_btn:
        if st.button(t["chest_btn"], use_container_width=True, type="primary"):
            gain = random.choice([50, 100, 200, 500, 1000])
            st.session_state.solde += gain
            st.session_state.xp += 30
            st.session_state.bonus_reclame = True
            st.balloons()
            st.success(t["chest_success"].format(gain=gain))
            st.rerun()
else:
    st.info(t["chest_claimed"])

st.divider()

# --- ESPACE TRADING INTERACTIF ---
st.subheader(t["market_title"])

actions_populaires = {"Apple": "AAPL", "Tesla": "TSLA", "Nvidia": "NVDA", "Amazon": "AMZN", "Bitcoin (ETF)": "IBIT"}
choix = st.selectbox(t["select_company"], list(actions_populaires.keys()))
symbole = actions_populaires[choix]

try:
    ticker = yf.Ticker(symbole)
    df_hist = ticker.history(period="1mo")
    prix_actuel = df_hist["Close"].iloc[-1]
    
    col_sym, col_pr = st.columns(2)
    col_sym.write(f"### {symbole}")
    col_pr.subheader(f"{prix_actuel:.2f} $")

    st.line_chart(df_hist["Close"])

    quantite = st.number_input(t["quantity"], min_value=1, value=1, step=1)
    cout_total = prix_actuel * quantite

    if st.button(t["buy_btn"].format(cost=cout_total), use_container_width=True):
        if cout_total <= st.session_state.solde:
            st.session_state.solde -= cout_total
            gained_xp = 20 * quantite
            st.session_state.xp += gained_xp
            
            if symbole in st.session_state.portefeuille:
                st.session_state.portefeuille[symbole]["quantite"] += quantite
            else:
                st.session_state.portefeuille[symbole] = {"quantite": quantite, "prix_moyen": prix_actuel}
                
            st.balloons()
            st.success(t["buy_success"].format(qty=quantite, sym=symbole, xp=gained_xp))
            st.rerun()
        else:
            st.error(t["no_funds"])
            
except Exception:
    st.error(t["error_fetch"])

st.divider()

# --- MON PORTEFEUILLE D'ACTIFS ---
st.subheader(t["my_portfolio"])
if st.session_state.portefeuille:
    for sym, details in st.session_state.portefeuille.items():
        st.write(f"- **{sym}** : `{details['quantite']}` {t['shares']}")
else:
    st.write(t["no_stocks"])
