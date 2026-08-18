import streamlit as st
import yfinance as yf
import pandas as pd
import random
import sqlite3
import json

# Configuration de la page
st.set_page_config(page_title="Trading Quest 📈", page_icon="⚡", layout="wide")

# --- BASE DE DONNÉES SQLITE (GESTION AUTO DE LA MÉMOIRE) ---
DB_NAME = "trading_quest.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            solde REAL,
            xp INTEGER,
            portefeuille TEXT,
            bonus_reclame INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def load_user_data(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT solde, xp, portefeuille, bonus_reclame FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "solde": row[0],
            "xp": row[1],
            "portefeuille": json.loads(row[2]),
            "bonus_reclame": bool(row[3])
        }
    return None

def save_user_data(username, solde, xp, portefeuille, bonus_reclame):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (username, solde, xp, portefeuille, bonus_reclame)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, solde, xp, json.dumps(portefeuille), int(bonus_reclame)))
    conn.commit()
    conn.close()

init_db()

# --- TRADUCTIONS (FR / EN) ---
TEXTS = {
    "FR": {
        "title": "⚡ Trading Quest",
        "subtitle": "Bâtis ton empire financier en temps réel !",
        "level": "Niveau",
        "xp": "XP",
        "ranks": {1: "🟢 Novice des Marchés", 2: "🔵 Trader Averti", 3: "🟣 Analyste Senior", 4: "👑 Loup de Wall Street"},
        "high_rank": "🔥 Demi-Dieu de la Finance",
        "cash": "Cash disponible",
        "portfolio_val": "Valeur actions",
        "total_net": "Patrimoine total",
        "chest_title": "🎁 Coffre Mystère Quotidien",
        "chest_btn": "📦 OUVRIR LE COFFRE MYSTÈRE 🔮",
        "chest_success": "🎉 INCROYABLE ! Tu as gagné un bonus mystère de **+{gain} $** et **+30 XP** !",
        "chest_claimed": "✅ Coffre déjà réclamé !",
        "tabs": ["🛒 Marché & Actions", "📊 Comparatif Grandes Marques", "📅 Résumé de la Semaine", "🏆 Mon Tableau de Bord"],
        "select_company": "Rechercher / Choisir une entreprise :",
        "quantity": "Quantité d'actions :",
        "buy_btn": "🚀 ACHETER POUR {cost:.2f} $",
        "buy_success": "💥 ACHAT RÉUSSI ! {qty} action(s) {sym} ajoutée(s). **+{xp} XP**",
        "no_funds": "❌ Fonds insuffisants ! Tente ta chance au coffre mystère.",
        "error_fetch": "Erreur lors de la récupération des données de cette action.",
        "my_portfolio": "💼 Mon Empire Financier",
        "no_stocks": "Aucune action possédée pour l'instant.",
        "shares": "action(s)",
        "summary_title": "📋 Résumé de l'Action",
        "prev_close": "Clôture précédente",
        "day_high": "Plus haut du jour",
        "day_low": "Plus bas du jour",
        "volume": "Volume d'échange",
        "leaderboard_title": "🏆 Bilan de ton Compte",
        "weekly_summary": "📅 Performance sur 7 jours",
        "comparison_title": "🏛️ Comparatif des Géants de la Bourse",
        "login_section": "👤 Connexion / Profil",
        "username_prompt": "Entre ton Pseudo :",
        "login_btn": "💾 Charger / Créer mon Profil",
        "reset_btn": "⚠️ Réinitialiser ma progression",
        "welcome": "Bienvenue",
        "auto_save_info": "🔒 Vos données sont sauvegardées automatiquement."
    },
    "EN": {
        "title": "⚡ Trading Quest",
        "subtitle": "Build your financial empire in real time!",
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
        "chest_claimed": "✅ Chest already claimed!",
        "tabs": ["🛒 Market & Stocks", "📊 Top Brands Comparison", "📅 Weekly Summary", "🏆 My Dashboard"],
        "select_company": "Search / Select a company:",
        "quantity": "Share quantity:",
        "buy_btn": "🚀 BUY FOR ${cost:.2f}",
        "buy_success": "💥 PURCHASE SUCCESSFUL! {qty} share(s) of {sym} added. **+{xp} XP**",
        "no_funds": "❌ Insufficient funds! Try your luck with the mystery chest.",
        "error_fetch": "Error fetching data for this stock.",
        "my_portfolio": "💼 My Financial Empire",
        "no_stocks": "No stocks owned yet.",
        "shares": "share(s)",
        "summary_title": "📋 Stock Summary",
        "prev_close": "Previous Close",
        "day_high": "Day High",
        "day_low": "Day Low",
        "volume": "Volume",
        "leaderboard_title": "🏆 Account Overview",
        "weekly_summary": "📅 7-Day Performance",
        "comparison_title": "🏛️ Giants Comparison Table",
        "login_section": "👤 Profile & Login",
        "username_prompt": "Enter your Username:",
        "login_btn": "💾 Load / Create Profile",
        "reset_btn": "⚠️ Reset my progress",
        "welcome": "Welcome",
        "auto_save_info": "🔒 Your progress is automatically saved."
    }
}

# --- INITIALISATION DE LA SESSION ---
if "user_loaded" not in st.session_state:
    st.session_state.user_loaded = False

# --- BARRE LATÉRALE (MENU ☰) ---
st.sidebar.title("☰ Menu")

# Choix de la langue
langue = st.sidebar.selectbox("🌐 Language / Langue", ["FR 🇫🇷", "EN 🇬🇧"])
lang_code = "FR" if "FR" in langue else "EN"
t = TEXTS[lang_code]

st.sidebar.divider()

# Gestion du Compte / Connexion
st.sidebar.subheader(t["login_section"])
input_username = st.sidebar.text_input(t["username_prompt"], value=st.session_state.get("username", "Youssef"))

if st.sidebar.button(t["login_btn"], use_container_width=True):
    if input_username.strip():
        data = load_user_data(input_username.strip())
        st.session_state.username = input_username.strip()
        if data:
            st.session_state.solde = data["solde"]
            st.session_state.xp = data["xp"]
            st.session_state.portefeuille = data["portefeuille"]
            st.session_state.bonus_reclame = data["bonus_reclame"]
        else:
            st.session_state.solde = 1000.0
            st.session_state.xp = 0
            st.session_state.portefeuille = {}
            st.session_state.bonus_reclame = False
            save_user_data(st.session_state.username, 1000.0, 0, {}, False)
        st.session_state.user_loaded = True
        st.rerun()

# Si première ouverture sans validation
if not st.session_state.user_loaded:
    st.session_state.username = input_username.strip() if input_username.strip() else "Youssef"
    data = load_user_data(st.session_state.username)
    if data:
        st.session_state.solde = data["solde"]
        st.session_state.xp = data["xp"]
        st.session_state.portefeuille = data["portefeuille"]
        st.session_state.bonus_reclame = data["bonus_reclame"]
    else:
        st.session_state.solde = 1000.0
        st.session_state.xp = 0
        st.session_state.portefeuille = {}
        st.session_state.bonus_reclame = False
    st.session_state.user_loaded = True

st.sidebar.caption(t["auto_save_info"])

# Option de réinitialisation
if st.sidebar.button(t["reset_btn"], use_container_width=True):
    st.session_state.solde = 1000.0
    st.session_state.xp = 0
    st.session_state.portefeuille = {}
    st.session_state.bonus_reclame = False
    save_user_data(st.session_state.username, 1000.0, 0, {}, False)
    st.rerun()

# Helper pour sauvegarder automatiquement après chaque modif
def sync_data():
    save_user_data(
        st.session_state.username,
        st.session_state.solde,
        st.session_state.xp,
        st.session_state.portefeuille,
        st.session_state.bonus_reclame
    )

# Calcul du niveau
niveau = (st.session_state.xp // 100) + 1
rang = t["ranks"].get(niveau, t["high_rank"])

MARQUES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Google (Alphabet)": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta (Facebook)": "META",
    "Bitcoin ETF": "IBIT"
}

# --- PAGE PRINCIPALE ---
st.title(t["title"])
st.caption(f"{t['subtitle']} | **{t['welcome']} :** `{st.session_state.username}`")

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
benefice_total = total_patrimoine - 1000.0

c1, c2, c3 = st.columns(3)
c1.metric(t["cash"], f"{st.session_state.solde:.2f} $")
c2.metric(t["portfolio_val"], f"{valeur_actions:.2f} $")
c3.metric(t["total_net"], f"{total_patrimoine:.2f} $", delta=f"{benefice_total:.2f} $")

st.divider()

# --- MODULE COFFRE MYSTÈRE VISUEL ---
st.subheader(t["chest_title"])
if not st.session_state.bonus_reclame:
    col_img, col_btn = st.columns([1, 3])
    with col_img:
        st.markdown("### 🧰✨")
    with col_btn:
        if st.button(t["chest_btn"], use_container_width=True, type="primary"):
            gain = random.choice([50, 100, 200, 500, 1000])
            st.session_state.solde += gain
            st.session_state.xp += 30
            st.session_state.bonus_reclame = True
            sync_data()
            st.balloons()
            st.success(t["chest_success"].format(gain=gain))
            st.rerun()
else:
    st.info(t["chest_claimed"])

st.divider()

# --- ONGLETS PRINCIPAUX ---
tab1, tab2, tab3, tab4 = st.tabs(t["tabs"])

# --- ONGLET 1 : MARCHÉ & SÉLECTION D'ACTION ---
with tab1:
    st.subheader(t["select_company"])
    choix = st.selectbox("", list(MARQUES.keys()), label_visibility="collapsed")
    symbole = MARQUES[choix]

    try:
        ticker = yf.Ticker(symbole)
        df_hist = ticker.history(period="1mo")
        info = ticker.fast_info
        prix_actuel = df_hist["Close"].iloc[-1]

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown(f"### {choix} (`{symbole}`)")
            st.write(f"**Prix en direct :** `{prix_actuel:.2f} $`")
            st.line_chart(df_hist["Close"])

            quantite = st.number_input(t["quantity"], min_value=1, value=1, step=1)
            cout_total = prix_actuel * quantite

            if st.button(t["buy_btn"].format(cost=cout_total), use_container_width=True, type="primary"):
                if cout_total <= st.session_state.solde:
                    st.session_state.solde -= cout_total
                    gained_xp = 20 * quantite
                    st.session_state.xp += gained_xp

                    if symbole in st.session_state.portefeuille:
                        st.session_state.portefeuille[symbole]["quantite"] += quantite
                    else:
                        st.session_state.portefeuille[symbole] = {"quantite": quantite, "prix_moyen": prix_actuel}

                    sync_data()
                    st.balloons()
                    st.success(t["buy_success"].format(qty=quantite, sym=symbole, xp=gained_xp))
                    st.rerun()
                else:
                    st.error(t["no_funds"])

        with col_right:
            st.markdown(f"#### {t['summary_title']}")
            st.metric(t["prev_close"], f"{info.get('previousClose', prix_actuel):.2f} $")
            st.metric(t["day_high"], f"{info.get('dayHigh', prix_actuel):.2f} $")
            st.metric(t["day_low"], f"{info.get('dayLow', prix_actuel):.2f} $")
            st.metric(t["volume"], f"{info.get('lastVolume', 0):,}")

    except Exception:
        st.error(t["error_fetch"])

# --- ONGLET 2 : COMPARATIF DE GRANDES MARQUES ---
with tab2:
    st.subheader(t["comparison_title"])
    
    comparaison_data = []
    for nom, sym in MARQUES.items():
        try:
            t_obj = yf.Ticker(sym)
            p = t_obj.history(period="1d")["Close"].iloc[-1]
            prev = t_obj.fast_info.get("previousClose", p)
            var = ((p - prev) / prev) * 100
            comparaison_data.append({"Marque": nom, "Symbole": sym, "Prix ($)": round(p, 2), "Variation (%)": f"{var:+.2f}%"})
        except:
            comparaison_data.append({"Marque": nom, "Symbole": sym, "Prix ($)": "N/A", "Variation (%)": "N/A"})

    df_comp = pd.DataFrame(comparaison_data)
    st.dataframe(df_comp, use_container_width=True)

# --- ONGLET 3 : RÉSUMÉ DE LA SEMAINE ---
with tab3:
    st.subheader(t["weekly_summary"])
    
    weekly_data = {}
    for nom, sym in list(MARQUES.items())[:5]:
        try:
            df_w = yf.Ticker(sym).history(period="7d")["Close"]
            weekly_data[nom] = df_w
        except:
            pass

    if weekly_data:
        df_weekly = pd.DataFrame(weekly_data)
        st.line_chart(df_weekly)
        st.dataframe(df_weekly.style.highlight_max(axis=0), use_container_width=True)

# --- ONGLET 4 : TABLEAU DE BORD & STATISTIQUES RÉELLES ---
with tab4:
    st.subheader(t["leaderboard_title"])

    stats_joueur = [
        {"Indicateur": "Pseudo", "Valeur": st.session_state.username},
        {"Indicateur": "Niveau Actuel", "Valeur": f"Niveau {niveau} ({rang})"},
        {"Indicateur": "XP Cumulé", "Valeur": f"{st.session_state.xp} XP"},
        {"Indicateur": "Cash Disponible", "Valeur": f"{st.session_state.solde:.2f} $"},
        {"Indicateur": "Valeur Portefeuille", "Valeur": f"{valeur_actions:.2f} $"},
        {"Indicateur": "Patrimoine Total", "Valeur": f"{total_patrimoine:.2f} $"},
        {"Indicateur": "Bénéfice/Perte Nette", "Valeur": f"{benefice_total:+.2f} $"}
    ]

    df_stats = pd.DataFrame(stats_joueur)
    st.table(df_stats)

st.divider()

# --- MON PORTEFEUILLE D'ACTIFS ---
st.subheader(t["my_portfolio"])
if st.session_state.portefeuille:
    for sym, details in st.session_state.portefeuille.items():
        st.write(f"- **{sym}** : `{details['quantite']}` {t['shares']}")
else:
    st.write(t["no_stocks"])
